from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Callable
import time
import uuid

from app.config import settings
from app.core.logging import get_logger, request_id_var
from app.core.exceptions import RateLimitError

logger = get_logger(__name__)

# Inicializar rate limiter
limiter = Limiter(key_func=get_remote_address)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        if settings.enable_security_headers:
            # Prevenir clickjacking
            response.headers["X-Frame-Options"] = "DENY"
            
            # Prevenir MIME sniffing
            response.headers["X-Content-Type-Options"] = "nosniff"
            
            # XSS Protection
            response.headers["X-XSS-Protection"] = "1; mode=block"
            
            # Strict Transport Security (HSTS) - Solo con HTTPS
            if settings.is_production:
                response.headers["Strict-Transport-Security"] = \
                    "max-age=31536000; includeSubDomains"
            
            # Content Security Policy
            response.headers["Content-Security-Policy"] = \
                "default-src 'self'; script-src 'self' 'unsafe-inline'; " \
                "style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
            
            # Referrer Policy
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            
            # Permissions Policy
            response.headers["Permissions-Policy"] = \
                "geolocation=(), microphone=(), camera=()"
        
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generar o usar Request ID existente
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Establecer en contexto para logging
        request_id_var.set(request_id)
        
        # Procesar request
        response = await call_next(request)
        
        # Agregar Request ID a response
        response.headers["X-Request-ID"] = request_id
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Extraer información del request
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        user_agent = request.headers.get("user-agent", "unknown")
        
        logger.info(
            "request_iniciado",
            method=method,
            path=path,
            ip=client_ip,
            user_agent=user_agent
        )
        
        try:
            response = await call_next(request)
            
            # Calcular tiempo de procesamiento
            process_time = time.time() - start_time
            
            # Agregar header de timing
            response.headers["X-Process-Time"] = str(process_time)
            
            logger.info(
                "request_completado",
                method=method,
                path=path,
                status_code=response.status_code,
                process_time=process_time
            )
            
            return response
        
        except Exception as e:
            process_time = time.time() - start_time
            
            logger.error(
                "request_error",
                method=method,
                path=path,
                error=str(e),
                process_time=process_time
            )
            
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app, calls: int = 60, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.is_production:
            # Deshabilitar rate limiting en desarrollo
            return await call_next(request)
        
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Limpiar requests antiguos
        self.requests = {
            ip: times for ip, times in self.requests.items()
            if any(t > current_time - self.period for t in times)
        }
        
        # Obtener requests del cliente
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Filtrar requests dentro del período
        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if t > current_time - self.period
        ]
        
        # Verificar límite
        if len(self.requests[client_ip]) >= self.calls:
            logger.warning(
                "rate_limit_excedido",
                ip=client_ip,
                path=request.url.path,
                requests=len(self.requests[client_ip])
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "rate_limit",
                    "message": "Demasiadas solicitudes. Intente más tarde.",
                    "retry_after": self.period
                }
            )
        
        # Registrar request
        self.requests[client_ip].append(current_time)
        
        return await call_next(request)


def get_cors_middleware():
    return CORSMiddleware(
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-CSRF-Token"
        ],
        expose_headers=["X-Request-ID", "X-Process-Time"],
        max_age=3600,  # Cache preflight por 1 hora
    )


def configure_rate_limiter(app):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    return limiter


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if settings.enable_https_redirect and settings.is_production:
            if request.url.scheme != "https":
                # Construir URL HTTPS
                https_url = request.url.replace(scheme="https")
                
                logger.info(
                    "https_redirect",
                    from_url=str(request.url),
                    to_url=str(https_url)
                )
                
                return Response(
                    status_code=status.HTTP_308_PERMANENT_REDIRECT,
                    headers={"Location": str(https_url)}
                )
        
        return await call_next(request)


class TrustedHostMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if settings.is_production:
            host = request.headers.get("host", "").split(":")[0]
            
            if host and host not in settings.allowed_hosts:
                logger.warning(
                    "host_no_permitido",
                    host=host,
                    allowed=settings.allowed_hosts
                )
                
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "error": "invalid_host",
                        "message": "Host no permitido"
                    }
                )
        
        return await call_next(request)
