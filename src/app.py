from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import (
    Footer,
    Header,
    TabbedContent,
    TabPane,
)

from src.services.cycle_service import CycleService
from src.services.modulegroup_service import ModuleGroupService
from src.services.push_service import PushService
from src.services.select_service import SelectService
from src.services.storage_service import StorageService
from src.views.menu_tree import MenuTree


class AmogusApp(App):
    CSS_PATH = "color.tcss"

    BINDINGS = [
        *App.BINDINGS,
        Binding("ctrl+x", "save", "Сохранить команды", show=True),
        Binding("ctrl+z", "load", "Загрузить команды", show=True),
        Binding("ctrl+v", "push", "Записаться", show=True),
    ]

    def __init__(
        self,
        cycle_service: CycleService,
        module_service: ModuleGroupService,
        select_service: SelectService,
        storage_service: StorageService,
        push_service: PushService,
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
        self.push_service.on_progress = self._on_push_progress

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Tree", id="menu-tab"):
                yield MenuTree(
                    label="Меню выбора",
                    cycle_service=self.cycle_service,
                    module_service=self.module_service,
                    select_service=self.select_service,
                )

        yield Header()
        yield Footer()

    def action_save(self):
        try:
            self.storage_service.save_to_file(self.select_service.selected)
            self.notify("Выбор сохранен")
        except Exception as e:
            self.notify(str(e), severity="error")

    def action_load(self):
        try:
            selected = self.storage_service.load_from_file()
            self.select_service.load_selected(selected)
            tree: MenuTree = self.query_one(MenuTree)
            tree.refresh_selection()
            self.notify("Выбор загружен")
        except FileNotFoundError as e:
            self.notify(str(e), severity="error")

    async def action_push(self):
        if self._pushing:
            self.notify("Запись уже выполняется", severity="warning")
            return
        self._pushing = True
        try:
            selection = self.select_service.get_teams_for_api()
            await self.push_service.push_all(selection)
        except Exception as e:
            self.notify(str(e), severity="error")
        finally:
            self._pushing = False

    def _on_push_progress(self, current: int, total: int, error: str = None):
        if error:
            self.notify(f"Ошибка: {error}")
        else:
            self.notify(f"Прогресс: {current}/{total}")
        if current == total:
            self.notify("Запись завершена")
