from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import ldap
from datetime import datetime

from app.config import settings
from app.core.logging import get_logger, audit_logger
from app.core.exceptions import AuthenticationError, ExternalServiceError
from app.schemas.auth import TipoAutenticacion

logger = get_logger(__name__)


class AuthProvider(ABC):
    
    @abstractmethod
    async def autenticar(self, nombre_usuario: str, contrasena: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_tipo(self) -> TipoAutenticacion:
        pass

class LDAPAuthProvider(AuthProvider):
    
    def __init__(self):
        self.server = settings.ldap_server
        self.port = settings.ldap_port
        self.use_ssl = settings.ldap_use_ssl
        self.base_dn = settings.ldap_base_dn
        self.user_dn_template = settings.ldap_user_dn_template
        self.bind_dn = settings.ldap_bind_dn
        self.bind_password = settings.ldap_bind_password
        self.search_filter = settings.ldap_search_filter
        self.timeout = settings.ldap_timeout
        
        logger.info(
            "ldap_provider_inicializado",
            server=self.server,
            port=self.port,
            use_ssl=self.use_ssl
        )
    
    async def autenticar(self, nombre_usuario: str, contrasena: str) -> Optional[Dict[str, Any]]:
        if not nombre_usuario or not contrasena:
            logger.warning("ldap_auth_credenciales_vacias")
            return None
        
        try:
            # Construir DN del usuario
            user_dn = self.user_dn_template.format(username=nombre_usuario)
            
            # Construir URL de conexión
            ldap_url = f"{self.server}:{self.port}"
            
            logger.info(
                "ldap_auth_intento",
                username=nombre_usuario,
                server=self.server
            )
            
            # Configurar SSL si es necesario
            if self.use_ssl:
                ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)
                ldap.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
            
            # Inicializar conexión
            conn = ldap.initialize(ldap_url)
            conn.set_option(ldap.OPT_REFERRALS, 0)
            conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            conn.set_option(ldap.OPT_NETWORK_TIMEOUT, self.timeout)
            
            # Intentar bind con credenciales del usuario
            conn.simple_bind_s(user_dn, contrasena)
            
            logger.info("ldap_bind_exitoso", username=nombre_usuario)
            
            # Obtener atributos del usuario
            user_info = await self._obtener_atributos_usuario(conn, nombre_usuario)
            
            conn.unbind_s()
            
            audit_logger.log_authentication(
                username=nombre_usuario,
                success=True,
                ip_address="system",
                user_agent="ldap",
                method="ldap"
            )
            
            return user_info
        
        except ldap.INVALID_CREDENTIALS:
            logger.warning(
                "ldap_credenciales_invalidas",
                username=nombre_usuario
            )
            audit_logger.log_authentication(
                username=nombre_usuario,
                success=False,
                ip_address="system",
                user_agent="ldap",
                method="ldap",
                reason="credenciales_invalidas"
            )
            return None
        
        except ldap.SERVER_DOWN:
            logger.error(
                "ldap_servidor_no_disponible",
                server=self.server,
                username=nombre_usuario
            )
            raise ExternalServiceError(
                f"Servidor LDAP no disponible: {self.server}",
                service="LDAP"
            )
        
        except ldap.TIMEOUT:
            logger.error(
                "ldap_timeout",
                server=self.server,
                username=nombre_usuario,
                timeout=self.timeout
            )
            raise ExternalServiceError(
                "Timeout al conectar con servidor LDAP",
                service="LDAP"
            )
        
        except Exception as e:
            logger.error(
                "ldap_error_inesperado",
                error=str(e),
                username=nombre_usuario
            )
            
            # En desarrollo, permitir bypass si LDAP no está configurado
            if settings.is_development and settings.local_auth_enabled:
                logger.warning("ldap_bypass_desarrollo", username=nombre_usuario)
                return {
                    "nombre_usuario": nombre_usuario,
                    "email": f"{nombre_usuario}@defensoria.gob.pe",
                    "nombre_completo": f"Usuario LDAP {nombre_usuario}",
                    "id_externo": None
                }
            
            raise ExternalServiceError(
                f"Error en autenticación LDAP: {str(e)}",
                service="LDAP"
            )
    
    async def _obtener_atributos_usuario(
        self,
        conn: ldap.ldapobject.LDAPObject,
        nombre_usuario: str
    ) -> Dict[str, Any]:
        try:
            search_filter = self.search_filter.format(username=nombre_usuario)
            attributes = [
                'mail', 'cn', 'displayName', 'givenName', 'sn',
                'telephoneNumber', 'department', 'title', 'employeeID'
            ]
            
            result = conn.search_s(
                self.base_dn,
                ldap.SCOPE_SUBTREE,
                search_filter,
                attributes
            )
            
            if not result:
                logger.warning(
                    "ldap_usuario_no_encontrado",
                    username=nombre_usuario
                )
                return {
                    "nombre_usuario": nombre_usuario,
                    "email": None,
                    "nombre_completo": None,
                    "id_externo": None
                }
            
            dn, attrs = result[0]
            
            # Extraer y decodificar atributos
            def get_attr(attr_name: str) -> Optional[str]:
                if attr_name in attrs and attrs[attr_name]:
                    return attrs[attr_name][0].decode('utf-8')
                return None
            
            user_info = {
                "nombre_usuario": nombre_usuario,
                "email": get_attr('mail'),
                "nombre_completo": get_attr('cn') or get_attr('displayName'),
                "telefono": get_attr('telephoneNumber'),
                "departamento": get_attr('department'),
                "cargo": get_attr('title'),
                "id_externo": get_attr('employeeID')
            }
            
            logger.info(
                "ldap_atributos_obtenidos",
                username=nombre_usuario,
                email=user_info.get('email')
            )
            
            return user_info
        
        except Exception as e:
            logger.error(
                "ldap_error_obteniendo_atributos",
                error=str(e),
                username=nombre_usuario
            )
            return {
                "nombre_usuario": nombre_usuario,
                "email": None,
                "nombre_completo": None,
                "id_externo": None
            }
    
    def get_tipo(self) -> TipoAutenticacion:
        return TipoAutenticacion.ldap


