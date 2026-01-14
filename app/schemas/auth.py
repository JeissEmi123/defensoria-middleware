from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TipoAutenticacion(str, Enum):
    local = "local"
    ldap = "ldap"
    azure_ad = "azure_ad"

class LoginRequest(BaseModel):
    nombre_usuario: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario", alias="username")
    contrasena: str = Field(..., min_length=8, description="Contraseña", alias="password")
    model_config = {"populate_by_name": True}
    @field_validator("nombre_usuario")
    @classmethod
    def validar_nombre_usuario(cls, v):
        import re
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Nombre de usuario inválido")
        return v.lower()

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Token de acceso JWT")
    refresh_token: str = Field(..., description="Token de refresco")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")

class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Token de refresco")

class UsuarioBase(BaseModel):
    nombre_usuario: str = Field(..., description="Nombre de usuario")
    email: Optional[EmailStr] = Field(None, description="Email")
    nombre_completo: Optional[str] = Field(None, description="Nombre completo")
    activo: bool = Field(default=True, description="Usuario activo")

class UsuarioCreate(UsuarioBase):
    contrasena: str = Field(..., min_length=12, description="Contraseña")
    es_superusuario: bool = Field(default=False, description="Es superusuario")

class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nombre_completo: Optional[str] = None
    activo: Optional[bool] = None
    es_superusuario: Optional[bool] = None

class UsuarioResponse(UsuarioBase):
    id: int
    es_superusuario: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    ultimo_acceso: Optional[datetime]
    tipo_autenticacion: TipoAutenticacion
    model_config = {"from_attributes": True}


class UsuarioActual(BaseModel):
    id: int
    nombre_usuario: str
    email: Optional[str]
    nombre_completo: Optional[str]
    activo: bool
    es_superusuario: bool
    tipo_autenticacion: TipoAutenticacion
    roles: List[str] = Field(default_factory=list)
    permisos: List[str] = Field(default_factory=list)

class RolBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=50, description="Nombre del rol")
    descripcion: Optional[str] = Field(None, description="Descripción del rol")
    activo: bool = Field(default=True, description="Rol activo")

class RolCreate(RolBase):
    permisos: List[str] = Field(default_factory=list, description="Lista de permisos")

class RolUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    permisos: Optional[List[str]] = None

class RolResponse(RolBase):
    id: int
    fecha_creacion: datetime
    permisos: List[str]
    model_config = {"from_attributes": True}


class PermisoBase(BaseModel):
    codigo: str = Field(..., min_length=3, max_length=100, description="Código del permiso")
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre del permiso")
    descripcion: Optional[str] = Field(None, description="Descripción del permiso")
    recurso: str = Field(..., description="Recurso protegido")
    accion: str = Field(..., description="Acción permitida")

class PermisoResponse(PermisoBase):
    id: int
    fecha_creacion: datetime
    model_config = {"from_attributes": True}


class AsignarRolesRequest(BaseModel):
    roles: List[int] = Field(..., description="IDs de roles a asignar")

class ValidateTokenResponse(BaseModel):
    valido: bool
    usuario: Optional[UsuarioResponse] = None
    razon: Optional[str] = None

class CambiarContrasenaRequest(BaseModel):
    contrasena_actual: str = Field(..., description="Contraseña actual")
    contrasena_nueva: str = Field(..., min_length=12, description="Contraseña nueva")
    contrasena_confirmacion: str = Field(..., description="Confirmación de contraseña nueva")
    @field_validator("contrasena_confirmacion")
    @classmethod
    def validar_contrasenas_coinciden(cls, v, info):
        if "contrasena_nueva" in info.data and v != info.data["contrasena_nueva"]:
            raise ValueError("Las contraseñas no coinciden")
        return v

class SolicitarResetRequest(BaseModel):
    email: EmailStr = Field(..., description="Email del usuario")

class SolicitarResetResponse(BaseModel):
    mensaje: str = Field(..., description="Mensaje de confirmación")
    token: Optional[str] = Field(None, description="Token (solo en desarrollo)")

class ResetearContrasenaRequest(BaseModel):
    token: str = Field(..., description="Token de reset")
    nueva_contrasena: str = Field(..., min_length=12, description="Nueva contraseña")
    confirmacion_contrasena: str = Field(..., description="Confirmación de contraseña")
    @field_validator("confirmacion_contrasena")
    @classmethod
    def validar_contrasenas_coinciden(cls, v, info):
        if "nueva_contrasena" in info.data and v != info.data["nueva_contrasena"]:
            raise ValueError("Las contraseñas no coinciden")
        return v
