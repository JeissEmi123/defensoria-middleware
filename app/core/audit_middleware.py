from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from typing import Optional
import time
from datetime import datetime

from app.core.logging import audit_logger, get_logger
from app.database.session import get_db_session
from app.database.models import EventoAuditoria
from app.auth.tokens import TokenManager

logger = get_logger(__name__)
token_manager = TokenManager()


class AuditMiddleware(BaseHTTPMiddleware):
    
    SKIP_PATHS = {
        "/",
        "/health",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico"
    }
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        # Saltar auditoría para endpoints excluidos
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)
        
        # Extraer información de la request
        start_time = time.time()
        usuario_id: Optional[int] = None
        usuario_nombre: Optional[str] = None
        
        # Intentar extraer usuario del token
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            try:
                payload = token_manager.validar_access_token(token)
                usuario_id = payload.get("sub")
                usuario_nombre = payload.get("username")
            except:
                pass  # Token inválido o expirado, seguir sin usuario
        
        # Procesar request
        response = await call_next(request)
        
        # Calcular duración
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Extraer información adicional
        ip_cliente = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Loggear en audit log
        audit_logger.info(
            "request_auditada",
            usuario_id=usuario_id,
            usuario_nombre=usuario_nombre,
            metodo=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duracion_ms=duration_ms,
            ip_cliente=ip_cliente,
            user_agent=user_agent
        )
        
        # Guardar en BD (async, sin bloquear la respuesta)
        if usuario_id:  # Solo guardar si hay usuario autenticado
            try:
                await self._guardar_evento_auditoria(
                    usuario_id=usuario_id,
                    accion=f"{request.method} {request.url.path}",
                    recurso_tipo="endpoint",
                    recurso_id=request.url.path,
                    ip_origen=ip_cliente,
                    user_agent=user_agent,
                    resultado="exito" if 200 <= response.status_code < 400 else "error",
                    detalles={
                        "metodo": request.method,
                        "status_code": response.status_code,
                        "duracion_ms": duration_ms
                    }
                )
            except Exception as e:
                logger.error(
                    "error_guardar_auditoria",
                    error=str(e),
                    usuario_id=usuario_id,
                    endpoint=request.url.path
                )
        
        return response
    
    async def _guardar_evento_auditoria(
        self,
        usuario_id: int,
        accion: str,
        recurso_tipo: str,
        recurso_id: str,
        ip_origen: str,
        user_agent: str,
        resultado: str,
        detalles: dict
    ):
        async for db in get_db_session():
            try:
                evento = EventoAuditoria(
                    usuario_id=usuario_id,
                    accion=accion,
                    recurso_tipo=recurso_tipo,
                    recurso_id=recurso_id,
                    ip_origen=ip_origen,
                    user_agent=user_agent,
                    resultado=resultado,
                    detalles=detalles,
                    fecha_evento=datetime.utcnow()
                )
                db.add(evento)
                await db.commit()
            except Exception as e:
                logger.error("error_insertar_evento_auditoria", error=str(e))
                await db.rollback()
            
            break  # Solo usar la primera sesión
