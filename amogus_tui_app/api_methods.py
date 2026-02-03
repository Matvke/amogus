import requests

from .entities import Cycle, Elective
from .settings import settings


def get_electives(menu_id: str):
    url = (
        f"https://urfu.modeus.org/learning-path-selection/api/selection/menus/{menu_id}"
    )
    response = requests.get(url=url, headers=settings.get_headers(), timeout=30)
    if response.status_code == 200:
        electives_json = response.json()["electives"]["items"]
        electives = [Elective.model_validate(e) for e in electives_json]
        return electives
    if response.status_code == 404:
        raise ValueError("Некорректный menu_id")
    if response.status_code == 401:
        raise ValueError("Некорректный token")


def get_cycles(menu_id: str, lesson_id: str):
    url = f"https://urfu.modeus.org/learning-path-selection/api/selection/menus/{menu_id}/items/{lesson_id}"
    response = requests.get(url=url, headers=settings.get_headers())
    cycles_json = response.json()["cycles"]
    cycles = [Cycle.model_validate(c) for c in cycles_json]
    return cycles


def post_lesson(menu_id, payload: list = None) -> requests.Response:
    url = f"https://urfu.modeus.org/learning-path-selection/api/menus/{menu_id}/elements/select"

    response = requests.post(url=url, headers=settings.get_headers(), json=payload)
    return response
    # if response.status_code == 200:
    #     print(
    #         f"{Fore.GREEN}[УСПЕХ] Записан на дисциплину {payload[0]}.{Style.RESET_ALL}"
    #     )
    # else:
    #     print(response.text)
