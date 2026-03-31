class SelectService:
    # TODO use the pipline
    def __init__(self):
        self._selected: dict[str, dict[str, dict[str, str]]] = {}

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value

    def select_team(self, module_id, lesson_id, cycle_id, team_id):
        """Выбрать команду"""
        if module_id in self._selected:
            if lesson_id in self._selected[module_id]:
                if cycle_id in self._selected[module_id][lesson_id]:
                    raise ValueError("Нельзя выбирать несколько команд в одном курсе")
            else:
                raise ValueError("В модуле уже выбрана дисциплина")

        self._selected.setdefault(module_id, {}).setdefault(lesson_id, {})[cycle_id] = (
            team_id
        )

    def deselect_team(self, module_id, lesson_id, cycle_id):
        """Убрать команду"""
        del self._selected[module_id][lesson_id][cycle_id]
        if not self._selected[module_id][lesson_id]:
            del self._selected[module_id][lesson_id]
            if not self._selected[module_id]:
                del self._selected[module_id]

    def is_selected(self, module_id, lesson_id, cycle_id, team_id):
        """Выбрана ли команда"""
        if module_id in self._selected:
            if lesson_id in self._selected[module_id]:
                if cycle_id in self._selected[module_id][lesson_id]:
                    if team_id == self._selected[module_id][lesson_id][cycle_id]:
                        return True
        return False

    def get_teams_for_api(self) -> dict[str, list[str]]:
        """Вернуть команды в формате для API"""
        selected: dict[str, list[str]] = {}
        for module_id in self._selected:
            for lesson_id in self._selected[module_id]:
                teams_list = []
                for cycle_id in self._selected[module_id][lesson_id]:
                    team = self._selected[module_id][lesson_id][cycle_id]
                    teams_list.append(team)
            selected[lesson_id] = teams_list
        return selected

    def get_selected_teams(self) -> set:
        """Вернуть множество id активных команд"""
        teams = set()
        for module_id in self._selected:
            for lesson_id in self._selected[module_id]:
                for cycle_id in self._selected[module_id][lesson_id]:
                    team = self._selected[module_id][lesson_id][cycle_id]
                    teams.add(team)
        return teams
