from typing import Dict, List, Type, TypeVar, Optional
from app.core.addon_ports import Addon
from app.core.capabilities import is_feature_unlocked

_INSTALLED_ADDONS: Dict[str, Addon] = {}

T = TypeVar('T', bound=Addon)

def register_addon(addon: Addon):
    """Registriert ein Addon im System (Code-Ebene)."""
    _INSTALLED_ADDONS[addon.id] = addon
    print(f"Addon installiert: {addon.name} ({addon.id})")
def get_active_addons(user_capabilities: list[str], is_admin: bool = False) -> List[Addon]:
    """Gibt alle Addons zurück, die für den aktuellen Nutzer freigeschaltet sind."""
    active = []
    for addon in _INSTALLED_ADDONS.values():
        req_key = addon.required_feature_key
        if not req_key or is_feature_unlocked(req_key, user_capabilities, is_admin):
            active.append(addon)
    return active

def get_active_addons_by_type(addon_type: Type[T], user_capabilities: list[str], is_admin: bool = False) -> List[T]:
    """Gibt alle aktiven Addons eines bestimmten Typs für einen Nutzer zurück."""
    return [a for a in get_active_addons(user_capabilities, is_admin) if isinstance(a, addon_type)]

def list_all_installed_addons(user_capabilities: list[str], is_admin: bool = False) -> List[dict]:
    """Gibt eine Liste aller installierten Addons mit ihrem Status für den Nutzer zurück."""
    addons = []
    for aid, a in _INSTALLED_ADDONS.items():
        req_key = a.required_feature_key
        is_active = not req_key or is_feature_unlocked(req_key, user_capabilities, is_admin)
        addons.append({
            "id": a.id,
            "name": a.name,
            "type": a.__class__.__name__,
            "required_key": req_key,
            "is_active": is_active
        })
    return addons
