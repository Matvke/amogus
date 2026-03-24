import asyncio
from typing import Callable, Optional

from src.services.api_client import ApiClient


class PushService:
    def __init__(
        self,
        api_client: ApiClient,
        on_progress: Optional[Callable[[str, int, int], None]] = None,
    ):
        self.api_client = api_client
        self.on_progress = on_progress

    async def push_all(self, selection: dict):
        """Отправить все выбранные предметы"""
        total = len(selection)
        completed = 0
        errors = 0
        tasks = []
        for lesson_id, team_ids in selection.items():
            payload = [lesson_id] + team_ids
            tasks.append(asyncio.create_task(self._push_one(payload)))
        for coro in asyncio.as_completed(tasks):
            success, error = await coro
            completed += 1
            if not success:
                errors += 1
                if self.on_progress:
                    self.on_progress(completed, total, error=error)
            else:
                if self.on_progress:
                    self.on_progress(completed, total)
        if self.on_progress:
            if errors == 0:
                self.on_progress(total, total, error=None)
            else:
                self.on_progress(total, total, error=f"Завершено с {errors} ошибками")

    async def _push_one(self, payload):
        loop = asyncio.get_running_loop()
        try:
            response = await loop.run_in_executor(
                None, self.api_client.post_selection, payload
            )
            if response.ok:
                return True, None
            else:
                return False, f"Ошибка {response.status_code}: {response.text}"
        except Exception as e:
            return False, str(e)
