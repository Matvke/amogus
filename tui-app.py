from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Tree

from api_methods import get_electives, get_lessons
from settings import settings


class MyTree(Tree):
    def on_tree_node_expanded(self, message: Tree.NodeExpanded) -> None:
        node = message.node
        if node.data and node.data[0] == "lesson":
            lessons = get_lessons(settings.menu_id, lesson_id=node.data[1])
            for lesson in lessons:
                lesson_node = node.add(label=lesson.name, data=("cycle", lesson.id))
                for team in lesson.teams:
                    team_node = lesson_node.add(label=team.name, data=("team", team.id))
                    for professor in team.professors:
                        team_node.add_leaf(label=professor.name, data=("professor"))


class AmogusApp(App):
    def compose(self) -> ComposeResult:
        tree: MyTree[str] = MyTree("Меню выбора")
        electives = tree.root.add("Дисциплины")
        for elective in get_electives(settings.menu_id):
            elective_node = electives.add(
                label=elective.name, data=("elective", elective.id)
            )
            for lesson in elective.children:
                elective_node.add(label=lesson.name, data=("lesson", lesson.id))

        yield tree
        yield Header()
        yield Footer()


if __name__ == "__main__":
    app = AmogusApp()
    app.run()
