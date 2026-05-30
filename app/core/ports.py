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


@dataclass
class ImageBackendStatus:
    id: str
    name: str
    host: str
    available: bool
    models: list[str]
    capabilities: list[str]
    error: str = ""


@dataclass
class ImageGenerationRequest:
    positive_prompt: str
    negative_prompt: str
    model: str = ""
    width: int = 1024
    height: int = 1024
    steps: int = 25
    cfg_scale: float = 7.0
    seed: int = -1


@dataclass
class ImageGenerationResult:
    image_bytes: bytes
    extension: str
    metadata: dict


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
    def save_character(self, character: dict, user_id: str) -> str:
        """Speichert einen Character für einen spezifischen Nutzer."""
        pass

    @abstractmethod
    def load_character(self, character_id: str, user_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    def list_characters(self, user_id: str) -> list[dict]:
        pass

    @abstractmethod
    def delete_character(self, character_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    def save_prompt_history(self, entry: dict, user_id: str) -> str:
        """Speichert einen Prompt-Verlauf-Eintrag für einen spezifischen Nutzer."""
        pass

    @abstractmethod
    def list_prompt_history(self, user_id: str, character_id: Optional[str] = None) -> list[dict]:
        pass

    @abstractmethod
    def load_prompt_history(self, entry_id: str, user_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    def delete_prompt_history(self, entry_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    def update_prompt_history(self, entry_id: str, user_id: str, updates: dict) -> bool:
        """Aktualisiert einzelne Felder eines bestehenden History-Eintrags."""
        pass


class ImageBackendPort(ABC):
    """Bildgenerator-Backends wie Automatic1111 oder ComfyUI."""

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def host(self) -> str:
        pass

    @abstractmethod
    def set_host(self, host: str):
        pass

    @abstractmethod
    def status(self) -> ImageBackendStatus:
        pass

    @abstractmethod
    def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        pass
