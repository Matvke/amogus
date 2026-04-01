import asyncio
import logging
from datetime import datetime
from typing import Awaitable, Callable

logger = logging.getLogger(__name__)


class Timer:
    def __init__(self, pick_time: datetime, on_complete: Callable[[], Awaitable[None]]):
        self.pick_time = pick_time
        self._timer_task = None
        self._on_complete = on_complete
        self._is_stopped = False

    async def set_timer(self):
        """Установить таймер на время."""
        if self._timer_task and not self._timer_task.done():
            logger.debug(
                "Timer start error: pick_time=%s, task=%s, stopped=%s",
                self.pick_time,
                self._timer_task,
                self._is_stopped,
            )
            raise ValueError("Таймер уже запущен")
        now = datetime.now()
        wait_seconds = (self.pick_time - now).total_seconds()
        self._timer_task = asyncio.create_task(self._wait(wait_seconds))
        self._is_stopped = False
        logger.debug(
            "Timer started: pick_time=%s, task=%s, stopped=%s",
            self.pick_time,
            self._timer_task,
            self._is_stopped,
        )

    async def stop_timer(self):
        """Останавливает таймер"""
        if self._timer_task and not self._timer_task.done():
            self._is_stopped = True
            self._timer_task.cancel()
            logger.debug(
                "Timer stopped: pick_time=%s, task=%s, stopped=%s",
                self.pick_time,
                self._timer_task,
                self._is_stopped,
            )
            try:
                await self._timer_task
            except asyncio.CancelledError:
                pass
        self._timer_task = None

    async def _wait(self, seconds: float):
        """Ждать и вызвать функцию"""
        try:
            logger.debug(
                "Timer waiting: pick_time=%s, task=%s, stopped=%s, seconds:%s",
                self.pick_time,
                self._timer_task,
                self._is_stopped,
                seconds,
            )
            await asyncio.sleep(seconds)
            if not self._is_stopped:
                await self._on_complete()
        except asyncio.CancelledError:
            pass
        finally:
            self._timer_task = None

    def is_active(self) -> bool:
        """Проверить, активен ли таймер."""
        return self._timer_task is not None and not self._timer_task.done()
