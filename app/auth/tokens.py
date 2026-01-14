from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt

from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import TokenExpiredError, InvalidTokenError
from app.core.security import calculate_expiration

logger = get_logger(__name__)


class TokenManager:
    
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.refresh_secret_key = settings.jwt_refresh_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days
    
    def crear_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = calculate_expiration(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        logger.debug(
            "access_token_creado",
            subject=data.get("sub"),
            expires_at=expire.isoformat()
        )
        
        return encoded_jwt
    
    def crear_refresh_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = calculate_expiration(days=self.refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.refresh_secret_key,
            algorithm=self.algorithm
        )
        
        logger.debug(
            "refresh_token_creado",
            subject=data.get("sub"),
            expires_at=expire.isoformat()
        )
        
        return encoded_jwt
    
    def validar_access_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Verificar que sea un access token
            if payload.get("type") != "access":
                logger.warning("token_tipo_incorrecto", tipo=payload.get("type"))
                raise InvalidTokenError("Tipo de token incorrecto")
            
            logger.debug(
                "access_token_validado",
                subject=payload.get("sub")
            )
            
            return payload
        
        except jwt.ExpiredSignatureError:
            logger.warning("access_token_expirado")
            raise TokenExpiredError("Token de acceso expirado")
        
        except JWTError as e:
            logger.warning("access_token_invalido", error=str(e))
            raise InvalidTokenError(f"Token de acceso inválido: {str(e)}")
    
    def validar_refresh_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self.refresh_secret_key,
                algorithms=[self.algorithm]
            )
            
            # Verificar que sea un refresh token
            if payload.get("type") != "refresh":
                logger.warning("token_tipo_incorrecto", tipo=payload.get("type"))
                raise InvalidTokenError("Tipo de token incorrecto")
            
            logger.debug(
                "refresh_token_validado",
                subject=payload.get("sub")
            )
            
            return payload
        
        except jwt.ExpiredSignatureError:
            logger.warning("refresh_token_expirado")
            raise TokenExpiredError("Token de refresco expirado")
        
        except JWTError as e:
            logger.warning("refresh_token_invalido", error=str(e))
            raise InvalidTokenError(f"Token de refresco inválido: {str(e)}")
    
    def decodificar_token_sin_validar(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_signature": False, "verify_exp": False}
            )
            return payload
        except Exception as e:
            logger.error("error_decodificando_token", error=str(e))
            return None
    
    def calcular_tiempo_expiracion(self) -> int:
        return self.access_token_expire_minutes * 60
