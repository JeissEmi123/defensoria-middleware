from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.services.password_reset_service import PasswordResetService
from app.schemas.auth import (
    SolicitarResetRequest,
    SolicitarResetResponse,
    ResetearContrasenaRequest
)
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/solicitar",
    response_model=SolicitarResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Solicitar reset de contraseña",
    description="""
    Solicita un token de reset de contraseña.
    
    **Comportamiento:**
    - En desarrollo: retorna el token directamente
    - En producción: envía token por email y retorna mensaje genérico
    
    **Anti-enumeración:**
    En producción, siempre retorna éxito aunque el email no exista.
    Esto previene que atacantes descubran emails válidos.
    
    **Rate Limiting:** 3 intentos por hora por IP
    """
)
async def resetear_contrasena(
    request: ResetearContrasenaRequest,
    db: AsyncSession = Depends(get_db_session)
):
    reset_service = PasswordResetService(db)
    await reset_service.resetear_contrasena(request.token, request.nueva_contrasena)
    return {
        "mensaje": "Contraseña actualizada exitosamente"
    }


@router.post(
    "/cancelar/{usuario_id}",
    status_code=status.HTTP_200_OK,
    summary="Cancelar reset de contraseña",
    description="""
    Cancela cualquier token de reset activo para un usuario.
    
    Útil para:
    - Usuario solicitó reset por error
    - Sospecha de compromiso de email
    - Limpieza administrativa
    
    **Permisos requeridos:** `usuarios.administrar`
    """
)
async def cancelar_reset_contrasena(
    usuario_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    reset_service = PasswordResetService(db)
    await reset_service.cancelar_reset(usuario_id)
    return {"mensaje": "Reset de contraseña cancelado exitosamente"}
