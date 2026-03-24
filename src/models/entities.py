from pydantic import BaseModel, ConfigDict


class Professor(BaseModel):
    name: str
    model_config = ConfigDict(extra="ignore")


class Team(BaseModel):
    id: str
    name: str
    totalSeats: int
    professors: list[Professor]
    model_config = ConfigDict(extra="ignore")


class Cycle(BaseModel):
    id: str
    name: str
    teams: list[Team]
    model_config = ConfigDict(extra="ignore")


class Lesson(BaseModel):
    id: str
    name: str
    model_config = ConfigDict(extra="ignore")


class ModuleGroup(BaseModel):
    id: str
    name: str
    children: list[Lesson]

    model_config = ConfigDict(extra="ignore")