class AzureADAuthProvider(AuthProvider):
    
    def __init__(self):
        self.tenant_id = settings.azure_ad_tenant_id
        self.client_id = settings.azure_ad_client_id
        self.client_secret = settings.azure_ad_client_secret
        
        if settings.azure_ad_enabled:
            logger.info(
                "azure_ad_provider_inicializado",
                tenant_id=self.tenant_id,
                client_id=self.client_id
            )
    
    async def autenticar(self, nombre_usuario: str, contrasena: str) -> Optional[Dict[str, Any]]:
        if not settings.azure_ad_enabled:
            logger.warning("azure_ad_no_habilitado")
            return None
        
        try:
            import msal
            
            # Crear aplicación MSAL
            app = msal.PublicClientApplication(
                client_id=self.client_id,
                authority=f"https://login.microsoftonline.com/{self.tenant_id}"
            )
            
            # Intentar autenticación (ROPC flow - NO recomendado para producción)
            result = app.acquire_token_by_username_password(
                username=nombre_usuario,
                password=contrasena,
                scopes=["User.Read"]
            )
            
            if "access_token" in result:
                logger.info("azure_ad_auth_exitosa", username=nombre_usuario)
                
                # Obtener información del usuario desde el token
                user_info = self._extraer_info_token(result)
                
                audit_logger.log_authentication(
                    username=nombre_usuario,
                    success=True,
                    ip_address="system",
                    user_agent="azure_ad",
                    method="azure_ad"
                )
                
                return user_info
            else:
                error = result.get("error_description", "Unknown error")
                logger.warning(
                    "azure_ad_auth_fallida",
                    username=nombre_usuario,
                    error=error
                )
                
                audit_logger.log_authentication(
                    username=nombre_usuario,
                    success=False,
                    ip_address="system",
                    user_agent="azure_ad",
                    method="azure_ad",
                    reason=error
                )
                
                return None
        
        except ImportError:
            logger.error("msal_no_instalado")
            raise ExternalServiceError(
                "Librería MSAL no instalada",
                service="Azure AD"
            )
        
        except Exception as e:
            logger.error(
                "azure_ad_error",
                error=str(e),
                username=nombre_usuario
            )
            raise ExternalServiceError(
                f"Error en autenticación Azure AD: {str(e)}",
                service="Azure AD"
            )
    
    def _extraer_info_token(self, token_result: Dict) -> Dict[str, Any]:
        # Los claims del token ID contienen información del usuario
        id_token_claims = token_result.get("id_token_claims", {})
        
        return {
            "nombre_usuario": id_token_claims.get("preferred_username", "").split("@")[0],
            "email": id_token_claims.get("email") or id_token_claims.get("preferred_username"),
            "nombre_completo": id_token_claims.get("name"),
            "id_externo": id_token_claims.get("oid")  # Object ID de Azure AD
        }
    
    def get_tipo(self) -> TipoAutenticacion:
        return TipoAutenticacion.azure_ad


class LocalAuthProvider(AuthProvider):
    
    def __init__(self):
        logger.info("local_auth_provider_inicializado")
    
    async def autenticar(self, nombre_usuario: str, contrasena: str) -> Optional[Dict[str, Any]]:
        if not settings.local_auth_enabled:
            logger.warning("local_auth_no_habilitado")
            return None
        
        # La autenticación local se maneja en AuthService
        # ya que requiere acceso a la base de datos
        logger.info("local_auth_delegado_a_servicio", username=nombre_usuario)
        
        return {
            "nombre_usuario": nombre_usuario,
            "tipo": "local"
        }
    
    def get_tipo(self) -> TipoAutenticacion:
        return TipoAutenticacion.local


class AuthProviderFactory:
    
    _providers: Dict[TipoAutenticacion, AuthProvider] = {}
    
    @classmethod
    def get_provider(cls, tipo: TipoAutenticacion) -> AuthProvider:
        if tipo not in cls._providers:
            if tipo == TipoAutenticacion.ldap:
                cls._providers[tipo] = LDAPAuthProvider()
            elif tipo == TipoAutenticacion.azure_ad:
                cls._providers[tipo] = AzureADAuthProvider()
            elif tipo == TipoAutenticacion.local:
                cls._providers[tipo] = LocalAuthProvider()
            else:
                raise ValueError(f"Tipo de autenticación no soportado: {tipo}")
        
        return cls._providers[tipo]
    
    @classmethod
    def get_available_providers(cls) -> list[AuthProvider]:
        providers = []
        
        if settings.ldap_enabled:
            providers.append(cls.get_provider(TipoAutenticacion.ldap))
        
        if settings.azure_ad_enabled:
            providers.append(cls.get_provider(TipoAutenticacion.azure_ad))
        
        if settings.local_auth_enabled:
            providers.append(cls.get_provider(TipoAutenticacion.local))
        
        return providers
