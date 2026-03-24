import json

from src.models.settings import Settings


class StorageService:
    def __init__(self, settings: Settings, file_name: str | None = None):
        self.settings = settings
        self.file_name = settings.file_name if file_name is None else file_name

    def load_from_file(self) -> dict:
        with open(self.file_name, "r", encoding="utf-8") as file:
            return json.load(file)

    def save_to_file(self, selection: dict):
        with open(self.file_name, "w", encoding="utf-8") as file:
            json.dump(selection, file, ensure_ascii=False, indent=4)
