import requests
import base64

from app.core.ports import (
    ImageBackendPort,
    ImageBackendStatus,
    ImageGenerationRequest,
    ImageGenerationResult,
)


class Automatic1111Adapter(ImageBackendPort):
    def __init__(self, host: str = "http://localhost:7860", timeout: int = 5):
        self._host = host.rstrip("/")
        self._timeout = timeout

    @property
    def id(self) -> str:
        return "automatic1111"

    @property
    def name(self) -> str:
        return "Automatic1111"

    @property
    def host(self) -> str:
        return self._host

    def set_host(self, host: str):
        self._host = host.rstrip("/")

    def status(self) -> ImageBackendStatus:
        try:
            models_res = requests.get(
                f"{self._host}/sdapi/v1/sd-models",
                timeout=self._timeout,
            )
            models_res.raise_for_status()
            models = [
                m.get("model_name") or m.get("title") or m.get("filename", "")
                for m in models_res.json()
            ]
            return ImageBackendStatus(
                id=self.id,
                name=self.name,
                host=self._host,
                available=True,
                models=[m for m in models if m],
                capabilities=["txt2img", "img2img", "models"],
            )
        except Exception as exc:
            return ImageBackendStatus(
                id=self.id,
                name=self.name,
                host=self._host,
                available=False,
                models=[],
                capabilities=["txt2img", "img2img", "models"],
                error=str(exc),
            )

    def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        payload = {
            "prompt": request.positive_prompt,
            "negative_prompt": request.negative_prompt,
            "width": request.width,
            "height": request.height,
            "steps": request.steps,
            "cfg_scale": request.cfg_scale,
            "seed": request.seed,
            "sampler_name": "Euler a",
        }
        if request.model:
            payload["override_settings"] = {"sd_model_checkpoint": request.model}

        res = requests.post(
            f"{self._host}/sdapi/v1/txt2img",
            json=payload,
            timeout=max(self._timeout, 300),
        )
        res.raise_for_status()
        data = res.json()
        images = data.get("images") or []
        if not images:
            raise RuntimeError("Automatic1111 returned no image")
        raw = images[0].split(",", 1)[-1]
        return ImageGenerationResult(
            image_bytes=base64.b64decode(raw),
            extension="png",
            metadata={
                "backend": self.id,
                "host": self._host,
                "model": request.model,
                "info": data.get("info", ""),
            },
        )
