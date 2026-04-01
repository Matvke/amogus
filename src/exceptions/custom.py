class CustomExc(Exception):
    def __init__(self, message: str, response=None):
        super().__init__(message)
        self.response = response


class IncorrectSchedule(CustomExc): ...


class IncorrectMenuId(CustomExc): ...


class IncorrectToken(CustomExc): ...


class ModeusError(CustomExc): ...


class MenuBlock(CustomExc): ...


class TeamAlreadySelectedError(CustomExc): ...
