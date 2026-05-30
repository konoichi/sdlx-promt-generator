import os
import json

_CAPABILITIES_FILE = "data/capabilities.json"

# Mock-Lizenzserver-Mapping
_LICENSE_KEYS = {
    "BETA-TESTER": ["premium_model_hub"],
    "PRO-2026": ["premium_model_hub", "advanced_batch"],
    "ULTIMATE": ["all"]
}

def _load_persistent_capabilities() -> list[str]:
    """Lädt freigeschaltete Features aus der JSON-Datei."""
    if os.path.exists(_CAPABILITIES_FILE):
        try:
            with open(_CAPABILITIES_FILE, "r") as f:
                data = json.load(f)
                return data.get("unlocked_features", [])
        except Exception:
            pass
    return []

def _save_persistent_capabilities(features: list[str]):
    """Speichert freigeschaltete Features in die JSON-Datei."""
    os.makedirs(os.path.dirname(_CAPABILITIES_FILE), exist_ok=True)
    with open(_CAPABILITIES_FILE, "w") as f:
        json.dump({"unlocked_features": list(set(features))}, f, indent=2)

def is_feature_unlocked(feature_key: str) -> bool:
    """
    Prüft, ob eine bestimmte Funktion (Capability) freigeschaltet ist.
    Priorität: 1. Umgebungsvariable (für Devs), 2. Persistente JSON-Datei.
    """
    # 1. Check Env (höchste Priorität)
    unlocked_env = os.getenv("UNLOCKED_FEATURES", "")
    if unlocked_env:
        env_keys = [f.strip() for f in unlocked_env.split(",")]
        if feature_key in env_keys or "all" in env_keys:
            return True

    # 2. Check Persistent Storage
    unlocked_persistent = _load_persistent_capabilities()
    return feature_key in unlocked_persistent or "all" in unlocked_persistent

def get_unlocked_features() -> list[str]:
    """Gibt eine Liste aller aktuell freigeschalteten Feature-Keys zurück."""
    features = set()
    
    # Aus Env
    unlocked_env = os.getenv("UNLOCKED_FEATURES", "")
    if unlocked_env:
        features.update([f.strip() for f in unlocked_env.split(",") if f.strip()])
    
    # Aus Storage
    features.update(_load_persistent_capabilities())
    
    return list(features)

def verify_and_unlock(license_key: str) -> tuple[bool, str, list[str]]:
    """
    Prüft einen Lizenz-Key gegen den Mock-Server und schaltet Features frei.
    Returns: (success, message, newly_unlocked_features)
    """
    key = license_key.strip().upper()
    if key in _LICENSE_KEYS:
        new_features = _LICENSE_KEYS[key]
        current = _load_persistent_capabilities()
        updated = list(set(current + new_features))
        _save_persistent_capabilities(updated)
        
        feature_names = ", ".join(new_features) if "all" not in new_features else "Alle Funktionen"
        return True, f"Erfolgreich! Freigeschaltet: {feature_names}", new_features
    
    return False, "Ungültiger Lizenzschlüssel.", []
