from langchain_ollama import ChatOllama

from core.client.base import BaseClient


class OllamaClient(BaseClient):
    def ask(self, prompt: str) -> str:
        llm = ChatOllama(
            model=self.model,
            base_url=self.base_url,
        )
        resp = llm.invoke(prompt)
        return resp.content
