from fastapi import status


class SubFlowError(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "subflow_error"

    def __init__(
        self,
        message: str,
    ) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(SubFlowError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class ConflictError(SubFlowError):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"


class AuthenticationError(SubFlowError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "authentication_error"


class AuthorizationError(SubFlowError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "authorization_error"
