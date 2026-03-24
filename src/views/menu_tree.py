from textual.binding import Binding
from textual.widgets import (
    Tree,
)
from textual.widgets.tree import TreeNode

from src.models.entities import Cycle, Lesson, ModuleGroup
from src.services.cycle_service import CycleService
from src.services.modulegroup_service import ModuleGroupService


class MenuTree(Tree):
    BINDINGS = [
        *Tree.BINDINGS,
        Binding("ctrl+s", "set_discipline", "Выбрать", show=True),
        Binding("ctrl+d", "delete_discipline", "Удалить", show=True),
    ]

    def __init__(
        self,
        label,
        cycle_service: CycleService,
        module_service: ModuleGroupService,
        *args,
        **kwargs,
    ):
        super().__init__(label, *args, **kwargs)
        self.cycle_service = cycle_service
        self.module_service = module_service

    def on_tree_node_expanded(self, message: Tree.NodeExpanded) -> None:
        """Отрисовка листьев дерева при разворачивании"""
        node = message.node
        if node is self.root:
            try:
                modules = self.module_service.get_modules()
                self._add_modules(node, modules)
            except ValueError as e:
                self.notify(str(e), severity="error")

        elif node.data and isinstance(node.data, Lesson) and not node.children:
            try:
                cycles = self.cycle_service.get_cycles(node.data.id)
                self._add_cycles(node, cycles)
            except ValueError as e:
                with open("logs.txt", "w") as f:
                    f.write(str(e))
                self.notify(str(e), severity="error")

    def _add_cycles(self, node: TreeNode, cycles: list[Cycle]):
        """Отрисовка курсов"""
        for cycle in cycles:
            cycle_node = node.add(label=cycle.name, data=cycle)
            for team in cycle.teams:
                team_node = cycle_node.add(label=f"{team.name} {team.id}", data=team)
                for prof in team.professors:
                    team_node.add_leaf(label=prof.name, data=prof)

    def _add_modules(self, node: TreeNode, modules: list[ModuleGroup]):
        """Отрисовка модулей"""
        elective_node = node.add("Дисциплины")
        for module in modules:
            module_node = elective_node.add(label=module.name, data=module)
            for lesson in module.children:
                module_node.add(label=f"{lesson.name} {lesson.id}", data=lesson)
