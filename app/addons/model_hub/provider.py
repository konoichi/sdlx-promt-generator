import os
import json
from typing import Optional, List
from app.core.addon_ports import ModelMetadataProvider
from .adapters.civitai_adapter import CivitaiAdapter

class ModelHubProvider(ModelMetadataProvider):
    def __init__(self, cache_dir: str = "data/cache/model_hub"):
        self.adapter = CivitaiAdapter()
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    @property
    def id(self) -> str:
        return "model_hub"

    @property
    def name(self) -> str:
        return "Model Metadata Hub"

    @property
    def required_feature_key(self) -> str:
        return "premium_model_hub"

    def get_model_info(self, model_name: str, model_type: str = "checkpoint") -> Optional[dict]:
        # 1. Cache prüfen
        cache_path = os.path.join(self.cache_dir, f"{model_name.replace('.', '_')}.json")
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                return json.load(f)

        # 2. Civitai abfragen
        raw_data = self.adapter.get_model_by_name(model_name)
        if not raw_data:
            return None

        # 3. In Unified Schema transformieren
        info = {
            "id": f"civitai_{raw_data.get('id')}",
            "name": raw_data.get("name"),
            "type": raw_data.get("type", "").lower(),
            "base_model": "",
            "trigger_words": [],
            "recommended_settings": {},
            "description": raw_data.get("description", ""),
        }

        # Basis-Modell und Triggerwords aus der neuesten Version holen
        versions = raw_data.get("modelVersions", [])
        if versions:
            latest = versions[0]
            info["base_model"] = latest.get("baseModel", "")
            info["trigger_words"] = latest.get("trainedWords", [])
            # Empfohlene Einstellungen extrahieren (falls vorhanden)
            # Hinweis: Civitai hat hierfür kein standardisiertes Feld, oft steht es in der Description
        
        # 4. Cachen
        with open(cache_path, "w") as f:
            json.dump(info, f, indent=2)

        return info

    def search_models(self, query: str, model_type: str = "lora") -> List[dict]:
        # Für die Zukunft: Liste von Modellen zurückgeben
        return []
