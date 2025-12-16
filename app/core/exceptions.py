from typing import Any, Dict, Optional
from fastapi import status


class DefensoriaException(Exception):
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(DefensoriaException):
    def __init__(self, message: str = "Credenciales inválidas", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="AUTH_001",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class AuthorizationError(DefensoriaException):
    def __init__(self, message: str = "No autorizado", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="AUTH_002",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class TokenExpiredError(DefensoriaException):
    def __init__(self, message: str = "Token expirado", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="AUTH_003",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class InvalidTokenError(DefensoriaException):
    def __init__(self, message: str = "Token inválido", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="AUTH_004",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class UserNotFoundError(DefensoriaException):
    def __init__(self, message: str = "Usuario no encontrado", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="USER_001",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class UserInactiveError(DefensoriaException):
    def __init__(self, message: str = "Usuario inactivo", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="USER_002",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class ValidationError(DefensoriaException):
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="VAL_001",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class DatabaseError(DefensoriaException):
    def __init__(self, message: str = "Error de base de datos", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="DB_001",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ExternalServiceError(DefensoriaException):
    def __init__(self, message: str, service: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="EXT_001",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"service": service, **(details or {})}
        )


class RateLimitError(DefensoriaException):
    def __init__(self, message: str = "Demasiadas solicitudes", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="RATE_001",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


class ConfigurationError(DefensoriaException):
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="CONFIG_001",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )
