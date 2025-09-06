from abc import ABC, abstractmethod
from typing import Optional


class BaseClient(ABC):
    model: str
    base_url: str

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key
        if model:
            self.model = model
        if base_url:
            self.base_url = base_url

    @abstractmethod
    def ask(self, prompt: str) -> str:
        return NotImplemented("You need to implement the ask method!")
