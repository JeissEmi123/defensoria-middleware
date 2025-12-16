import logging
import structlog
import sys
from typing import Any, Dict, Optional
from datetime import datetime
from contextvars import ContextVar

from app.config import settings

# ContextVar para tracking de request ID
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[int]] = ContextVar("user_id", default=None)


def add_request_context(
    logger: Any, method_name: str, event_dict: Dict
) -> Dict:
    request_id = request_id_var.get()
    user_id = user_id_var.get()
    
    if request_id:
        event_dict["request_id"] = request_id
    if user_id:
        event_dict["user_id"] = user_id
    
    return event_dict


def add_timestamp(logger: Any, method_name: str, event_dict: Dict) -> Dict:
    event_dict["timestamp"] = datetime.utcnow().isoformat()
    return event_dict


def configure_logging():
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Configurar logging estándar de Python
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    # Configurar procesadores de structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        add_request_context,
        add_timestamp,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.StackInfoRenderer(),
    ]
    
    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    return structlog.get_logger(name)


class AuditLogger:
    
    def __init__(self):
        self.logger = get_logger("audit")
    
    def log_authentication(
        self,
        username: str,
        success: bool,
        ip_address: str,
        user_agent: str,
        method: str = "unknown",
        reason: Optional[str] = None
    ):
        self.logger.info(
            "authentication_attempt",
            username=username,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            auth_method=method,
            reason=reason,
            event_type="authentication"
        )
    
    def log_authorization(
        self,
        user_id: int,
        username: str,
        resource: str,
        action: str,
        granted: bool,
        reason: Optional[str] = None
    ):
        self.logger.info(
            "authorization_attempt",
            user_id=user_id,
            username=username,
            resource=resource,
            action=action,
            granted=granted,
            reason=reason,
            event_type="authorization"
        )
    
    def log_data_access(
        self,
        user_id: int,
        username: str,
        resource: str,
        action: str,
        record_id: Optional[str] = None
    ):
        self.logger.info(
            "data_access",
            user_id=user_id,
            username=username,
            resource=resource,
            action=action,
            record_id=record_id,
            event_type="data_access"
        )
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        details: Optional[Dict] = None
    ):
        self.logger.warning(
            "security_event",
            security_event_type=event_type,
            severity=severity,
            description=description,
            details=details or {},
            event_type="security"
        )
    
    def log_configuration_change(
        self,
        user_id: int,
        username: str,
        setting: str,
        old_value: Any,
        new_value: Any
    ):
        self.logger.info(
            "configuration_change",
            user_id=user_id,
            username=username,
            setting=setting,
            old_value=str(old_value),
            new_value=str(new_value),
            event_type="configuration"
        )


# Inicializar logging
configure_logging()

# Instancia global de audit logger
audit_logger = AuditLogger()
