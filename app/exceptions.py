# app/exceptions.py

class ServiceException(Exception):
    """Base exception for all service layer errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class PasswordMismatchException(ServiceException):
    def __init__(self, message: str = "Confirmation password does not match."):
        super().__init__(message=message, status_code=400)


class EmailAlreadyExistsException(ServiceException):
    def __init__(self, message: str = "This email is already taken."):
        super().__init__(message=message, status_code=409)


class UserNotFoundException(ServiceException):
    def __init__(self, message: str = "User not found."):
        super().__init__(message=message, status_code=404) # Fixed to 404!



class LocationNotFoundException(ServiceException):
    def __init__(self, message: str = "Location not found."):
        super().__init__(message=message, status_code=404) # Fixed to 404!

