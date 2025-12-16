from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache
import json


class Settings(BaseSettings):
    # Aplicación
    app_name: str = "Defensoria Middleware"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = True

    # Variables de conexión y credenciales
    postgres_user: str
    postgres_password: str
    postgres_db: str
    admin_default_password: str
    postgres_port: str
    log_level: str = "INFO"
    log_format: str = "json"
    enable_audit_log: bool = True
    azure_ad_enabled: bool = False

    # Seguridad
    secret_key: str
    jwt_secret_key: str
    jwt_refresh_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Rate Limiting
    rate_limit_per_minute: int = 60
    auth_rate_limit_per_minute: int = 5

    # CORS
    allowed_origins: str = "[]"
    allowed_hosts: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: List[str] = ["*"]
    
    @property
    def get_allowed_origins(self) -> List[str]:
        """Parse allowed_origins from JSON string to list"""
        try:
            return json.loads(self.allowed_origins)
        except (json.JSONDecodeError, TypeError):
            return ["*"]

    # Base de datos
    database_url: str
    db_pool_size: int = 20
    db_max_overflow: int = 10
    azure_ad_redirect_uri: Optional[str] = None
    db_echo: bool = False

    # LDAP
    ldap_enabled: bool = False
    ldap_server: Optional[str] = None
    ldap_port: int = 636
    ldap_use_ssl: bool = True
    ldap_base_dn: Optional[str] = None
    ldap_user_dn_template: Optional[str] = None
    ldap_bind_dn: Optional[str] = None
    ldap_bind_password: Optional[str] = None
    ldap_search_filter: str = "(uid={username})"
    ldap_timeout: int = 10

    # Local Auth
    local_auth_enabled: bool = True

    # Security Headers
    enable_security_headers: bool = True
    enable_https_redirect: bool = False

    # Session
    session_cookie_secure: bool = False
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "lax"

    # GCP
    gcp_project_id: Optional[str] = None
    gcp_region: str = "us-central1"
    enable_gcp_secret_manager: bool = False

    # Password Reset
    password_reset_token_expire_hours: int = 1
    password_reset_max_attempts: int = 3

    # Account Lockout
    max_login_attempts: int = 5
    account_lockout_minutes: int = 30
    
    # Session Limits
    max_active_sessions_per_user: int = 5
    session_inactivity_timeout_minutes: int = 60
    
    # Password Policy
    password_history_count: int = 5  # No reutilizar últimas 5 contraseñas
    password_expiration_days: int = 90  # Cambio obligatorio cada 90 días
    enforce_password_history: bool = True
    enforce_password_expiration: bool = False  # Deshabilitado por defecto
    
    # User Limits
    max_users_limit: int = 1000  # Límite de usuarios en el sistema
    enforce_user_limit: bool = False  # Deshabilitado por defecto

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
