import argparse

from .settings import Settings
from .tui_app import AmogusApp

__version__ = "0.1.0"
__all__ = ["AmogusApp"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env-file", type=str, default=".env", help="Path to .env file"
    )
    args = parser.parse_args()

    settings = Settings(_env_file=args.env_file)
    app = AmogusApp(settings)
    app.run()
