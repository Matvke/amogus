import logging

from src.exceptions.custom import TeamAlreadySelectedError

logger = logging.getLogger(__name__)


class SelectService:
    def __init__(self):
        self._selected: dict[str, dict[str, dict[str, str]]] = {}

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        # TODO валидировать
        self._selected = value

    def select_team(self, module_id, lesson_id, cycle_id, team_id):
        """Выбрать команду"""
        if module_id in self._selected:
            if lesson_id in self._selected[module_id]:
                if cycle_id in self._selected[module_id][lesson_id]:
                    logger.debug(
                        "Select team failed: module_id=%s, lesson_id=%s, cycle_id=%s, team_id=%s",
                        module_id,
                        lesson_id,
                        cycle_id,
                        team_id,
                    )
                    raise TeamAlreadySelectedError(
                        "Нельзя выбирать несколько команд в одном курсе"
                    )
            else:
                logger.debug(
                    "Select team failed: module_id=%s, lesson_id=%s, cycle_id=%s, team_id=%s",
                    module_id,
                    lesson_id,
                    cycle_id,
                    team_id,
                )
                raise TeamAlreadySelectedError("В модуле уже выбрана дисциплина")

        self._selected.setdefault(module_id, {}).setdefault(lesson_id, {})[cycle_id] = (
            team_id
        )
        logger.debug(
            "Select team success: module_id=%s, lesson_id=%s, cycle_id=%s, team_id=%s",
            module_id,
            lesson_id,
            cycle_id,
            team_id,
        )

    def deselect_team(self, module_id, lesson_id, cycle_id):
        """Убрать команду из cycle."""
        del self._selected[module_id][lesson_id][cycle_id]
        if not self._selected[module_id][lesson_id]:
            del self._selected[module_id][lesson_id]
            if not self._selected[module_id]:
                del self._selected[module_id]
        logger.debug(
            "Deselect team success: module_id=%s, lesson_id=%s, cycle_id=%s",
            module_id,
            lesson_id,
            cycle_id,
        )

    def is_selected(self, module_id, lesson_id, cycle_id, team_id):
        """Выбрана ли команда"""
        if module_id in self._selected:
            if lesson_id in self._selected[module_id]:
                if cycle_id in self._selected[module_id][lesson_id]:
                    if team_id == self._selected[module_id][lesson_id][cycle_id]:
                        logger.debug(
                            "The team is selected: module_id=%s, lesson_id=%s, cycle_id=%s, team_id=%s",
                            module_id,
                            lesson_id,
                            cycle_id,
                            team_id,
                        )
                        return True
        logger.debug(
            "The team is not selected: module_id=%s, lesson_id=%s, cycle_id=%s, team_id=%s",
            module_id,
            lesson_id,
            cycle_id,
            team_id,
        )
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
        logger.debug("Teams for api: selected=%s", selected)
        return selected

    def get_selected_teams(self) -> set:
        """Вернуть множество id активных команд"""
        teams = set()
        for module_id in self._selected:
            for lesson_id in self._selected[module_id]:
                for cycle_id in self._selected[module_id][lesson_id]:
                    team = self._selected[module_id][lesson_id][cycle_id]
                    teams.add(team)
        logger.debug("Active teams: %s", teams)
        return teams
