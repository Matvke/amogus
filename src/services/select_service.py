class SelectService:
    def __init__(self):
        self._selected: dict[str, dict[str, dict[str, str]]] = {}

    def select_team(self, module_id, lesson_id, cycle_id, team_id):
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
        del self._selected[module_id][lesson_id][cycle_id]
        if not self._selected[module_id][lesson_id]:
            del self._selected[module_id][lesson_id]
            if not self._selected[module_id]:
                del self._selected[module_id]

    def is_selected(self, module_id, lesson_id, cycle_id, team_id):
        if module_id in self._selected:
            if lesson_id in self._selected[module_id]:
                if cycle_id in self._selected[module_id][lesson_id]:
                    if team_id == self._selected[module_id][lesson_id][cycle_id]:
                        return True
        return False
