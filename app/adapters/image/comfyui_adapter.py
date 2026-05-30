import requests
import random
import time

from app.core.ports import (
    ImageBackendPort,
    ImageBackendStatus,
    ImageGenerationRequest,
    ImageGenerationResult,
)


class ComfyUIAdapter(ImageBackendPort):
    def __init__(self, host: str = "http://localhost:8188", timeout: int = 5):
        self._host = host.rstrip("/")
        self._timeout = timeout

    @property
    def id(self) -> str:
        return "comfyui"

    @property
    def name(self) -> str:
        return "ComfyUI"

    @property
    def host(self) -> str:
        return self._host

    def set_host(self, host: str):
        self._host = host.rstrip("/")

    def status(self) -> ImageBackendStatus:
        try:
            stats_res = requests.get(
                f"{self._host}/system_stats",
                timeout=self._timeout,
            )
            stats_res.raise_for_status()
            models = self._checkpoint_models()
            return ImageBackendStatus(
                id=self.id,
                name=self.name,
                host=self._host,
                available=True,
                models=models,
                capabilities=["prompt_workflow", "queue", "history", "models"],
            )
        except Exception as exc:
            return ImageBackendStatus(
                id=self.id,
                name=self.name,
                host=self._host,
                available=False,
                models=[],
                capabilities=["prompt_workflow", "queue", "history", "models"],
                error=str(exc),
            )

    def _checkpoint_models(self) -> list[str]:
        try:
            res = requests.get(f"{self._host}/object_info", timeout=self._timeout)
            res.raise_for_status()
            ckpt_loader = res.json().get("CheckpointLoaderSimple", {})
            inputs = ckpt_loader.get("input", {}).get("required", {})
            ckpt = inputs.get("ckpt_name", [])
            if isinstance(ckpt, list) and ckpt and isinstance(ckpt[0], list):
                return ckpt[0]
        except Exception:
            pass
        return []

    def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        workflow = self._build_workflow(request)
        res = requests.post(
            f"{self._host}/prompt",
            json={"prompt": workflow},
            timeout=self._timeout,
        )
        res.raise_for_status()
        prompt_id = res.json()["prompt_id"]
        image_ref = self._wait_for_image(prompt_id)
        image_res = requests.get(f"{self._host}/view", params=image_ref, timeout=60)
        image_res.raise_for_status()
        filename = image_ref.get("filename", "")
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "png"
        return ImageGenerationResult(
            image_bytes=image_res.content,
            extension=ext if ext in {"png", "jpg", "jpeg", "webp"} else "png",
            metadata={
                "backend": self.id,
                "host": self._host,
                "model": request.model,
                "prompt_id": prompt_id,
                "filename": filename,
            },
        )

    def _wait_for_image(self, prompt_id: str) -> dict:
        deadline = time.time() + max(self._timeout, 300)
        while time.time() < deadline:
            res = requests.get(f"{self._host}/history/{prompt_id}", timeout=self._timeout)
            res.raise_for_status()
            item = res.json().get(prompt_id)
            if item:
                status = item.get("status", {})
                if status.get("status_str") == "error":
                    raise RuntimeError(self._format_error(status))
                outputs = item.get("outputs", {})
                for output in outputs.values():
                    images = output.get("images") or []
                    if images:
                        return images[0]
            time.sleep(1)
        raise TimeoutError(f"ComfyUI prompt {prompt_id} did not finish in time")

    def _format_error(self, status: dict) -> str:
        for msg_type, payload in status.get("messages", []):
            if msg_type == "execution_error":
                exc_type = payload.get("exception_type", "ComfyUI error")
                exc_msg = payload.get("exception_message", "")
                node = payload.get("node_type") or payload.get("node_id", "")
                if "OutOfMemory" in exc_type or "out of memory" in exc_msg.lower():
                    return (
                        "ComfyUI hat nicht genug GPU-Speicher für diese Render-Einstellungen. "
                        "Kleinere Größe, weniger Steps oder ein kleineres Modell wählen."
                    )
                return f"{exc_type} {node}: {exc_msg}".strip()
        return "ComfyUI konnte den Workflow nicht ausführen"

    def _build_workflow(self, request: ImageGenerationRequest) -> dict:
        seed = request.seed if request.seed >= 0 else random.randint(0, 2**31 - 1)
        ckpt = request.model or "juggernautXL_ragnarokBy.safetensors"
        return {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": ckpt},
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": request.positive_prompt, "clip": ["1", 1]},
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": request.negative_prompt, "clip": ["1", 1]},
            },
            "4": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": request.width,
                    "height": request.height,
                    "batch_size": 1,
                },
            },
            "5": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": request.steps,
                    "cfg": request.cfg_scale,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0],
                },
            },
            "6": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": "sdxl_prompt_app", "images": ["6", 0]},
            },
        }
