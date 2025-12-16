from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from typing import Union

from app.core.exceptions import DefensoriaException
from app.core.logging import get_logger

logger = get_logger(__name__)


async def defensoria_exception_handler(
    request: Request,
    exc: DefensoriaException
) -> JSONResponse:
    logger.warning(
        "excepcion_manejada",
        error_code=exc.error_code,
        message=exc.message,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        "error_validacion",
        errors=errors,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Error de validación en los datos enviados",
            "details": {"errors": errors}
        }
    )


async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    logger.error(
        "error_base_datos",
        error=str(exc),
        path=request.url.path,
        method=request.method
    )
    
    # En producción, no exponer detalles del error
    if not hasattr(request.app.state, "settings") or \
       request.app.state.settings.is_production:
        message = "Error interno del servidor"
        details = {}
    else:
        message = str(exc)
        details = {"type": type(exc).__name__}
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "DATABASE_ERROR",
            "message": message,
            "details": details
        }
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    logger.error(
        "excepcion_no_manejada",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        exc_info=True
    )
    
    # En producción, no exponer detalles del error
    if not hasattr(request.app.state, "settings") or \
       request.app.state.settings.is_production:
        message = "Error interno del servidor"
        details = {}
    else:
        message = str(exc)
        details = {"type": type(exc).__name__}
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_ERROR",
            "message": message,
            "details": details
        }
    )


def register_exception_handlers(app):
    app.add_exception_handler(DefensoriaException, defensoria_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("exception_handlers_registrados")
