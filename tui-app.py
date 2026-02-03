import json

from colorama import Fore, Style
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Log, Pretty, TabbedContent, TabPane, Tree

from api_methods import get_cycles, get_electives, post_lesson
from entities import Lesson, Team
from settings import settings

logs = Log()


class SelectedItems:
    def __init__(self):
        self._unique_teams = dict()  # lesson_id: [team]

    def append(self, team: Team):
        logs.write_line("Trying to add team")
        if team.lesson_id in self._unique_teams.keys():
            if team.id in list(map(lambda x: x.id, self._unique_teams[team.lesson_id])):
                logs.write_line("Team already exists")
                return
            self._unique_teams[team.lesson_id].append(team)
            logs.write_line(f"Append team to {team.lesson_id}")
        else:
            self._unique_teams[team.lesson_id] = [team]
            logs.write_line(f"Init {team.lesson_id}")


selected_items = SelectedItems()


class MenuTree(Tree):
    BINDINGS = [
        *Tree.BINDINGS,
        Binding("ctrl+s", "set_discipline", "Выбрать", show=True),
    ]

    def __init__(self, label):
        super().__init__(label)
        self.electives = self.root.add("Дисциплины")
        for elective in get_electives(settings.menu_id):
            elective_node = self.electives.add(label=f"{elective.name}", data=elective)
            for lesson in elective.children:
                elective_node.add(label=f"{lesson.name} {lesson.id}", data=lesson)

    def on_tree_node_expanded(self, message: Tree.NodeExpanded) -> None:
        node = message.node
        if node.data and isinstance(node.data, Lesson) and not node.children:
            cycles = get_cycles(settings.menu_id, lesson_id=node.data.id)
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
            selected_items.append(team)
            self.notify("Выбрано")
            logs.write_line("Disciplines successfully set")
            pretty.refresh(layout=True)
        else:
            self.notify("Ошибка", severity="error")
            logs.write_line("Disciplines set error. IsNotDiscipline")


menu = MenuTree("Меню выбора")
pretty = Pretty(selected_items._unique_teams)


class AmogusApp(App):
    BINDINGS = [
        *App.BINDINGS,
        Binding("ctrl+x", "save_disciplines", "Сохранить команды", show=True),
        Binding("ctrl+z", "load_disciplines", "Загрузить команды", show=True),
        Binding("ctrl+v", "push_disciplines", "Записаться", show=True),
    ]

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Tree", id="menu-tab"):
                yield menu
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
        logs.write_line("Succesfully loaded from file")

        pretty.refresh(layout=True)

    def action_save_disciplines(self) -> None:
        serializable_dict = {}
        for lesson_id, teams in selected_items._unique_teams.items():
            serializable_dict[lesson_id] = [team.dict() for team in teams]

        with open("disciplines.json", "w", encoding="utf-8") as file:
            json.dump(serializable_dict, file, ensure_ascii=False, indent=4)
        self.notify("Сохранено в disciplines.json")
        logs.write_line("Succesfully save to file")

    def action_push_disciplines(self) -> None:
        for lesson_id, teams in selected_items._unique_teams.items():
            payload = [lesson_id]
            for team in teams:
                payload.append(team.id)
            logs.write_line(f"Payload set: {payload}")
            response = post_lesson(settings.menu_id, payload)
            response_data = response.json()
            if response.status_code == 200:
                logs.write_line(
                    f"{Fore.GREEN}[УСПЕХ] Записан на дисциплину {payload[0]}.{Style.RESET_ALL}"
                )
                if response_data.get("errors"):
                    logs.write_lines(
                        f"{Fore.YELLOW}Но есть предупреждения: {response_data['errors']}{Style.RESET_ALL}"
                    )
            else:
                logs.write_line(
                    f"{Fore.RED}[ОШИБКА {response.status_code}] для {payload[0]}: {response_data}{Style.RESET_ALL}"
                )


if __name__ == "__main__":
    app = AmogusApp()
    app.run()
