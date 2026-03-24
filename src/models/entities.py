from colorama import Fore, Style
from pydantic import BaseModel, ConfigDict


class Professor(BaseModel):
    name: str
    model_config = ConfigDict(extra="ignore")

    def __repr__(self):
        return f"{Fore.CYAN}Преподаватель: {Style.RESET_ALL}{self.name}"


class Team(BaseModel):
    id: str
    name: str
    totalSeats: int
    professors: list[Professor]
    lesson_id: str | None = None
    model_config = ConfigDict(extra="ignore")

    def __repr__(self) -> str:
        return (
            f"{Fore.BLUE}Команда: {Style.RESET_ALL}{self.name} "
            f"({Fore.BLUE}ID:{Style.RESET_ALL} {self.id})"
        )

    def __str__(self):
        return self.__repr__()


class Cycle(BaseModel):
    id: str
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
    id: str
    name: str

    model_config = ConfigDict(extra="ignore")

    def __repr__(self):
        return f"\n    {Fore.MAGENTA}Дисциплина: {Style.RESET_ALL}{self.name} {self.id}"


class ModuleGroup(BaseModel):
    id: str
    name: str
    children: list[Lesson]

    model_config = ConfigDict(extra="ignore")

    def __repr__(self):
        return (
            f"\n{Fore.YELLOW}ID модуля:{Style.RESET_ALL} {self.id}\n"
            f"{Fore.YELLOW}Название модуля: {Style.RESET_ALL}{self.name}\n"
            f"{Fore.YELLOW}Дисциплины: {Style.RESET_ALL}\n{self.children}"
        )
