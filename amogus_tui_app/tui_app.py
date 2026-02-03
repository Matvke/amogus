import json

from colorama import Fore, Style
from requests.exceptions import ReadTimeout
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import (
    Footer,
    Header,
    Log,
    Pretty,
    TabbedContent,
    TabPane,
    Tree,
)

from .api_methods import get_cycles, get_electives, post_lesson
from .entities import Lesson, Team
from .settings import Settings
from .timer import BackgroundTimer

logs = Log()


class SelectedItems:
    def __init__(self):
        self._unique_teams = dict()  # lesson_id: [team]

    def append(self, team: Team) -> bool:
        if team.lesson_id in self._unique_teams.keys():
            if team.id in list(map(lambda x: x.id, self._unique_teams[team.lesson_id])):
                logs.write_line("Team already exists")
                return False
            self._unique_teams[team.lesson_id].append(team)
            logs.write_line(f"Append team to {team.lesson_id}")
        else:
            self._unique_teams[team.lesson_id] = [team]
            logs.write_line(f"Init {team.lesson_id}")
        return True

    def delete(self, team: Team) -> True:
        if team.lesson_id in self._unique_teams.keys():
            if team.id in list(map(lambda x: x.id, self._unique_teams[team.lesson_id])):
                logs.write_line("Team deleted")
                self._unique_teams[team.lesson_id].remove(team)
                return True
        logs.write_line("Error deleting team")
        return False


selected_items = SelectedItems()


class MenuTree(Tree):
    BINDINGS = [
        *Tree.BINDINGS,
        Binding("ctrl+s", "set_discipline", "Выбрать", show=True),
        Binding("ctrl+d", "delete_discipline", "Удалить", show=True),
    ]

    def __init__(self, label, settings: Settings, *args, **kwargs):
        super().__init__(label, *args, **kwargs)
        self.settings = settings

    def on_tree_node_expanded(self, message: Tree.NodeExpanded) -> None:
        node = message.node
        if node.data and isinstance(node.data, Lesson) and not node.children:
            cycles = get_cycles(self.settings, node.data.id)
            for cycle in cycles:
                lesson_node = node.add(label=f"{cycle.name}", data=cycle)
                for team in cycle.teams:
                    new_team = Team(
                        id=team.id,
                        name=team.name,
                        totalSeats=team.totalSeats,
                        professors=team.professors,
                        lesson_id=lesson_node.data.id,
                    )
                    team_node = lesson_node.add(
                        label=f"{team.name} {team.id}", data=new_team
                    )
                    for professor in team.professors:
                        team_node.add_leaf(label=professor.name, data=professor)
            logs.write_line(f"Cycles successfully loaded. Lesson id = {node.data.id}")

        elif node.id == 0 and not node.children:
            self.electives = self.root.add("Дисциплины")
            electives_list = []
            try:
                electives_list = get_electives(self.settings)
            except ValueError as e:
                self.notify(f"Error: {str(e)}")
            except ReadTimeout:
                self.notify("The website is down")
            if not electives_list:
                logs.write_line("Failed to get list of electives")
            for elective in electives_list:
                elective_node = self.electives.add(
                    label=f"{elective.name}", data=elective
                )
                for lesson in elective.children:
                    elective_node.add(label=f"{lesson.name} {lesson.id}", data=lesson)
            logs.write_line(f"Logged as {self.settings.user}")

    def action_set_discipline(self) -> None:
        node = self.cursor_node
        if node.data and isinstance(node.data, Team):
            team = Team(
                id=node.data.id,
                name=node.data.name,
                totalSeats=node.data.totalSeats,
                professors=node.data.professors,
                lesson_id=node.parent.parent.data.id,
            )
            response = selected_items.append(team)
            if response:
                self.notify("Выбрано")
                logs.write_line("Disciplines successfully set")
                pretty.refresh(layout=True)
            else:
                self.notify("Ошибка, уже выбрано", severity="error")

        else:
            self.notify("Ошибка, не команда", severity="error")
            logs.write_line("Disciplines set error. IsNotDiscipline")

    def action_delete_discipline(self) -> None:
        node = self.cursor_node
        if node.data and isinstance(node.data, Team):
            team = Team(
                id=node.data.id,
                name=node.data.name,
                totalSeats=node.data.totalSeats,
                professors=node.data.professors,
                lesson_id=node.parent.parent.data.id,
            )
            respone = selected_items.delete(team)
            if respone:
                self.notify("Удалено")
                logs.write_line("Disciplines successfully delete")
                pretty.refresh(layout=True)
            else:
                self.notify("Ошибка, не существует", severity="error")

        else:
            self.notify("Ошибка, не команда", severity="error")
            logs.write_line("Disciplines delete error. IsNotDiscipline")


