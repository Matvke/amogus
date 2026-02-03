import json

from amogus_tui_app.entities import Team


class SelectedItems:
    def __init__(self):
        self._unique_teams = dict()  # lesson_id: [team]

    def append(self, team: Team) -> bool:
        if team.lesson_id in self._unique_teams.keys():
            if any(team.id in t.id for t in self._unique_teams[team.lesson_id]):
                return False
            self._unique_teams[team.lesson_id].append(team)
        else:
            self._unique_teams[team.lesson_id] = [team]
        return True

    def delete(self, team: Team) -> bool:
        if team.lesson_id in self._unique_teams.keys():
            if team.id in list(map(lambda x: x.id, self._unique_teams[team.lesson_id])):
                self._unique_teams[team.lesson_id].remove(team)
                return True
        return False

    def load_from_file(self, file_name: str = "disciplines.json"):
        with open(file_name, "r", encoding="utf-8") as file:
            deseralizable_dict = json.load(file)
            for lesson_id, teams in deseralizable_dict.items():
                self._unique_teams[lesson_id] = [
                    Team.model_validate(team) for team in teams
                ]

    def save_to_file(self, file_name: str = "disciplines.json"):
        serializable_dict = {}
        for lesson_id, teams in self._unique_teams.items():
            serializable_dict[lesson_id] = [team.dict() for team in teams]

        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(serializable_dict, file, ensure_ascii=False, indent=4)
