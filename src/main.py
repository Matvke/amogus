import argparse
import asyncio
import logging

import httpx

from src.clients.async_client import AsyncApiClient
from src.services.cycle_service import CycleService
from src.services.modulegroup_service import ModuleGroupService
from src.services.push_service import PushService
from src.services.select_service import SelectService
from src.services.storage_service import StorageService

from .app import AmogusApp
from .models.settings import Settings

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("amogus.log")],
)


class BearerAuth(httpx.Auth):
    def __init__(self, token: str) -> None:
        self.token = token

    def auth_flow(self, request: httpx.Request):
        request.headers["authorization"] = f"Bearer {self.token}"
        yield request


async def async_main():
    parser = argparse.ArgumentParser(
        description="Amogus TUI App - запись на элективы УрФУ"
    )
    parser.add_argument(
        "--env-file", type=str, default=".env", help="Path to .env file (default: .env)"
    )

    args = parser.parse_args()

    settings = Settings(_env_file=args.env_file)
    auth = BearerAuth(settings.token)
    async with httpx.AsyncClient(timeout=10, auth=auth) as http_client:
        api_client = AsyncApiClient(settings, http_client)
        cycle_service = CycleService(api_client)
        module_service = ModuleGroupService(api_client)
        push_service = PushService(api_client)
        select_service = SelectService()
        storage_service = StorageService(settings)

        app = AmogusApp(
            cycle_service,
            module_service,
            select_service,
            storage_service,
            push_service,
            settings,
        )
        await app.run_async()


def main():
    return asyncio.run(async_main())


if __name__ == "__main__":
    asyncio.run(main())
