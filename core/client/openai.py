import os

from openai import OpenAI

from core.client.base import BaseClient


class OpenAIClient(BaseClient):
    def ask(self, prompt: str) -> str:
        # Find the API key based on the base URL
        if "openrouter" in self.base_url:
            self.api_key = os.getenv("OPENROUTER_API_KEY")
        elif "openai" in self.base_url:
            self.api_key = os.getenv("OPENAI_API_KEY")

        client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
        completion = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        )
        return completion.choices[0].message.content
