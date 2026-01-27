from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Label, ListItem, ListView, Tree

from api_methods import get_cycles, get_electives
from entities import Lesson, Team
from settings import settings


class SelectedList(ListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._unique_teams = dict()  # lesson_id: [team_id]

    def append(self, team: Team):
        item_str = str(team)
        if team.lesson_id in self._unique_teams.keys():
            if team.id in self._unique_teams[team.lesson_id]:
                return
            self._unique_teams[team.lesson_id].append(team.id)
        else:
            self._unique_teams[team.lesson_id] = [team.id]
        new_item = ListItem(Label(item_str))
        new_item.data = team
        super().append(new_item)


selected_items = SelectedList(ListItem(Label("Выбранные команды")))


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
                    team_node = lesson_node.add(
                        label=f"{team.name} {team.id}", data=team
                    )
                    for professor in team.professors:
                        team_node.add_leaf(label=professor.name, data=professor)

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


class AmogusApp(App):
    BINDINGS = [
        *App.BINDINGS,
        Binding("ctrl+x", "save_disciplines", "Сохранить команды", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield MenuTree("Меню выбора")
        yield selected_items
        yield Header()
        yield Footer()

    def action_save_disciplines(self) -> None:
        with open("disciplines.json", "w") as file:
            for lesson_id, teams in selected_items._unique_teams.items():
                # TODO: Структура body для Post
                # запроса для записи на курс состоит из
                # 2 частей (3 для дисциплин с лекциями)
                # Поэтому нужно сохранять все в виде: ["id lesson", "id team (лекции)", "id team (практики)"]
                file.write(f"{lesson_id} {' '.join(list(map(str, teams)))}")
            self.notify("Сохранено в disciplines.json")


if __name__ == "__main__":
    app = AmogusApp()
    app.run()
