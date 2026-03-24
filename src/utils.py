from textual.widgets.tree import TreeNode

from src.models.entities import Team

from .api_methods import get_cycles, get_electives
from .models.settings import Settings


def load_cycles(settings: Settings, node: TreeNode):
    cycles = get_cycles(settings, node.data.id)
    if not cycles:
        raise ValueError("Cycles is empty")
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
            team_node = lesson_node.add(label=f"{team.name} {team.id}", data=new_team)
            for professor in team.professors:
                team_node.add_leaf(label=professor.name, data=professor)


def load_electives(settings: Settings, node: TreeNode):
    elective_node = node.add("Дисциплины")
    electives = get_electives(settings)
    if not electives:
        raise ValueError("Electives is empty")
    for elective in electives:
        child_node = elective_node.add(label=f"{elective.name}", data=elective)
        for lesson in elective.children:
            child_node.add(label=f"{lesson.name} {lesson.id}", data=lesson)
