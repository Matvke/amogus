from httpx import AsyncClient

from src.models.settings import Settings


class AsyncApiClient:
    def __init__(self, settings: Settings, client: AsyncClient):
        self.settings = settings
        self.client = client

    async def get_modules(self):
        url = self.settings.get_electives_url()
        response = await self.client.get(url=url)
        response.raise_for_status()
        if response.status_code == 200:
            electives_json = response.json()["electives"]["items"]
            return electives_json
        elif response.status_code == 404:
            raise ValueError("Некорректный menu_id")
        elif response.status_code == 401:
            raise ValueError("Некорректный token")

    async def get_cycles(self, lesson_id: str):
        url = f"{self.settings.get_cycles_url()}{lesson_id}"
        response = await self.client.get(url=url)
        cycles_json = response.json()["cycles"]
        return cycles_json

    async def post_selection(self, payload: list):
        url = self.settings.get_api_menu_url()
        response = await self.client.post(url=url, json=payload)
        return response
