class SubFlowError(Exception):
    status_code = 400
    code = "subflow_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(SubFlowError):
    status_code = 404
    code = "not_found"


class ConflictError(SubFlowError):
    status_code = 409
    code = "conflict"


class AuthenticationError(SubFlowError):
    status_code = 401
    code = "authentication_failed"


class AuthorizationError(SubFlowError):
    status_code = 403
    code = "forbidden"
