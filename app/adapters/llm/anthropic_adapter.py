"""
Anthropic Adapter — implementiert LLMPort für die Anthropic API.
Um einen neuen Anbieter hinzuzufügen: diese Datei als Vorlage nehmen,
LLMPort implementieren, in config.py registrieren. Fertig.
"""

import os
import anthropic
from app.core.ports import LLMPort, LLMResponse

DEFAULT_MODEL = "claude-sonnet-4-20250514"

AVAILABLE_MODELS = [
    "claude-sonnet-4-20250514",
    "claude-opus-4-20250514",
    "claude-haiku-4-5-20251001",
]


class AnthropicAdapter(LLMPort):
    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self._model = model

    @property
    def name(self) -> str:
        return "Anthropic"

    @property
    def available_models(self) -> list[str]:
        return AVAILABLE_MODELS

    def is_available(self) -> bool:
        return bool(self._api_key)

    def set_model(self, model: str):
        if model in AVAILABLE_MODELS:
            self._model = model

    def generate(self, system_prompt: str, user_message: str) -> LLMResponse:
        if not self._api_key:
            raise ValueError("Anthropic API Key nicht gesetzt. Bitte in der Konfiguration eintragen.")

        client = anthropic.Anthropic(api_key=self._api_key)
        message = client.messages.create(
            model=self._model,
            max_tokens=1200,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        return LLMResponse(
            content=message.content[0].text,
            model=self._model,
            provider="anthropic",
        )
