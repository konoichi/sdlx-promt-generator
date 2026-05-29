"""
Ollama Adapter — implementiert LLMPort für lokale Ollama-Modelle.
Ollama muss lokal laufen: https://ollama.ai
Modelle installieren z.B.: ollama pull llama3.1
"""

import requests
import json
from app.core.ports import LLMPort, LLMResponse

DEFAULT_HOST = "http://localhost:11434"
DEFAULT_MODEL = "llama3.1"


class OllamaAdapter(LLMPort):
    def __init__(self, host: str = DEFAULT_HOST, model: str = DEFAULT_MODEL,
                 api_key: str = "", label: str = "Ollama",
                 filter_mode: str = "all", timeout: int = 300):
        self._host = host.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._label = label
        self._filter_mode = filter_mode  # "all" | "local" | "cloud"
        self._timeout = timeout
        self._available_models_cache: list[str] | None = None

    @property
    def name(self) -> str:
        return self._label

    @property
    def model_id(self) -> str:
        return self._model

    @property
    def provider_id(self) -> str:
        return "ollama"

    @staticmethod
    def _is_cloud_model(name: str) -> bool:
        return name.endswith(":cloud") or name.endswith("-cloud")

    def _is_cloud(self) -> bool:
        return self._is_cloud_model(self._model)

    def _build_payload(self, system_prompt: str, user_message: str,
                       stream: bool) -> dict:
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": stream,
        }
        if not self._is_cloud():
            payload["options"] = {"temperature": 0.3, "num_predict": 2048}
            # Constrained JSON decoding — forces local models to output valid JSON
            # even if they ignore the "Reply ONLY with JSON" instruction in the prompt
            payload["format"] = "json"
        return payload

    @property
    def available_models(self) -> list[str]:
        try:
            res = requests.get(f"{self._host}/api/tags", timeout=3, headers=self._headers())
            if res.status_code == 200:
                all_models = [m["name"] for m in res.json().get("models", [])]
                if self._filter_mode == "cloud":
                    return [m for m in all_models if self._is_cloud_model(m)]
                if self._filter_mode == "local":
                    return [m for m in all_models if not self._is_cloud_model(m)]
                return all_models
        except Exception:
            pass
        return [self._model]

    def is_available(self) -> bool:
        try:
            res = requests.get(f"{self._host}/api/tags", timeout=3, headers=self._headers())
            return res.status_code == 200
        except Exception:
            return False

    def set_model(self, model: str):
        self._model = model

    def set_host(self, host: str):
        self._host = host.rstrip("/")

    def _headers(self) -> dict:
        if self._api_key:
            return {"Authorization": f"Bearer {self._api_key}"}
        return {}

    def _raise_on_timeout(self, exc: Exception) -> None:
        raise requests.exceptions.ReadTimeout(
            f"Modell '{self._model}' hat nicht innerhalb von {self._timeout}s geantwortet. "
            f"Großes Modell? Beim ersten Laden kann es länger dauern. "
            f"Timeout erhöhen via OLLAMA_LOCAL_TIMEOUT / OLLAMA_CLOUD_TIMEOUT."
        ) from exc

    def generate(self, system_prompt: str, user_message: str) -> LLMResponse:
        if not self.is_available():
            raise ConnectionError(
                f"Ollama nicht erreichbar unter {self._host}. "
                "Bitte Ollama starten: 'ollama serve'"
            )

        payload = self._build_payload(system_prompt, user_message, stream=False)

        try:
            res = requests.post(
                f"{self._host}/api/chat",
                json=payload,
                headers=self._headers(),
                timeout=self._timeout,
            )
        except requests.exceptions.ReadTimeout as e:
            self._raise_on_timeout(e)

        if not res.ok:
            try:
                body = res.json().get("error", res.text[:400])
            except Exception:
                body = res.text[:400]
            raise requests.HTTPError(
                f"{res.status_code} {res.reason} — {body}",
                response=res,
            )

        data = res.json()
        msg = data["message"]
        # Thinking models (e.g. gpt-oss, kimi) put the answer in "thinking"
        # when they reason through their full output; fall back if content is empty
        content = msg.get("content") or msg.get("thinking", "")

        return LLMResponse(content=content, model=self._model, provider="ollama")

    def generate_stream(self, system_prompt: str, user_message: str):
        """
        Yields typed event dicts for SSE streaming:
          {"type": "meta",      "model": ..., "provider": ...}
          {"type": "loaded"}                   — first token arrived (model was ready)
          {"type": "thinking",  "delta": ...}  — reasoning chunk (thinking models)
          {"type": "token",     "delta": ...}  — content token
        Raises on connection/HTTP errors (caller handles).
        """
        if not self.is_available():
            raise ConnectionError(
                f"Ollama nicht erreichbar unter {self._host}. "
                "Bitte Ollama starten: 'ollama serve'"
            )

        yield {"type": "meta", "model": self._model, "provider": "ollama"}

        payload = self._build_payload(system_prompt, user_message, stream=True)

        try:
            res = requests.post(
                f"{self._host}/api/chat",
                json=payload,
                headers=self._headers(),
                timeout=self._timeout,
                stream=True,
            )
        except requests.exceptions.ReadTimeout as e:
            self._raise_on_timeout(e)

        if not res.ok:
            try:
                body = res.json().get("error", res.text[:400])
            except Exception:
                body = res.text[:400]
            raise requests.HTTPError(
                f"{res.status_code} {res.reason} — {body}",
                response=res,
            )

        first_chunk = True
        for line in res.iter_lines():
            if not line:
                continue
            try:
                chunk = json.loads(line)
            except Exception:
                continue

            if first_chunk:
                yield {"type": "loaded"}
                first_chunk = False

            msg = chunk.get("message", {})
            thinking = msg.get("thinking", "")
            content = msg.get("content", "")

            if thinking:
                yield {"type": "thinking", "delta": thinking}
            if content:
                yield {"type": "token", "delta": content}

            if chunk.get("done"):
                return
