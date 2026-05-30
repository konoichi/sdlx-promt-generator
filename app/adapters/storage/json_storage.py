"""
JSON Storage Adapter — speichert Characters und Prompt-Verlauf als JSON-Dateien.
Einfach, portabel, kein Datenbankserver nötig.
Für größere Datenmengen: SQLite-Adapter als Ersatz implementieren (StoragePort).
"""

import json
import uuid
import os
from datetime import datetime
from typing import Optional
from app.core.ports import StoragePort


class JsonStorageAdapter(StoragePort):
    def __init__(self, data_dir: str = "data"):
        self._data_dir = data_dir
        self._characters_file = os.path.join(data_dir, "characters.json")
        self._history_file = os.path.join(data_dir, "prompt_history.json")
        self._ensure_files()

    def _ensure_files(self):
        os.makedirs(self._data_dir, exist_ok=True)
        for path in [self._characters_file, self._history_file]:
            if not os.path.exists(path):
                with open(path, "w") as f:
                    json.dump([], f)

    def _read(self, path: str) -> list:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, path: str, data: list):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # --- Characters ---

    def save_character(self, character: dict) -> str:
        characters = self._read(self._characters_file)
        existing = next((i for i, c in enumerate(characters) if c["id"] == character["id"]), None)

        character["updated_at"] = datetime.now().isoformat()

        if existing is not None:
            characters[existing] = character
        else:
            if "id" not in character:
                character["id"] = str(uuid.uuid4())
            characters.append(character)

        self._write(self._characters_file, characters)
        return character["id"]

    def load_character(self, character_id: str) -> Optional[dict]:
        characters = self._read(self._characters_file)
        return next((c for c in characters if c["id"] == character_id), None)

    def list_characters(self) -> list[dict]:
        characters = self._read(self._characters_file)
        # Neueste zuerst
        return sorted(characters, key=lambda c: c.get("updated_at", ""), reverse=True)

    def delete_character(self, character_id: str) -> bool:
        characters = self._read(self._characters_file)
        filtered = [c for c in characters if c["id"] != character_id]
        if len(filtered) == len(characters):
            return False
        self._write(self._characters_file, filtered)
        return True

    # --- Prompt History ---

    def save_prompt_history(self, entry: dict) -> str:
        history = self._read(self._history_file)
        if "id" not in entry:
            entry["id"] = str(uuid.uuid4())
        history.append(entry)
        self._write(self._history_file, history)
        return entry["id"]

    def list_prompt_history(self, character_id: Optional[str] = None) -> list[dict]:
        history = self._read(self._history_file)
        if character_id:
            history = [h for h in history if h.get("character_id") == character_id]
        return sorted(history, key=lambda h: h.get("created_at", ""), reverse=True)

    def load_prompt_history(self, entry_id: str) -> Optional[dict]:
        history = self._read(self._history_file)
        return next((h for h in history if h["id"] == entry_id), None)

    def delete_prompt_history(self, entry_id: str) -> bool:
        history = self._read(self._history_file)
        filtered = [h for h in history if h["id"] != entry_id]
        if len(filtered) == len(history):
            return False
        self._write(self._history_file, filtered)
        return True

    def update_prompt_history(self, entry_id: str, updates: dict) -> bool:
        history = self._read(self._history_file)
        for i, entry in enumerate(history):
            if entry["id"] == entry_id:
                history[i].update(updates)
                self._write(self._history_file, history)
                return True
        return False
