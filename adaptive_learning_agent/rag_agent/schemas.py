from typing import List
from pydantic import BaseModel, Field

class QueryAnalysis(BaseModel):
    is_clear: bool = Field(
        description="Indicates if the user's question is clear and answerable."
    )
    questions: List[str] = Field(
        description="List of rewritten, self-contained questions."
    )
    clarification_needed: str = Field(
        description="Explanation if the question is unclear."
    )

class QuizQuestion(BaseModel):
    """Structure for a revision question"""
    question_text: str = Field(description="The question to test user understanding.")
    options: List[str] = Field(description="List of 4 possible answers.", min_items=4, max_items=4)
    correct_option_index: int = Field(description="Index (0-3) of the correct answer.")
    explanation: str = Field(description="Brief explanation of why the answer is correct.")