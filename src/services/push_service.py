import asyncio
from dataclasses import dataclass
from typing import Callable, Optional

from src.clients.async_client import AsyncApiClient
from src.exceptions.api_exc import ApiError


@dataclass
class PushResult:
    lesson_id: str
    success: bool
    error: str | None = None
    text: str | None = None


class PushService:
    def __init__(
        self,
        api_client: AsyncApiClient,
        on_progress: Optional[Callable[[PushResult, int, int], None]] = None,
    ):
        self.api_client = api_client
        self.on_progress = on_progress

    async def push_all(self, selection: dict[str, list[str]]) -> list[PushResult]:
        total = len(selection)
        completed = 0
        results = []
        tasks = [
            self._push_one(lesson_id, self.build_payload(lesson_id, teams_ids))
            for lesson_id, teams_ids in selection.items()
        ]
        for task in asyncio.as_completed(tasks):
            result = await task
            completed += 1
            results.append(result)
            if self.on_progress:
                self.on_progress(result, completed, total)
        return results

    async def _push_one(self, lesson_id: str, payload: list[str]) -> PushResult:
        try:
            response = await self.api_client.post_selection(payload)
            return PushResult(lesson_id=lesson_id, success=True, text=response)
        except ApiError as e:
            return PushResult(
                lesson_id=lesson_id, success=False, error=str(e), text=None
            )

    @staticmethod
    def build_payload(lesson_id: str, teams_ids: list[str]) -> list[str]:
        return [lesson_id, *teams_ids]
