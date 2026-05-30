from app.core.addon_ports import Addon

class NSFWExpansionAddon(Addon):
    @property
    def id(self) -> str:
        return "nsfw_expansion"

    @property
    def name(self) -> str:
        return "NSFW & Uncensored Expansion"

    @property
    def required_feature_key(self) -> str:
        return "nsfw_content"
