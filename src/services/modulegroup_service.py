import logging

from src.clients.async_client import AsyncApiClient
from src.models.entities import ModuleGroup

logger = logging.getLogger(__name__)


class ModuleGroupService:
    def __init__(self, api_client: AsyncApiClient):
        self.api_client = api_client
        self._modules: list[ModuleGroup] | None = None

    async def get_modules(self) -> list[ModuleGroup]:
        if self._modules is None:
            electives_json = await self.api_client.get_modules()
            self._modules = [ModuleGroup.model_validate(e) for e in electives_json]
            logger.debug(
                "Modules get: count=%s",
                len(self._modules),
            )
        return self._modules
