import json

from models.entities import Team
from models.settings import Settings


class Storage:
    def __init__(self, settings: Settings, file_name: str | None = None):
        self.settings = settings
        self.file_name = settings.file_name if file_name is None else file_name

    def load_from_file(self):
        with open(self.file_name, "r", encoding="utf-8") as file:
            deseralizable_dict = json.load(file)
            for lesson_id, teams in deseralizable_dict.items():
                self._unique_teams[lesson_id] = [
                    Team.model_validate(team) for team in teams
                ]

    def save_to_file(self):
        serializable_dict = {}
        for lesson_id, teams in self._unique_teams.items():
            serializable_dict[lesson_id] = [team.dict() for team in teams]

        with open(self.file_name, "w", encoding="utf-8") as file:
            json.dump(serializable_dict, file, ensure_ascii=False, indent=4)
