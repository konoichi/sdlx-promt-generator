from abc import ABC, abstractmethod
from typing import Optional, List

class Addon(ABC):
    """Basis-Klasse für alle Addons/Plugins."""
    
    @property
    @abstractmethod
    def id(self) -> str:
        """Eindeutige ID des Addons (z.B. 'model_hub')."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Anzeigename des Addons."""
        pass

    @property
    @abstractmethod
    def required_feature_key(self) -> str:
        """
        Der Capability-Key, der benötigt wird, um dieses Addon freizuschalten.
        Wenn leer, ist das Addon immer verfügbar (sofern installiert).
        """
        pass


class ModelMetadataProvider(Addon):
    """Spezialisierung für Addons, die Modell-Metadaten liefern."""
    
    @abstractmethod
    def get_model_info(self, model_name: str, model_type: str = "checkpoint") -> Optional[dict]:
        """Holt Informationen zu einem spezifischen Modell."""
        pass
    
    @abstractmethod
    def search_models(self, query: str, model_type: str = "lora") -> List[dict]:
        """Sucht nach Modellen (z.B. LoRAs)."""
        pass
