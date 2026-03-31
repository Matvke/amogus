class ApiError(Exception):
    def __init__(self, message: str, response=None):
        super().__init__(message)
        self.response = response


class IncorrectSchedule(ApiError): ...


class IncorrectMenuId(ApiError): ...


class IncorrectToken(ApiError): ...


class ModeusError(ApiError): ...


class MenuBlock(ApiError): ...
