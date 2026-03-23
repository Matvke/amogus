from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    token: str
    menu_id: str
    pick_time: str
    user: None | str = None
    base_selection_url: str = (
        "https://urfu.modeus.org/learning-path-selection/api/selection/menus/"
    )
    base_api_url: str = "https://urfu.modeus.org/learning-path-selection/api/menus/"

    electives_endpoint: str = ""
    cycles_endpoint: str = "items/"
    select_endpoint: str = "elements/select/"

    def get_headers(self) -> dict:
        return {
            "accept": "application/json, text/plain, */*",
            "accept-language": "ru-RU",
            "authorization": f"Bearer {self.token}",
            "content-type": "application/json",
            "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }

    def get_electives_url(self) -> str:
        return f"{self.base_selection_url}{self.menu_id}/{self.electives_endpoint}"

    def get_cycles_url(self) -> str:
        return f"{self.base_selection_url}{self.menu_id}/{self.cycles_endpoint}"

    def get_api_menu_url(self) -> str:
        return f"{self.base_api_url}{self.menu_id}/{self.select_endpoint}"
