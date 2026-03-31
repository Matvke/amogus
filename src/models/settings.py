import datetime

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    token: str
    menu_id: str
    pick_time: datetime.datetime
    base_selection_url: str = (
        "https://urfu.modeus.org/learning-path-selection/api/selection/menus/"
    )
    base_api_url: str = "https://urfu.modeus.org/learning-path-selection/api/menus/"

    electives_endpoint: str = ""
    cycles_endpoint: str = "items/"
    select_endpoint: str = "elements/select/"

    file_name: str = "disciplines.json"

    def get_electives_url(self) -> str:
        return f"{self.base_selection_url}{self.menu_id}/{self.electives_endpoint}/"

    def get_cycles_url(self, lesson_id: str) -> str:
        return f"{self.base_selection_url}{self.menu_id}/{self.cycles_endpoint}/{lesson_id}"

    def get_api_menu_url(self) -> str:
        return f"{self.base_api_url}{self.menu_id}/{self.select_endpoint}/"
