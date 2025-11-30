class FileValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message, details=None):
        super().__init__(message, code=400, details=details)


class ProcessingError(Exception):
    """Custom exception for processing errors"""
    def __init__(self, message, status_code=500):
        super().__init__()
        self.message =message
        self.status_code = status_code


class RunLimitExceededError(Exception):
    """The limit of simultaneous launches has been exceeded"""
    def __init__(self, message="You already have an active run", details=None):
        super().__init__(message, code=429, details=details)


class SessionExpiredError(Exception):
    """Session expired"""
    def __init__(self, message="Session expired", details=None):
        super().__init__(message, code=401, details=details)


class InvalidTokenError(Exception):
    """Invalid token"""
    def __init__(self, message="Invalid token", details=None):
        super().__init__(message, code=401, details=details)

