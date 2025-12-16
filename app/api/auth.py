from fastapi import APIRouter, Depends, status, Request, Header, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.services.auth_service import AuthService
from app.schemas.auth import (
    TokenResponse, TokenRefreshRequest, ValidateTokenResponse,
    UsuarioResponse, UsuarioActual, LoginRequest
)
from app.core.dependencies import get_current_user, get_current_active_superuser
from app.core.logging import get_logger
from app.core.middleware import limiter
from app.core.exceptions import AuthenticationError

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Autenticar usuario",
    description="Autentica un usuario usando múltiples proveedores. Retorna access_token y refresh_token para uso en requests subsecuentes."
)
async def login(
    login_data: LoginRequest = Body(...),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Endpoint de login para autenticación de usuario.
    """
    auth_service = AuthService(db)
    token_response = await auth_service.autenticar_usuario(
        nombre_usuario=login_data.nombre_usuario,
        contrasena=login_data.contrasena
    )
    return token_response


@router.get(
    "/me",
    response_model=UsuarioActual,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario actual",
    description="Obtiene la información del usuario autenticado actual basado en el token JWT."
)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """
    Obtiene la información del usuario actual autenticado.
    """
    return current_user


@router.post(
    "/validate",
    response_model=ValidateTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Validar token JWT",
    description="Valida un token JWT enviado en el header Authorization. Útil para servicios externos que necesitan verificar tokens."
)
async def validate_token(
    authorization: str = Header(..., description="Bearer token JWT"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Valida el token JWT enviado en el header Authorization.
    """
    if not authorization.startswith("Bearer "):
        return ValidateTokenResponse(valido=False, razon="Formato de token inválido")
    token = authorization.split(" ", 1)[1]
    auth_service = AuthService(db)
    usuario = await auth_service.obtener_usuario_desde_token(token)
    if not usuario:
        return ValidateTokenResponse(valido=False, razon="Token inválido o expirado")
    return ValidateTokenResponse(valido=True, usuario=usuario)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refrescar token",
    description="Refresca un access token usando el refresh token"
)
async def refresh_token(
    refresh_data: TokenRefreshRequest = Body(...),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Refresca el access token usando el refresh token.
    """
    auth_service = AuthService(db)
    token_response = await auth_service.refrescar_token(refresh_data.refresh_token)
    return token_response


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión",
    description="Cierra la sesión actual invalidando el token"
)
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """
    Cierra la sesión del usuario actual.
    """
    auth_header = request.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None
    
    if token:
        auth_service = AuthService(db)
        await auth_service.cerrar_sesion(token)
    
    return {"message": "Sesión cerrada exitosamente"}