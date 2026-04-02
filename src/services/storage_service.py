import json
import logging

from src.models.settings import Settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self, settings: Settings, file_name: str | None = None):
        self.settings = settings
        self.file_name = settings.file_name if file_name is None else file_name

    def load_from_file(self) -> dict:
        with open(self.file_name, "r", encoding="utf-8") as file:
            logger.debug("Succes load from the file")
            return json.load(file)

    def save_to_file(self, selection: dict):
        with open(self.file_name, "w", encoding="utf-8") as file:
            logger.debug("Succes save to the file")
            json.dump(selection, file, ensure_ascii=False, indent=4)
