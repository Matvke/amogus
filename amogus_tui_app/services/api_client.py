import requests
from models.settings import Settings

from amogus_tui_app.models.entities import Cycle, Elective


class ApiClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def get_electives(self):
        url = self.settings.get_electives_url()
        response = requests.get(
            url=url, headers=self.settings.get_headers(), timeout=10
        )
        if response.status_code == 200:
            self.settings.user = response.json()["student"]["fullName"]
            electives_json = response.json()["electives"]["items"]
            electives = [Elective.model_validate(e) for e in electives_json]
            return electives
        elif response.status_code == 404:
            raise ValueError("Некорректный menu_id")
        elif response.status_code == 401:
            raise ValueError("Некорректный token")

    def get_cycles(
        self,
        lesson_id: str,
    ):
        url = f"{self.settings.get_cycles_url}{lesson_id}"
        response = requests.get(url=url, headers=self.settings.get_headers())
        cycles_json = response.json()["cycles"]
        cycles = [Cycle.model_validate(c) for c in cycles_json]
        return cycles

    def post_lesson(self, payload: list = None) -> requests.Response:
        url = self.settings.get_api_menu_url()

        response = requests.post(
            url=url, headers=self.settings.get_headers(), json=payload
        )
        return response
