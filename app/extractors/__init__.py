from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, pdf_path: str) -> list[dict]:
        pass
