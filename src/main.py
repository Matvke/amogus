import argparse

from src.services.api_client import ApiClient
from src.services.cycle_service import CycleService
from src.services.modulegroup_service import ModuleGroupService
from src.services.push_service import PushService
from src.services.select_service import SelectService
from src.services.storage_service import StorageService

from .app import AmogusApp
from .models.settings import Settings


def main():
    parser = argparse.ArgumentParser(
        description="Amogus TUI App - запись на элективы УрФУ"
    )
    parser.add_argument(
        "--env-file", type=str, default=".env", help="Path to .env file (default: .env)"
    )

    args = parser.parse_args()

    try:
        settings = Settings(_env_file=args.env_file)
        api_client = ApiClient(settings)
        cycle_service = CycleService(api_client)
        module_service = ModuleGroupService(api_client)
        select_service = SelectService()
        storage_service = StorageService(settings)
        push_service = PushService(api_client)
        app = AmogusApp(
            cycle_service,
            module_service,
            select_service,
            storage_service,
            push_service,
        )
        app.run()
    except Exception as e:
        print(f"Ошибка при запуске: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
