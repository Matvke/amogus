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
from src.services.select_service import SelectService
from src.services.storage_service import StorageService
from src.views.menu_tree import MenuTree


class AmogusApp(App):
    CSS_PATH = "color.tcss"

    BINDINGS = [
        *App.BINDINGS,
        Binding("ctrl+x", "save_disciplines", "Сохранить команды", show=True),
        Binding("ctrl+z", "load_disciplines", "Загрузить команды", show=True),
        Binding("ctrl+v", "push_disciplines", "Записаться", show=True),
    ]

    def __init__(
        self,
        cycle_service: CycleService,
        module_service: ModuleGroupService,
        select_service: SelectService,
        storage_service: StorageService,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.cycle_service = cycle_service
        self.module_service = module_service
        self.select_service = select_service
        self.storage_service = storage_service

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Tree", id="menu-tab"):
                yield MenuTree(
                    label="Меню выбора",
                    cycle_service=self.cycle_service,
                    module_service=self.module_service,
                    select_service=self.select_service,
                    storage_service=self.storage_service,
                )

        yield Header()
        yield Footer()
