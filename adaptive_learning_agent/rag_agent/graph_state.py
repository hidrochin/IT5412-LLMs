from typing import List, Annotated, Optional, Dict, Any
from langgraph.graph import MessagesState

def accumulate_or_reset(existing: List[dict], new: List[dict]) -> List[dict]:
    if new and any(item.get('__reset__') for item in new):
        return []
    return existing + new

class State(MessagesState):
    """State for main agent graph"""
    questionIsClear: bool = False
    conversation_summary: str = ""
    originalQuery: str = "" 
    rewrittenQuestions: List[str] = []
    agent_answers: Annotated[List[dict], accumulate_or_reset] = []
    quiz_data: Optional[Dict[str, Any]] = None
    mode: str = "standard" # "standard" = just answer, "adaptive" = answer + quiz

class AgentState(MessagesState):
    """State for individual agent subgraph"""
    question: str = ""
    question_index: int = 0
    final_answer: str = ""
    agent_answers: List[dict] = []