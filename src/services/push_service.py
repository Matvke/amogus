from src.services.api_client import ApiClient


class PushService:
    def __init__(self, api_client: ApiClient, on_progress):
        self.api_client = ApiClient
        self.on_progress = on_progress

    async def push_all(self, selection: dict):
        pass
