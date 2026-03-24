from src.models.entities import Cycle, Team

from .api_client import ApiClient


class CycleService:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client
        self._cycles: dict[str, list[Cycle]] = {}

    def get_cycles(self, lesson_id: str) -> list[Cycle]:
        if lesson_id not in self._cycles:
            cycles = self.api_client.get_cycles(lesson_id)
            for cycle in cycles:
                cycle.teams = [
                    Team(
                        id=team.id,
                        name=team.name,
                        totalSeats=team.totalSeats,
                        professors=team.professors,
                        lesson_id=lesson_id,
                    )
                    for team in cycle.teams
                ]
        self._cycles[lesson_id] = cycles
        return self._cycles[lesson_id]
