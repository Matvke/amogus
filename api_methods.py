import requests
from colorama import Fore, Style

from entities import Cycle, Elective
from settings import settings


def get_electives(menu_id: str):
    url = (
        f"https://urfu.modeus.org/learning-path-selection/api/selection/menus/{menu_id}"
    )
    response = requests.get(url=url, headers=settings.get_headers())
    electives_json = response.json()["electives"]["items"]
    electives = [Elective.model_validate(e) for e in electives_json]
    return electives


def get_lessons(menu_id: str, lesson_id: str):
    url = f"https://urfu.modeus.org/learning-path-selection/api/selection/menus/{menu_id}/items/{lesson_id}"
    response = requests.get(url=url, headers=settings.get_headers())
    cycles_json = response.json()["cycles"]
    cycles = [Cycle.model_validate(c) for c in cycles_json]
    return cycles


def post_lesson(
    menu_id,
    lesson_id: str | None = None,
    lecture_id: str | None = None,
    practice_id: str | None = None,
):
    url = f"https://urfu.modeus.org/learning-path-selection/api/menus/{menu_id}/elements/select"
    json = [lesson_id, lecture_id, practice_id]

    response = requests.post(url=url, headers=settings.get_headers(), json=json)
    if response.status_code == 200:
        print(
            f"{Fore.GREEN}[УСПЕХ] Записан на дисциплину {lesson_id}.{Style.RESET_ALL}"
        )
    else:
        print(response.text)
