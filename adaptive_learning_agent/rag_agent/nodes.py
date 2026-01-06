from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage, AIMessage
from .graph_state import State, AgentState
from .schemas import QueryAnalysis, QuizQuestion
from .prompts import *

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted

# This will try 3 times, waiting 4s, 8s, 16s... if Gemini says "Resource Exhausted"
retry_decorator = retry(
    retry=retry_if_exception_type(ResourceExhausted) | retry_if_exception_type(Exception), # Catch generic exceptions if API wrapper hides the specific 429
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    reraise=True
)

def analyze_chat_and_summarize(state: State, llm):
    print("🔄 [1/5] Summarizing conversation history...")
    if len(state["messages"]) < 4:
        return {"conversation_summary": ""}
    
    relevant_msgs = [
        msg for msg in state["messages"][:-1]
        if isinstance(msg, (HumanMessage, AIMessage))
        and not getattr(msg, "tool_calls", None)
    ]

    if not relevant_msgs:
        return {"conversation_summary": ""}
    
    conversation = "Conversation history:\n"
    for msg in relevant_msgs[-6:]:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        conversation += f"{role}: {msg.content}\n"

    summary_response = llm.with_config(temperature=0.2).invoke([SystemMessage(content=get_conversation_summary_prompt())] + [HumanMessage(content=conversation)])
    return {"conversation_summary": summary_response.content, "agent_answers": [{"__reset__": True}]}

def analyze_and_rewrite_query(state: State, llm):
    print("🤔 [2/5] Analyzing and rewriting query...")
    last_message = state["messages"][-1]
    conversation_summary = state.get("conversation_summary", "")

    context_section = (f"Conversation Context:\n{conversation_summary}\n" if conversation_summary.strip() else "") + f"User Query:\n{last_message.content}\n"

    llm_with_structure = llm.with_config(temperature=0.1).with_structured_output(QueryAnalysis)
    response = llm_with_structure.invoke([SystemMessage(content=get_query_analysis_prompt())] + [HumanMessage(content=context_section)])

    if len(response.questions) > 0 and response.is_clear:
        delete_all = [
            RemoveMessage(id=m.id)
            for m in state["messages"]
            if not isinstance(m, SystemMessage)
        ]
        return {
            "questionIsClear": True,
            "messages": delete_all,
            "originalQuery": last_message.content,
            "rewrittenQuestions": response.questions
        }
    else:
        clarification = response.clarification_needed if (response.clarification_needed and len(response.clarification_needed.strip()) > 10) else "I need more information to understand your question."
        return {
            "questionIsClear": False,
            "messages": [AIMessage(content=clarification)]
        }

def human_input_node(state: State):
    return {}

def agent_node(state: AgentState, llm_with_tools):
    print("🕵️ [3/5] Agent is thinking (Deciding on tools)...")
    sys_msg = SystemMessage(content=get_rag_agent_prompt())    
    if not state.get("messages"):
        human_msg = HumanMessage(content=state["question"])
        response = llm_with_tools.invoke([sys_msg] + [human_msg])
        return {"messages": [human_msg, response]}
    
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

def extract_final_answer(state: AgentState):
    for msg in reversed(state["messages"]):
        if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
            res = {
                "final_answer": msg.content,
                "agent_answers": [{
                    "index": state["question_index"],
                    "question": state["question"],
                    "answer": msg.content
                }]
            }
            return res
    return {
        "final_answer": "Unable to generate an answer.",
        "agent_answers": [{
            "index": state["question_index"],
            "question": state["question"],
            "answer": "Unable to generate an answer."
        }]
    }

def aggregate_responses(state: State, llm):
    print("✍️ [4/5] Synthesizing final answer from documents...")
    if not state.get("agent_answers"):
        return {"messages": [AIMessage(content="No answers were generated.")]}

    sorted_answers = sorted(state["agent_answers"], key=lambda x: x["index"])

    formatted_answers = ""
    for i, ans in enumerate(sorted_answers, start=1):
        formatted_answers += (f"\nAnswer {i}:\n"f"{ans['answer']}\n")

    user_message = HumanMessage(content=f"""Original user question: {state["originalQuery"]}\nRetrieved answers:{formatted_answers}""")
    synthesis_response = llm.invoke([SystemMessage(content=get_aggregation_prompt())] + [user_message])
    
    return {"messages": [AIMessage(content=synthesis_response.content)]}

@retry_decorator
def generate_revision_quiz(state: State, llm):
    """
    Generates a multiple choice question based on the agent's last answer.
    """
    print("🎓 [5/5] Generating quiz question...")
    last_message = state["messages"][-1]
    
    # Validation: Don't quiz if the answer was "I don't know" or empty
    if not last_message.content or "unable to generate" in last_message.content.lower():
        return {"quiz_data": None}

    print("--- GENERATING REVISION QUIZ ---")
    
    # Force structured output
    structured_llm = llm.with_structured_output(QuizQuestion)
    system_prompt = get_quiz_prompt()
    try:
        response = structured_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Create a quiz based on this explanation:\n\n{last_message.content}")
        ])
        return {"quiz_data": response.dict()}
    except Exception as e:
        print(f"Quiz generation failed: {e}")
        raise e