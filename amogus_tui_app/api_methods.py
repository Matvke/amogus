import requests

from .models.entities import Cycle, Elective
from .models.settings import Settings


def get_electives(settings: Settings):
    url = f"https://urfu.modeus.org/learning-path-selection/api/selection/menus/{settings.menu_id}"
    response = requests.get(url=url, headers=settings.get_headers(), timeout=10)
    if response.status_code == 200:
        settings.user = response.json()["student"]["fullName"]
        electives_json = response.json()["electives"]["items"]
        electives = [Elective.model_validate(e) for e in electives_json]
        return electives
    elif response.status_code == 404:
        raise ValueError("Некорректный menu_id")
    elif response.status_code == 401:
        raise ValueError("Некорректный token")


def get_cycles(
    settings: Settings,
    lesson_id: str,
):
    url = f"https://urfu.modeus.org/learning-path-selection/api/selection/menus/{settings.menu_id}/items/{lesson_id}"
    response = requests.get(url=url, headers=settings.get_headers())
    cycles_json = response.json()["cycles"]
    cycles = [Cycle.model_validate(c) for c in cycles_json]
    return cycles


def post_lesson(settings: Settings, payload: list = None) -> requests.Response:
    url = f"https://urfu.modeus.org/learning-path-selection/api/menus/{settings.menu_id}/elements/select"

    response = requests.post(url=url, headers=settings.get_headers(), json=payload)
    return response
