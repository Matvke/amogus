from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Tree

from api_methods import get_electives, get_lessons
from entities import Lesson
from settings import settings


class MenuTree(Tree):
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


class AmogusApp(App):
    def compose(self) -> ComposeResult:
        yield MenuTree("Меню выбора")
        yield Header()
        yield Footer()


if __name__ == "__main__":
    app = AmogusApp()
    app.run()
