"""
Ports — die Außengrenzen der Hexagonalen Architektur.
Jeder Adapter (Anthropic, Ollama, Storage...) implementiert genau ein Port.
Der Core kennt nur diese Interfaces, nie konkrete Implementierungen.
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str


class LLMPort(ABC):
    """Jeder LLM-Anbieter implementiert dieses Interface."""

    @abstractmethod
    def generate(self, system_prompt: str, user_message: str) -> LLMResponse:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Prüft ob der Anbieter erreichbar ist (API-Key vorhanden, Server läuft etc.)"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def available_models(self) -> list[str]:
        pass


class StoragePort(ABC):
    """Alles was gespeichert/geladen werden muss, geht durch dieses Interface."""

    @abstractmethod
    def save_character(self, character: dict) -> str:
        """Speichert einen Character, gibt die ID zurück."""
        pass

    @abstractmethod
    def load_character(self, character_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    def list_characters(self) -> list[dict]:
        pass

    @abstractmethod
    def delete_character(self, character_id: str) -> bool:
        pass

    @abstractmethod
    def save_prompt_history(self, entry: dict) -> str:
        """Speichert einen Prompt-Verlauf-Eintrag, gibt die ID zurück."""
        pass

    @abstractmethod
    def list_prompt_history(self, character_id: Optional[str] = None) -> list[dict]:
        pass

    @abstractmethod
    def delete_prompt_history(self, entry_id: str) -> bool:
        pass

    @abstractmethod
    def update_prompt_history(self, entry_id: str, updates: dict) -> bool:
        """Aktualisiert einzelne Felder eines bestehenden History-Eintrags."""
        pass
