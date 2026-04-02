from textual import work
from textual.binding import Binding
from textual.widgets import (
    Tree,
)
from textual.widgets.tree import TreeNode

from src.exceptions.custom import TeamAlreadySelectedError
from src.models.entities import Cycle, Lesson, ModuleGroup, Team
from src.services.cycle_service import CycleService
from src.services.modulegroup_service import ModuleGroupService
from src.services.select_service import SelectService


class MenuTree(Tree):
    BINDINGS = [
        *Tree.BINDINGS,
        Binding("ctrl+s", "select", "Выбрать", show=True),
    ]

    def __init__(
        self,
        label,
        cycle_service: CycleService,
        module_service: ModuleGroupService,
        select_service: SelectService,
        *args,
        **kwargs,
    ):
        super().__init__(label, *args, **kwargs)
        self.cycle_service = cycle_service
        self.module_service = module_service
        self.select_service = select_service
        self._team_nodes: dict[str, TreeNode] = {}

    @work(exclusive=True)
    async def on_tree_node_expanded(self, message: Tree.NodeExpanded) -> None:
        """Отрисовка листьев дерева при разворачивании"""
        node = message.node
        if node is self.root and not node.children:
            try:
                modules = await self.module_service.get_modules()
                self._add_modules(node, modules)
            except ValueError as e:
                self.notify(str(e), severity="error")

        elif node.data and isinstance(node.data, Lesson) and not node.children:
            try:
                cycles = await self.cycle_service.get_cycles(node.data.id)
                self._add_cycles(node, cycles)
            except ValueError as e:
                self.notify(str(e), severity="error")

    def _add_cycles(self, node: TreeNode, cycles: list[Cycle]):
        """Отрисовка курсов и команд"""
        module_id = node.parent.data.id
        lesson_id = node.data.id
        for cycle in cycles:
            cycle_node = node.add(label=cycle.name, data=cycle)
            for team in cycle.teams:
                is_selected = self.select_service.is_selected(
                    module_id, lesson_id, cycle.id, team.id
                )
                label = f"[green]{team.name}[/green]" if is_selected else f"{team.name}"
                team_node = cycle_node.add(label=label, data=team)
                self._team_nodes[team.id] = team_node

                for prof in team.professors:
                    team_node.add_leaf(label=prof.name, data=prof)

    def _add_modules(self, node: TreeNode, modules: list[ModuleGroup]):
        """Отрисовка модулей"""
        for module in modules:
            module_node = node.add(label=module.name, data=module)
            for lesson in module.children:
                module_node.add(label=lesson.name, data=lesson)

    def action_select(self) -> None:
        """Выбрать команду"""
        node = self.cursor_node
        if node.data and isinstance(node.data, Team):
            try:
                module_id, lesson_id, cycle_id, team_id = self._get_parent_ids(node)
                if self.select_service.is_selected(
                    module_id, lesson_id, cycle_id, team_id
                ):
                    self._deselect_team(node, module_id, lesson_id, cycle_id)
                    self.notify("Успешно удалено")
                else:
                    self._select_team(node, module_id, lesson_id, cycle_id, team_id)
                    self.notify("Успешно добавлено")

            except TeamAlreadySelectedError as e:
                self.notify(str(e), severity="error")
        else:
            self.notify("Нужно выбирать команды", severity="warning")

    def _select_team(self, node, module_id, lesson_id, cycle_id, team_id):
        """Выбрать команду"""
        self.select_service.select_team(
            module_id,
            lesson_id,
            cycle_id,
            team_id,
        )
        self._mark_selected(node, True)

    def _deselect_team(self, node, module_id, lesson_id, cycle_id):
        """Удалить команду из выбранных"""
        self.select_service.deselect_team(module_id, lesson_id, cycle_id)
        self._mark_selected(node, select=False)

    def _mark_selected(self, node: TreeNode, select: bool):
        """Покрасить в зеленый"""
        if select:
            node.label = f"[green]{node.label}[/green]"
        else:
            node.label = str(node.label).replace("[green]", "").replace("[/green]", "")

    def _get_parent_ids(self, node: TreeNode, depth: int = 3):
        """Получить ids родителей ноды выше на depth"""
        result = []
        curr_node = node
        for _ in range(depth + 1):
            result.append(curr_node.data.id)
            curr_node = curr_node.parent
        return result[::-1]

    def refresh_selection(self):
        """Обновление подгруженных команд"""
        teams_ids = self.select_service.get_selected_teams()
        for team_id in self._team_nodes:
            if team_id in teams_ids:
                self._mark_selected(self._team_nodes[team_id], True)
            else:
                self._mark_selected(self._team_nodes[team_id], False)
