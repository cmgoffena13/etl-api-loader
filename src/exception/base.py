class CustomException(Exception):
    pass


class GrainValidationError(CustomException):
    pass


class AuditFailedError(CustomException):
    pass