pretty = Pretty(selected_items._unique_teams)


class AmogusApp(App):
    BINDINGS = [
        *App.BINDINGS,
        Binding("ctrl+x", "save_disciplines", "Сохранить команды", show=True),
        Binding("ctrl+z", "load_disciplines", "Загрузить команды", show=True),
        Binding("ctrl+v", "push_disciplines", "Записаться", show=True),
    ]

    def __init__(self, settings: Settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Tree", id="menu-tab"):
                yield MenuTree(label="Меню выбора", settings=self.settings)
            with TabPane("Json", id="pretty-tab"):
                yield pretty
            with TabPane("Logs", id="logs-tab"):
                yield logs

        yield Header()
        yield Footer()

    def action_load_disciplines(self) -> None:
        with open("disciplines.json", "r", encoding="utf-8") as file:
            deseralizable_dict = json.load(file)
            for lesson_id, teams in deseralizable_dict.items():
                selected_items._unique_teams[lesson_id] = [
                    Team.model_validate(team) for team in teams
                ]
        self.notify("Выгружено из disciplines.json")
        logs.write_line("Successfully loaded from file")
        pretty.refresh(layout=True)

    def action_save_disciplines(self) -> None:
        serializable_dict = {}
        for lesson_id, teams in selected_items._unique_teams.items():
            serializable_dict[lesson_id] = [team.dict() for team in teams]

        with open("disciplines.json", "w", encoding="utf-8") as file:
            json.dump(serializable_dict, file, ensure_ascii=False, indent=4)
        self.notify("Сохранено в disciplines.json")
        logs.write_line("Successfully save to file")

    def action_push_disciplines(self) -> None:
        pick_time = self.settings.pick_time.split(":")
        BackgroundTimer(
            hour=pick_time[0], minute=pick_time[1], func=self.push_disciplines
        )
        self.notify(f"Установлен таймер {self.settings.pick_time}")
        logs.write_line(f"Timer set {self.settings.pick_time}")

    def push_disciplines(self):
        logs.write_line("Start pushing")
        self.notify("Начинаю записывать")

        for lesson_id, teams in selected_items._unique_teams.items():
            payload = [lesson_id]
            for team in teams:
                payload.append(team.id)
            logs.write_line(f"Payload set: {payload}")
            response = post_lesson(self.settings, payload)
            response_data = response.json()
            if response.status_code == 200:
                logs.write_line(
                    f"{Fore.GREEN}[УСПЕХ] Записан на дисциплину {payload[0]}.{Style.RESET_ALL}"
                )
                self.notify("[УСПЕХ]")
                if response_data.get("errors"):
                    logs.write_lines(
                        f"{Fore.YELLOW}Но есть предупреждения: {response_data['errors']}{Style.RESET_ALL}"
                    )
            else:
                logs.write_line(
                    f"{Fore.RED}[ОШИБКА {response.status_code}] для {payload[0]}: {response_data}{Style.RESET_ALL}"
                )
                self.notify("[ОШИБКА]")
