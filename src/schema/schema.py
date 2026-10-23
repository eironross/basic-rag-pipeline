from pydantic import BaseModel
from typing import Optional

class DataItem(BaseModel):
    content: str = ""
    source: str = ""

class EvaluationResult(BaseModel):
    question: str
    response: str
    expected_answer: str
    is_correct: bool
    reasoning: Optional[str] = None