from abc import ABC, abstractmethod
from typing import Optional

from schema.schema import EvaluationResult

class BaseEvaluator(ABC):

    @abstractmethod
    def evaluate(
        self, query: str, response: str, expected_answer: str
    ) -> EvaluationResult:
        pass