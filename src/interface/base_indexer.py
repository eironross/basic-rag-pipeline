from abc import ABC, abstractmethod
from typing import List

from schema.schema import DataItem

class BaseIndexer(ABC):

    @abstractmethod
    def index(self, document_paths: List[str]) -> List[DataItem]:
        pass 