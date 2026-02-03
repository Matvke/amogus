from typing import Callable

from colorama import Fore, Style
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
from textual.widgets.tree import TreeNode

from .api_methods import post_lesson
from .entities import Lesson, Team
from .selected_items import SelectedItems
from .settings import Settings
from .timer import BackgroundTimer
from .utils import load_cycles, load_electives

logs = Log()


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
            load_cycles(self.settings, node)
            logs.write_line(f"Cycles successfully loaded. Lesson id = {node.data.id}")

        elif node.id == 0 and not node.children:
            load_electives(self.settings, self.root)
            logs.write_line(f"Logged in as {self.settings.user}")
            logs.write_line("Electives successfully loaded.")

    def action_set_discipline(self) -> None:
        node = self.cursor_node
        self._process_disciplie(
            node,
            selected_items.append,
            error_msg="Ошибка. Уже существует.",
            succes_msg="Добавлено",
        )

    def action_delete_discipline(self) -> None:
        node = self.cursor_node
        self._process_disciplie(
            node,
            selected_items.delete,
            error_msg="Ошибка. Не существует.",
            succes_msg="Удалено",
        )

    def _process_disciplie(
        self, node: TreeNode, action: Callable[[Team], bool], error_msg, succes_msg
    ):
        if node.data and isinstance(node.data, Team):
            team = self._create_team_from_node(node)
            response = action(team)
            if response:
                self.notify(succes_msg)
                logs.write_line(succes_msg)
                pretty.refresh(layout=True)
            else:
                self.notify(error_msg, severity="error")
                logs.write_line(error_msg)

        else:
            self.notify("Ошибка, не команда", severity="error")
            logs.write_line("Discipline set error. IsNotDiscipline")

    def _create_team_from_node(self, node: TreeNode) -> Team:
        return Team(
            id=node.data.id,
            name=node.data.name,
            totalSeats=node.data.totalSeats,
            professors=node.data.professors,
            lesson_id=node.parent.parent.data.id,
        )


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
        selected_items.load_from_file()
        self.notify("Выгружено из disciplines.json")
        logs.write_line("Successfully loaded from file")
        pretty.refresh(layout=True)

    def action_save_disciplines(self) -> None:
        selected_items.save_to_file()
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
