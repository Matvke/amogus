from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Label, ListItem, ListView, Tree

from api_methods import get_electives, get_lessons
from entities import Lesson, Team
from settings import settings


class SelectedList(ListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._unique_items = set()

    def append(self, item_data):
        item_str = str(item_data)
        if item_str in self._unique_items:
            return

        self._unique_items.add(item_str)

        new_item = ListItem(Label(item_str))
        new_item.data = item_data
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
            elective_node = self.electives.add(label=elective.name, data=elective)
            for lesson in elective.children:
                elective_node.add(label=lesson.name, data=lesson)

    def on_tree_node_expanded(self, message: Tree.NodeExpanded) -> None:
        node = message.node
        if node.data and isinstance(node.data, Lesson):
            lessons = get_lessons(settings.menu_id, lesson_id=node.data.id)
            for lesson in lessons:
                lesson_node = node.add(label=lesson.name, data=lesson)
                for team in lesson.teams:
                    team_node = lesson_node.add(label=team.name, data=team)
                    for professor in team.professors:
                        team_node.add_leaf(label=professor.name, data=professor)

    def action_set_discipline(self) -> None:
        node = self.cursor_node
        if node.data and isinstance(node.data, Team):
            selected_items.append(node.data)


class AmogusApp(App):
    def compose(self) -> ComposeResult:
        yield MenuTree("Меню выбора")
        yield selected_items
        yield Header()
        yield Footer()


if __name__ == "__main__":
    app = AmogusApp()
    app.run()
