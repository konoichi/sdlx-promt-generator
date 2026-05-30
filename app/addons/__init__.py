from typing import Dict, List, Type, TypeVar, Optional
from app.core.addon_ports import Addon
from app.core.capabilities import is_feature_unlocked

_INSTALLED_ADDONS: Dict[str, Addon] = {}
_ACTIVE_ADDONS: Dict[str, Addon] = {}

T = TypeVar('T', bound=Addon)

def register_addon(addon: Addon):
    """
    Registriert ein Addon. Es wird nur aktiviert, wenn die entsprechende 
    Capability freigeschaltet ist.
    """
    _INSTALLED_ADDONS[addon.id] = addon
    
    req_key = addon.required_feature_key
    if not req_key or is_feature_unlocked(req_key):
        _ACTIVE_ADDONS[addon.id] = addon
        print(f"Addon registriert: {addon.name} ({addon.id}) [AKTIV]")
    else:
        print(f"Addon registriert: {addon.name} ({addon.id}) [GESPERRT - benötigt '{req_key}']")

def get_addon(addon_id: str) -> Optional[Addon]:
    """Gibt ein aktives Addon anhand seiner ID zurück."""
    return _ACTIVE_ADDONS.get(addon_id)

def get_addons_by_type(addon_type: Type[T]) -> List[T]:
    """Gibt alle aktiven Addons eines bestimmten Typs zurück."""
    return [a for a in _ACTIVE_ADDONS.values() if isinstance(a, addon_type)]

def list_active_addons() -> List[dict]:
    """Gibt eine Liste der Metadaten aller aktiven Addons zurück."""
    return [
        {"id": a.id, "name": a.name, "type": a.__class__.__name__}
        for a in _ACTIVE_ADDONS.values()
    ]

def list_all_installed_addons() -> List[dict]:
    """Gibt eine Liste aller installierten Addons mit ihrem Status zurück."""
    addons = []
    for aid, a in _INSTALLED_ADDONS.items():
        is_active = aid in _ACTIVE_ADDONS
        addons.append({
            "id": a.id,
            "name": a.name,
            "type": a.__class__.__name__,
            "required_key": a.required_feature_key,
            "is_active": is_active
        })
    return addons
