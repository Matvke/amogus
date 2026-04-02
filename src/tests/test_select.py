import pytest

from src.exceptions.custom import TeamAlreadySelectedError
from src.services.select_service import SelectService


class TestSelectServiceSelectTeam:
    """Тесты для метода select_team"""

    @pytest.fixture
    def service(self):
        return SelectService()

    def test_select_first_team_in_empty_service(self, service: SelectService):
        """Выбор первой команды в пустом сервисе"""
        service.select_team(
            module_id="Языки программирования",
            lesson_id="Python",
            cycle_id="Практика",
            team_id="АТ-01 Иванов",
        )

        assert service._selected == {
            "Языки программирования": {"Python": {"Практика": "АТ-01 Иванов"}}
        }

    def test_select_two_different_cycles_same_lesson(self, service: SelectService):
        """Выбор лекции и практики в одном предмете"""
        service.select_team(
            "Языки программирования", "Python", "Практика", "АТ-01 Иванов"
        )
        service.select_team("Языки программирования", "Python", "Лекция", "Л-01 Шадрин")

        assert service._selected == {
            "Языки программирования": {
                "Python": {"Практика": "АТ-01 Иванов", "Лекция": "Л-01 Шадрин"}
            }
        }

    def test_select_same_cycle_twice_raises_error(self, service: SelectService):
        """Нельзя выбрать две команды в одном цикле (две практики)"""
        service.select_team(
            "Языки программирования", "Python", "Практика", "АТ-01 Иванов"
        )

        with pytest.raises(
            TeamAlreadySelectedError,
            match="Нельзя выбирать несколько команд в одном курсе",
        ):
            service.select_team(
                "Языки программирования", "Python", "Практика", "АТ-02 Петров"
            )

    def test_select_different_lesson_same_module_raises_error(
        self, service: SelectService
    ):
        """Нельзя выбрать Python и C++ в одном модуле (два курса)"""
        service.select_team(
            "Языки программирования", "Python", "Практика", "АТ-01 Иванов"
        )

        with pytest.raises(
            TeamAlreadySelectedError, match="В модуле уже выбрана дисциплина"
        ):
            service.select_team(
                "Языки программирования", "C++", "Практика", "АТ-03 Сидоров"
            )

    def test_select_team_in_new_module_after_other_module_has_data(
        self, service: SelectService
    ):
        """Выбор в новом модуле, когда другой модуль уже имеет данные"""
        service.select_team(
            "Языки программирования", "Python", "Практика", "АТ-01 Иванов"
        )
        service.select_team("Математика", "Алгебра", "Лекция", "Л-04 Петрова")

        assert service._selected["Математика"]["Алгебра"]["Лекция"] == "Л-04 Петрова"
        assert (
            service._selected["Языки программирования"]["Python"]["Практика"]
            == "АТ-01 Иванов"
        )

    def test_select_team_with_same_lesson_name_in_different_modules(
        self, service: SelectService
    ):
        """Проверка на одинаковые названия курсов в разных модулях"""
        service.select_team(
            "Языки программирования", "Python", "Практика", "АТ-01 Иванов"
        )
        service.select_team("Факультатив", "Python", "Лекция", "Л-01 Соколов")

        assert (
            service._selected["Языки программирования"]["Python"]["Практика"]
            == "АТ-01 Иванов"
        )
        assert service._selected["Факультатив"]["Python"]["Лекция"] == "Л-01 Соколов"

    def test_select_team_after_deselect_in_same_module(self, service: SelectService):
        """После удаления команды можно выбрать новую дисциплину в том же модуле"""
        service.select_team(
            "Языки программирования", "Python", "Практика", "АТ-01 Иванов"
        )
        service.deselect_team("Языки программирования", "Python", "Практика")

        service.select_team("Языки программирования", "C++", "Лекция", "Л-01 Орлов")

        assert service._selected == {
            "Языки программирования": {"C++": {"Лекция": "Л-01 Орлов"}}
        }

    def test_select_team_after_deselect_all_cycles_in_lesson(
        self, service: SelectService
    ):
        """После удаления всех курсов предмета можно выбрать другой предмет"""
        service.select_team(
            "Языки программирования", "Python", "Практика", "АТ-01 Иванов"
        )
        service.select_team("Языки программирования", "Python", "Лекция", "Л-01 Шадрин")
        service.deselect_team("Языки программирования", "Python", "Практика")
        service.deselect_team("Языки программирования", "Python", "Лекция")

        service.select_team("Языки программирования", "C++", "Практика", "АТ-02 Петров")

        assert service._selected == {
            "Языки программирования": {"C++": {"Практика": "АТ-02 Петров"}}
        }

    def test_select_team_in_lesson_with_same_name_as_deleted_lesson(
        self, service: SelectService
    ):
        """Выбор предмета с таким же названием как удаленный"""
        service.select_team(
            "Языки программирования", "Python", "Практика", "АТ-01 Иванов"
        )
        service.deselect_team("Языки программирования", "Python", "Практика")

        service.select_team("Языки программирования", "Python", "Лекция", "Л-01 Шадрин")

        assert service._selected == {
            "Языки программирования": {"Python": {"Лекция": "Л-01 Шадрин"}}
        }
