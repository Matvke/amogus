from src.clients.async_client import AsyncApiClient
from src.models.entities import Cycle


class CycleService:
    def __init__(self, api_client: AsyncApiClient):
        self.api_client = api_client
        self._cycles: dict[str, list[Cycle]] = {}

    async def get_cycles(self, lesson_id: str) -> list[Cycle]:
        if lesson_id not in self._cycles:
            cycles_json = await self.api_client.get_cycles(lesson_id)
            self._cycles[lesson_id] = [Cycle.model_validate(c) for c in cycles_json]
        return self._cycles[lesson_id]
