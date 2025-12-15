"""Custom exceptions for the application."""

from typing import Any


class VLMSException(Exception):
    """Base exception for VLMS application."""

    def __init__(self, message: str, code: str = "VLMS_ERROR", details: Any = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(message)


class NotFoundError(VLMSException):
    """Resource not found exception."""

    def __init__(self, resource: str, identifier: Any = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__(message, code="NOT_FOUND", details={"resource": resource})


class ValidationError(VLMSException):
    """Validation error exception."""

    def __init__(self, message: str, details: Any = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class AuthenticationError(VLMSException):
    """Authentication error exception."""

    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, code="AUTHENTICATION_ERROR")


class AuthorizationError(VLMSException):
    """Authorization error exception."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message, code="AUTHORIZATION_ERROR")


class ConflictError(VLMSException):
    """Conflict error exception (e.g., duplicate entry)."""

    def __init__(self, message: str, details: Any = None):
        super().__init__(message, code="CONFLICT_ERROR", details=details)


class DatabaseError(VLMSException):
    """Database error exception."""

    def __init__(self, message: str = "Database operation failed", details: Any = None):
        super().__init__(message, code="DATABASE_ERROR", details=details)


class ExternalServiceError(VLMSException):
    """External service error exception."""

    def __init__(self, service: str, message: str, details: Any = None):
        super().__init__(
            f"{service}: {message}",
            code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, **(details or {})},
        )
