from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
try:
    from fastapi.responses import ORJSONResponse
    DEFAULT_RESPONSE_CLASS = ORJSONResponse
except ImportError:
    # Si orjson no está disponible, usar JSONResponse con charset UTF-8
    DEFAULT_RESPONSE_CLASS = JSONResponse
from app.config import get_settings
from app.api import auth, rbac, usuarios, password_reset, senales_v2, categoria_observacion
from app.api.detalle_completo import router as detalle_router
from app.core.exceptions import DefensoriaException
from app.core.handlers import register_exception_handlers
from app.core.middleware import (
    SecurityHeadersMiddleware,
    RequestIDMiddleware,
    UserContextMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
    HTTPSRedirectMiddleware,
    TrustedHostMiddleware,
    configure_rate_limiter,
    get_cors_settings,
)
from app.core.audit_middleware import AuditMiddleware
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description='Sistema de autenticación Defensoría',
    redirect_slashes=False,  # Evitar redirecciones 307 que pierden headers
    default_response_class=DEFAULT_RESPONSE_CLASS  # UTF-8 por defecto
)
app.state.settings = settings
register_exception_handlers(app)

cors_settings, allowed_origins, allow_all_origins, allow_credentials = get_cors_settings()

app.add_middleware(
    CORSMiddleware,
    **cors_settings,
)
configure_rate_limiter(app)
app.add_middleware(TrustedHostMiddleware)
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    calls=settings.rate_limit_per_minute,
    period=60,
)
app.add_middleware(AuditMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(UserContextMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

if settings.debug and not settings.is_production:
    # Middleware para debug CORS (solo en desarrollo)
    @app.middleware("http")
    async def debug_cors_middleware(request: Request, call_next):
        sensitive_headers = {
            "authorization",
            "cookie",
            "set-cookie",
            "proxy-authorization",
            "x-api-key",
        }
        redacted_headers = {}
        for header_name, header_value in request.headers.items():
            if header_name.lower() in sensitive_headers:
                redacted_headers[header_name] = "[redacted]"
            else:
                redacted_headers[header_name] = header_value
        origin = request.headers.get("origin", "No Origin")
        method = request.method
        path = request.url.path
        
        logger.debug(
            "cors_debug_request",
            method=method,
            path=path,
            origin=origin,
            headers=redacted_headers
        )
        
        response = await call_next(request)
        
        # Forzar headers CORS manualmente para debug
        origin_permitido = (
            origin
            and (
                origin in allowed_origins
                or allow_all_origins
            )
        )
        if origin_permitido:
            response.headers["access-control-allow-origin"] = origin
            if allow_credentials:
                response.headers["access-control-allow-credentials"] = "true"
            response.headers["access-control-expose-headers"] = "*"
            # Agregar headers anti-cache para evitar problemas de proxy/CDN
            response.headers["cache-control"] = "no-cache, no-store, must-revalidate"
            response.headers["pragma"] = "no-cache"
            response.headers["expires"] = "0"
            logger.debug(
                "cors_debug_headers_added",
                origin=origin
            )
        
        return response

# Middleware para garantizar Content-Type con charset UTF-8
@app.middleware("http")
async def add_utf8_charset(request: Request, call_next):
    response = await call_next(request)
    if "application/json" in response.headers.get("content-type", ""):
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response

# Manejador global de excepciones personalizadas
@app.exception_handler(DefensoriaException)
async def defensoria_exception_handler(request: Request, exc: DefensoriaException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details
        },
        media_type="application/json; charset=utf-8"
    )

# Registrar routers
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(rbac.router, prefix="/rbac", tags=["RBAC"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(password_reset.router, prefix="/password", tags=["Recuperación de Contraseña"])
app.include_router(senales_v2.router, prefix="/api/v2/senales", tags=["Señales v2"])
app.include_router(detalle_router, prefix="/api/v2/senales", tags=["Detalle Completo"])
app.include_router(categoria_observacion.router, prefix="/api/v2/categorias-observacion", tags=["Categorías Observación"])

@app.get('/')
async def root():
    return {'message': 'Defensoria Middleware API', 'version': settings.app_version, 'status': 'operational'}

@app.get('/health')
async def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
