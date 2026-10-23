from abc import ABC, abstractmethod
from typing import List

class BaseReponseGenerator(ABC):

    @abstractmethod
    def generator_response(self, query: str, context: List[str]) -> str:
        pass