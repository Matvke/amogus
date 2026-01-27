from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    token: str
    menu_id: str

    model_config = SettingsConfigDict(env_file=".env")

    def get_headers(self):
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


settings = Settings()
