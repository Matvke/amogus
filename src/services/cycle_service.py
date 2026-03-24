from src.models.entities import Cycle

from .api_client import ApiClient


class CycleService:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client
        self._cycles: dict[str, list[Cycle]] = {}

    def get_cycles(self, lesson_id: str) -> list[Cycle]:
        if lesson_id not in self._cycles:
            cycles = self.api_client.get_cycles(lesson_id)
            self._cycles[lesson_id] = cycles
        return self._cycles[lesson_id]
