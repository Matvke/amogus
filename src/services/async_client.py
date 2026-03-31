from httpx import AsyncClient, HTTPStatusError

from src.exceptions.api_exc import (
    IncorrectMenuId,
    IncorrectSchedule,
    IncorrectToken,
    MenuBlock,
    ModeusError,
)
from src.models.settings import Settings


class AsyncApiClient:
    def __init__(self, settings: Settings, client: AsyncClient):
        self.settings = settings
        self.client = client

    async def _request(self, url: str, method: str, payload: list[str] | None = None):
        try:
            if method == "GET":
                response = await self.client.get(url=url)
                response.raise_for_status()
                return response
            elif method == "POST":
                response = await self.client.post(url=url, json=payload)
                response.raise_for_status()
                return response
        except HTTPStatusError as e:
            status = e.response.status_code
            if status == 404:
                raise IncorrectMenuId(
                    "Некорректный menu_id", response=e.response
                ) from e
            elif status == 401:
                raise IncorrectToken("Некорректный token", response=e.response) from e
            elif 500 <= status <= 599:
                raise ModeusError("Упал модеус", response=e.response) from e
            elif status == 400:
                raise IncorrectSchedule(
                    "Неправильно выбраны предметы/Конфликт в расписании.",
                    response=e.response,
                ) from e
            elif status == 409:
                raise MenuBlock(
                    "Меню выбора заблокировано. Выбор невозможен.",
                    response=e.response,
                ) from e
            else:
                raise

    async def get_modules(self):
        url = self.settings.get_electives_url()
        response = await self._request(url, method="GET")
        electives_json = response.json()["electives"]["items"]
        return electives_json

    async def get_cycles(self, lesson_id: str):
        url = self.settings.get_cycles_url(lesson_id)
        response = await self._request(url=url, method="GET")
        cycles_json = response.json()["cycles"]
        return cycles_json

    async def post_selection(self, payload: list[str]):
        url = self.settings.get_api_menu_url()
        response = await self._request(url=url, payload=payload, method="POST")
        return response.json()
