import json

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Log, Pretty, TabbedContent, TabPane, Tree

from api_methods import get_cycles, get_electives
from entities import Lesson, Team
from settings import settings

logs = Log()


class SelectedItems:
    def __init__(self):
        self._unique_teams = dict()  # lesson_id: [team]

    def append(self, team: Team):
        logs.write("Trying to add team\n")
        if team.lesson_id in self._unique_teams.keys():
            if team.id in list(map(lambda x: x.id, self._unique_teams[team.lesson_id])):
                logs.write("Team already exists\n")
                return
            self._unique_teams[team.lesson_id].append(team)
            logs.write(f"Append team to {team.lesson_id}\n")
        else:
            self._unique_teams[team.lesson_id] = [team]
            logs.write(f"Init {team.lesson_id}\n")


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
            logs.write(f"Cycles successfully loaded. Lesson id = {node.data.id}\n")

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
            logs.write("Disciplines successfully set\n")
            pretty.refresh(layout=True)
        else:
            self.notify("Ошибка", severity="error")
            logs.write("Disciplines set error. IsNotDiscipline\n")


menu = MenuTree("Меню выбора")
pretty = Pretty(selected_items._unique_teams)


class AmogusApp(App):
    BINDINGS = [
        *App.BINDINGS,
        Binding("ctrl+x", "save_disciplines", "Сохранить команды", show=True),
        Binding("ctrl+z", "load_disciplines", "Загрузить команды", show=True),
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
        logs.write("Succesfully loaded from file\n")

        pretty.refresh(layout=True)

    def action_save_disciplines(self) -> None:
        serializable_dict = {}
        for lesson_id, teams in selected_items._unique_teams.items():
            serializable_dict[lesson_id] = [team.dict() for team in teams]

        with open("disciplines.json", "w", encoding="utf-8") as file:
            json.dump(serializable_dict, file, ensure_ascii=False, indent=4)
        self.notify("Сохранено в disciplines.json")
        logs.write("Succesfully save to file\n")


if __name__ == "__main__":
    app = AmogusApp()
    app.run()
