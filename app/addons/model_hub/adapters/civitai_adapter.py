import requests
from typing import Optional, Dict

class CivitaiAdapter:
    """Holt Daten von der Civitai API."""
    
    BASE_URL = "https://civitai.com/api/v1"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def get_model_by_name(self, name: str) -> Optional[dict]:
        """Sucht ein Modell nach Namen."""
        try:
            # Civitai hat keine direkte "Get by Name" API, wir nutzen Search
            response = requests.get(
                f"{self.BASE_URL}/models",
                params={"query": name, "limit": 1},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            if data.get("items"):
                return data["items"][0]
        except Exception as e:
            print(f"Fehler bei Civitai-Abfrage: {e}")
        return None

    def get_model_version_by_hash(self, model_hash: str) -> Optional[dict]:
        """Findet eine Modell-Version anhand des SHA256 Hashes."""
        try:
            response = requests.get(
                f"{self.BASE_URL}/model-versions/by-hash/{model_hash}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Fehler bei Civitai-Hash-Abfrage: {e}")
        return None
