class AppError(Exception):
    """Base application exception."""

    def __init__(self, message: str, code: str = None, context: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.context = context or {}


class RecordNotFoundError(AppError):
    pass


class URLExpiredError(AppError):
    pass


class URLDeletedError(AppError):
    pass


class AliasNotAvailable(AppError):
    pass


class CodeGenerationError(AppError):
    pass


class UserAlreadyExists(AppError):
    pass


class InvalidUser(AppError):
    pass


class ForbiddenUser(AppError):
    pass


class InvalidParameter(AppError):
    pass


class URLDisabledError(AppError):
    pass


class URLAlreadyActive(AppError):
    pass