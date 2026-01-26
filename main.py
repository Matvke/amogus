import requests
from colorama import Fore, Style
from pydantic import UUID4, BaseModel, ConfigDict


class Professor(BaseModel):
    name: str
    model_config = ConfigDict(extra="ignore")

    def __repr__(self):
        return f"{Fore.CYAN}Преподаватель: {Style.RESET_ALL}{self.name}"


class Team(BaseModel):
    id: UUID4
    name: str
    totalSeats: int
    professors: list[Professor]

    model_config = ConfigDict(extra="ignore")

    def __repr__(self):
        return (
            f"\n{Fore.BLUE}Команда: {Style.RESET_ALL}{self.name} "
            f"({Fore.BLUE}ID:{Style.RESET_ALL} {self.id}, "
            f"{Fore.BLUE}Мест:{Style.RESET_ALL} {self.totalSeats}, "
            f"{Fore.BLUE}Преподаватели:{Style.RESET_ALL} [{self.professors}])"
        )


class Cycle(BaseModel):
    id: UUID4
    name: str
    teams: list[Team]
    model_config = ConfigDict(extra="ignore")

    def __repr__(self):
        return (
            f"\n{Fore.GREEN}ID курса: {Style.RESET_ALL}{self.id}\n"
            f"{Fore.GREEN}Название курса: {Style.RESET_ALL}{self.name}\n"
            f"{Fore.GREEN}Команды: {Style.RESET_ALL}{self.teams}\n"
        )


class Lesson(BaseModel):
    id: UUID4
    name: str

    model_config = ConfigDict(extra="ignore")

    def __repr__(self):
        return f"\n    {Fore.MAGENTA}Дисциплина: {Style.RESET_ALL}{self.name} {self.id}"


class Elective(BaseModel):
    id: UUID4
    name: str
    children: list[Lesson]

    model_config = ConfigDict(extra="ignore")

    def __repr__(self):
        return (
            f"\n{Fore.YELLOW}ID модуля:{Style.RESET_ALL} {self.id}\n"
            f"{Fore.YELLOW}Название модуля: {Style.RESET_ALL}{self.name}\n"
            f"{Fore.YELLOW}Дисциплины: {Style.RESET_ALL}\n{self.children}"
        )


def get_electives(menu_id: str, headers):
    url = (
        f"https://urfu.modeus.org/learning-path-selection/api/selection/menus/{menu_id}"
    )
    response = requests.get(url=url, headers=headers)
    electives_json = response.json()["electives"]["items"]
    electives = [Elective.model_validate(e) for e in electives_json]
    print(electives)


def get_lesson(menu_id: str, elective_id: str, headers):
    url = f"https://urfu.modeus.org/learning-path-selection/api/selection/menus/{menu_id}/items/{elective_id}"
    response = requests.get(url=url, headers=headers)
    cycles_json = response.json()["cycles"]
    cycles = [Cycle.model_validate(c) for c in cycles_json]
    print(cycles)


def post_lesson(
    headers,
    menu_id,
    lesson_id: str | None = None,
    lecture_id: str | None = None,
    practice_id: str | None = None,
):
    url = f"https://urfu.modeus.org/learning-path-selection/api/menus/{menu_id}/elements/select"
    json = [lesson_id, lecture_id, practice_id]

    response = requests.post(url=url, headers=headers, json=json)
    if response.status_code == 200:
        print(
            f"{Fore.GREEN}[УСПЕХ] Записан на дисциплину {lesson_id}.{Style.RESET_ALL}"
        )
    else:
        print(response.text)


def main():
    # token = input("Введите JWT токен")
    # menu_id = input("Введите ID меню")
    token = "eyJ4NXQiOiJORGhpTkROalpHTmpORFl6WXpJMVpUQmhZakUxTUdOaE1EQTJOelk0TTJKa1pEQTVaREptTXciLCJraWQiOiJkMGVjNTE0YTMyYjZmODhjMGFiZDEyYTI4NDA2OTliZGQzZGViYTlkIiwiYWxnIjoiUlMyNTYifQ.eyJhdF9oYXNoIjoiN2ZQWVV1Q0xKVUg2bmVtMjdSd21fZyIsInN1YiI6IjU3MzMyODE2LTdhMjItNGJjMi04MjM4LWNlNTRiYTI1NTZkMyIsImF1ZCI6WyIzQ3VGM0ZzTnlSTGlGVmowSWwyZkl1amZ0dzBhIl0sImF6cCI6IjNDdUYzRnNOeVJMaUZWajBJbDJmSXVqZnR3MGEiLCJFeHRlcm5hbFBlcnNvbklkIjoiOWJkZTY1YzEtZGZkMy00OTI1LTk5YTQtNGNlYzEyNTczNWY3IiwiaXNzIjoiaHR0cHM6XC9cL3VyZnUtYXV0aC5tb2RldXMub3JnXC9vYXV0aDJcL3Rva2VuIiwicHJlZmVycmVkX3VzZXJuYW1lIjoi0JHRg9GC0L7Qu9C40L0g0JzQsNGC0LLQtdC5INCS0LjRgtCw0LvRjNC10LLQuNGHIiwiZXhwIjoxNzY5NTEzNjM2LCJub25jZSI6IlIyOXdZMXBEYzA1RU0xQmpSalJpWWtSNVZtbG1jVFJFYTBOWlVsVkJkbW90TWtzd1dqUmllbWQzUm5oeSIsImlhdCI6MTc2OTQyNzIzNiwicGVyc29uX2lkIjoiYmEyNGEzOWItNzdkZC00OTQ3LWFjZTUtZWZhNDE0OGEwOGM5In0.R5OHFU9al_8LNaHLlN2MkW4mKajtLe7AfD9Tnw43D7wD4aQDlhVB5PnNuH7B3K36tenX50QszFFDYJXAB_hwUEDpwJJEZN1KjzsuZjZV_YV1TsccHYtG0lJw9D0ZitniVSTxDx59z9HIl6whK38YE2dmmIAec1LUTFXzWZ_gQeEsOjcjXdKtZfEJFYyewJY1cTzDC_l_B0Ehg3i50bvaQl5LUoxWhaQxXMXwzS0rRsrD8GsLvrzJhWCrDWecrqojJma7tpiisnGZinP22y9dP6gVIdAY2SVWzLnD_t4aeHbuZeTIXhdVU2UwH02fmp3pNSYeG3FkHnA7RGjNnWe6aQ"
    menu_id = "1a973e20-232c-4328-8329-77afe804f49e"
    lesson_id = "f76c3547-8942-4f53-a199-450ef05423aa"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ru-RU",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }
    # get_electives(menu_id, headers)
    # get_lesson(menu_id, lesson_id, headers)
    post_lesson(
        headers,
        menu_id,
        lesson_id,
        "10508468-2628-47cf-99d8-a216a7fc3851",
        "7a4477bc-cfcd-4c69-84dd-461240ab53bc",
    )


if __name__ == "__main__":
    main()
