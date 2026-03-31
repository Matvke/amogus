import asyncio
from datetime import datetime
from typing import Coroutine


class Timer:
    def __init__(self, pick_time: datetime, on_complete: Coroutine):
        self.pick_time = pick_time
        self._timer_task = None
        self._on_complete = on_complete

    async def set_timer(self):
        """Установить таймер на время."""
        if self._timer_task and not self._timer_task.done():
            raise ValueError("Таймер уже запущен")
        now = datetime.now()
        wait_seconds = (self.pick_time - now).total_seconds()
        self._timer_task = asyncio.create_task(self._wait(wait_seconds))

    async def stop_timer(self):
        if self._timer_task and not self._timer_task.done():
            self._timer_task.cancel()

    async def _wait(self, seconds: float):
        """Ждать и вызвать функцию"""
        try:
            await asyncio.sleep(seconds)
            await self._on_complete()
        except asyncio.CancelledError:
            raise
