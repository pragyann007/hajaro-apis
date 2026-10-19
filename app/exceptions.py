# app/exceptions.py

class ServiceException(Exception):
    """Base exception for all service layer errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class PasswordMismatchException(ServiceException):
    """Raised when confirmation password does not match."""
    pass


class EmailAlreadyExistsException(ServiceException):
    """Raised when registering an email that is already taken."""
    pass


class UserNotFoundException(ServiceException):
    """Raised when a requested user does not exist."""
    pass
