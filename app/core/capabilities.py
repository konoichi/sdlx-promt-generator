import os

# Mock-Lizenzserver-Mapping (zentral definiert)
_LICENSE_KEYS = {
    "BETA-TESTER": ["premium_model_hub"],
    "PRO-2026": ["premium_model_hub", "advanced_batch"],
    "ULTIMATE": ["all"]
}

def is_feature_unlocked(feature_key: str, user_capabilities: list[str]) -> bool:
    """
    Prüft, ob eine bestimmte Funktion für einen Nutzer freigeschaltet ist.
    Inklusive Check der Umgebungsvariable 'UNLOCKED_FEATURES' für globale Overrides.
    """
    # 1. Globaler Override via Env (für Devs)
    unlocked_env = os.getenv("UNLOCKED_FEATURES", "")
    if unlocked_env:
        env_keys = [f.strip() for f in unlocked_env.split(",")]
        if feature_key in env_keys or "all" in env_keys:
            return True

    # 2. Nutzer-spezifische Capabilities
    return feature_key in user_capabilities or "all" in user_capabilities

def verify_license_key(license_key: str) -> tuple[bool, str, list[str]]:
    """
    Prüft einen Lizenz-Key gegen den Mock-Server.
    Gibt (success, message, features) zurück.
    """
    key = license_key.strip().upper()
    if key in _LICENSE_KEYS:
        features = _LICENSE_KEYS[key]
        feature_names = ", ".join(features) if "all" not in features else "Alle Funktionen"
        return True, f"Erfolgreich! Freigeschaltet: {feature_names}", features
    
    return False, "Ungültiger Lizenzschlüssel.", []
