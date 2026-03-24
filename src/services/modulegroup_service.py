from src.models.entities import ModuleGroup

from .api_client import ApiClient


class ModuleGroupService:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client
        self._modules: list[ModuleGroup] | None = None

    def get_modules(self) -> list[ModuleGroup]:
        if self._modules is None:
            self._modules = self.api_client.get_modules()
        return self._modules
