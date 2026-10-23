from abc import ABC, abstractmethod
from typing import Optional

from schema.schema import EvaluationResult

class BaseEvaluation(ABC):

    @abstractmethod
    def evaluate(
        self, query: str, reponse: str, expected_answer: str
    ) -> EvaluationResult:
        pass