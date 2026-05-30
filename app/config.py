"""
Config — zentrale Konfiguration und Dependency Injection.
Hier werden Adapter instanziiert und dem Core übergeben.
Neuen Anbieter hinzufügen: Adapter importieren, in PROVIDERS eintragen. Fertig.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from app.adapters.llm.anthropic_adapter import AnthropicAdapter
from app.adapters.llm.ollama_adapter import OllamaAdapter
from app.adapters.image.automatic1111_adapter import Automatic1111Adapter
from app.adapters.image.comfyui_adapter import ComfyUIAdapter
from app.adapters.storage.json_storage import JsonStorageAdapter
from app.core.prompt_generator import PromptGenerator

# --- Storage (einmalig) ---
DATA_DIR = os.getenv("DATA_DIR", "data")
storage = JsonStorageAdapter(data_dir=DATA_DIR)

# --- LLM Adapter ---
anthropic_adapter = AnthropicAdapter(
    api_key=os.getenv("ANTHROPIC_API_KEY", ""),
    model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
)

ollama_local_adapter = OllamaAdapter(
    host=os.getenv("OLLAMA_LOCAL_HOST", "http://localhost:11434"),
    model=os.getenv("OLLAMA_LOCAL_MODEL", "llama3.1"),
    api_key=os.getenv("OLLAMA_LOCAL_API_KEY", os.getenv("OLLAMA_API_KEY", "")),
    label="Ollama (lokal)",
    filter_mode="local",
    timeout=int(os.getenv("OLLAMA_LOCAL_TIMEOUT", "300")),
)

ollama_cloud_adapter = OllamaAdapter(
    host=os.getenv("OLLAMA_CLOUD_HOST", "http://srv01:11434"),
    model=os.getenv("OLLAMA_CLOUD_MODEL", "kimi-k2.6:cloud"),
    api_key=os.getenv("OLLAMA_CLOUD_API_KEY", ""),
    label="Ollama (Cloud)",
    filter_mode="cloud",
    timeout=int(os.getenv("OLLAMA_CLOUD_TIMEOUT", "120")),
)

# --- Provider-Registry ---
# Neuen Anbieter: hier eintragen. Der Rest der App passt sich automatisch an.
PROVIDERS: dict[str, object] = {
    "anthropic": anthropic_adapter,
    "ollama_local": ollama_local_adapter,
    "ollama_cloud": ollama_cloud_adapter,
}

DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "anthropic")

# --- Image Backend Adapter ---
automatic1111_adapter = Automatic1111Adapter(
    host=os.getenv("AUTOMATIC1111_HOST", "http://localhost:7860"),
    timeout=int(os.getenv("IMAGE_BACKEND_TIMEOUT", "5")),
)

comfyui_adapter = ComfyUIAdapter(
    host=os.getenv("COMFYUI_HOST", "http://localhost:8188"),
    timeout=int(os.getenv("IMAGE_BACKEND_TIMEOUT", "5")),
)

IMAGE_BACKENDS = {
    "automatic1111": automatic1111_adapter,
    "comfyui": comfyui_adapter,
}


def get_provider(name: str):
    return PROVIDERS.get(name, anthropic_adapter)


def get_generator(provider_name: str | None = None) -> PromptGenerator:
    provider = get_provider(provider_name or DEFAULT_PROVIDER)
    return PromptGenerator(llm=provider, storage=storage)


def get_providers_status() -> list[dict]:
    return [
        {
            "id": pid,
            "name": adapter.name,
            "available": adapter.is_available(),
            "models": adapter.available_models,
        }
        for pid, adapter in PROVIDERS.items()
    ]


def get_image_backend(backend_id: str):
    return IMAGE_BACKENDS.get(backend_id)


def get_image_backends_status() -> list[dict]:
    return [backend.status().__dict__ for backend in IMAGE_BACKENDS.values()]


# --- Addons (Optional) ---
from app.addons import register_addon

# Versuch, den Model Hub zu laden
try:
    from app.addons.model_hub.provider import ModelHubProvider
    register_addon(ModelHubProvider())
except ImportError:
    pass
