import argparse

from .app import AmogusApp
from .models.settings import Settings


def main():
    parser = argparse.ArgumentParser(
        description="Amogus TUI App - запись на элективы УрФУ"
    )
    parser.add_argument(
        "--env-file", type=str, default=".env", help="Path to .env file (default: .env)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__import__('amogus_tui_app').__version__}",
    )

    args = parser.parse_args()

    try:
        settings = Settings(_env_file=args.env_file)
        app = AmogusApp(settings)
        app.run()
    except Exception as e:
        print(f"Ошибка при запуске: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
