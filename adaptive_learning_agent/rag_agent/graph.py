from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from functools import partial

from .graph_state import State, AgentState
from .nodes import *
from .edges import *
# from adaptive_learning_agent.utils import visualize_graph

def create_agent_graph(llm, tools_list, llm_quiz):
    llm_with_tools = llm.bind_tools(tools_list)
    tool_node = ToolNode(tools_list)

    checkpointer = InMemorySaver()

    print("Compiling agent graph...")
    agent_builder = StateGraph(AgentState)
    agent_builder.add_node("agent", partial(agent_node, llm_with_tools=llm_with_tools))
    agent_builder.add_node("tools", tool_node)
    agent_builder.add_node("extract_answer", extract_final_answer)
    
    agent_builder.add_edge(START, "agent")    
    agent_builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: "extract_answer"})
    agent_builder.add_edge("tools", "agent")    
    agent_builder.add_edge("extract_answer", END)
    
    agent_subgraph = agent_builder.compile()
    
    graph_builder = StateGraph(State)
    graph_builder.add_node("summarize", partial(analyze_chat_and_summarize, llm=llm))
    graph_builder.add_node("analyze_rewrite", partial(analyze_and_rewrite_query, llm=llm))
    graph_builder.add_node("human_input", human_input_node)
    graph_builder.add_node("process_question", agent_subgraph)
    graph_builder.add_node("aggregate", partial(aggregate_responses, llm=llm))
    graph_builder.add_node("generate_quiz", partial(generate_revision_quiz, llm=llm))
    
    graph_builder.add_edge(START, "summarize")
    graph_builder.add_edge("summarize", "analyze_rewrite")
    graph_builder.add_conditional_edges("analyze_rewrite", route_after_rewrite)
    graph_builder.add_edge("human_input", "analyze_rewrite")
    graph_builder.add_edge(["process_question"], "aggregate")
    graph_builder.add_edge("aggregate", "generate_quiz")
    graph_builder.add_edge("generate_quiz", END)

    agent_graph = graph_builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_input"]
    )

    print("✓ Agent graph compiled successfully.")
    return agent_graph

def visualize_graph(workflow, output_path: str = "graph.png"):
    """
    Generate visualization of the workflow graph

    Args:
        workflow: Compiled LangGraph workflow
        output_path: Path to save the graph image
    """
    try:
        from langchain_core.runnables.graph import MermaidDrawMethod

        graph = workflow.get_graph(xray=True)
        png_bytes = graph.draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER)

        with open(output_path, "wb") as f:
            f.write(png_bytes)

        print(f"\n📊 Graph visualization saved to: {output_path}")
    except Exception as e:
        print(f"\n⚠️  Could not generate graph visualization: {e}")

if __name__ == "__main__":
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    workflow = create_agent_graph(llm=llm, tools_list=[], llm_quiz=llm)
    visualize_graph(workflow, output_path="agent_graph.png")