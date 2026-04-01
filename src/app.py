from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Static,
    TabbedContent,
    TabPane,
)

from src.models.settings import Settings
from src.services.cycle_service import CycleService
from src.services.modulegroup_service import ModuleGroupService
from src.services.push_service import PushResult, PushService
from src.services.select_service import SelectService
from src.services.storage_service import StorageService
from src.services.timer_service import Timer
from src.views.menu_tree import MenuTree


class AmogusApp(App):
    CSS_PATH = "color.tcss"

    BINDINGS = [
        *App.BINDINGS,
        Binding("ctrl+x", "save", "Сохранить команды", show=True),
        Binding("ctrl+z", "load", "Загрузить команды", show=True),
        Binding("ctrl+v", "push", "Записаться", show=True),
        Binding("ctrl+t", "set_timer", "Поставить таймер", show=True),
    ]

    def __init__(
        self,
        cycle_service: CycleService,
        module_service: ModuleGroupService,
        select_service: SelectService,
        storage_service: StorageService,
        push_service: PushService,
        settings: Settings,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.cycle_service = cycle_service
        self.module_service = module_service
        self.select_service = select_service
        self.storage_service = storage_service
        self.push_service = push_service
        self._pushing = False
        self.settings = settings
        self.push_service.on_progress = self._on_push_progress
        self._timer = None

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Меню выбора", id="menu-tab"):
                yield MenuTree(
                    label="Меню выбора",
                    cycle_service=self.cycle_service,
                    module_service=self.module_service,
                    select_service=self.select_service,
                )
                yield Static("Таймер: --:--:--", id="timer")
            with TabPane("Результаты записи", id="table-tab"):
                yield DataTable(id="push_table")

        yield Header()
        yield Footer()

    def on_mount(self):
        self.push_table = self.query_one("#push_table", DataTable)
        self.push_table.add_columns("Lesson ID", "Status", "Message")

    def action_save(self):
        try:
            self.storage_service.save_to_file(self.select_service.selected)
            self.notify("Выбор сохранен")
        except Exception as e:
            self.notify(str(e), severity="error")

    def action_load(self):
        try:
            selected = self.storage_service.load_from_file()
            self.select_service.selected = selected
            tree: MenuTree = self.query_one(MenuTree)
            tree.refresh_selection()
            self.notify("Выбор загружен")
        except FileNotFoundError as e:
            self.notify(str(e), severity="error")

    async def action_push(self):
        self._push_disciplines()

    @work(exclusive=True)
    async def _push_disciplines(self):
        if not self.select_service.get_teams_for_api():
            self.notify("Нет выбранных предметов", severity="warning")
            return
        if self._pushing:
            self.notify("Запись уже выполняется", severity="warning")
            return
        self.notify("Выполняю запись", severity="information")
        self._pushing = True
        try:
            selection = self.select_service.get_teams_for_api()
            await self.push_service.push_all(selection)
        except Exception as e:
            self.notify(str(e), severity="error")
        finally:
            self._pushing = False
            self.notify("Запись завершена", severity="information")

    def _on_push_progress(self, result: PushResult, completed: int, total: int):
        status = "✅ OK" if result.success else "❌ ERR"
        message = result.error or result.text or ""
        self.push_table.add_row(result.lesson_id, status, message)

    async def action_set_timer(self):
        """Установить таймер на время, указанное в settings.pick_time."""
        if not self.select_service.get_teams_for_api():
            self.notify("Нет выбранных предметов", severity="warning")
            return

        timer_widget = self.query_one("#timer", Static)
        if self._timer is None:
            self._timer = Timer(
                pick_time=self.settings.pick_time, on_complete=self.action_push
            )
            await self._timer.set_timer()
            self.notify(
                f"Запуск таймера на {self.settings.pick_time}", severity="warning"
            )
            timer_widget.update(f"Таймер: {self.settings.pick_time}")
        else:
            self.notify("Останавливаю таймер")
            await self._timer.stop_timer()
            self._timer = None
            timer_widget.update("Таймер: --:--:--")
