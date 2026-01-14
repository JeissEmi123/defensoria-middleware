from passlib.context import CryptContext
from typing import Optional
import secrets
import re
from datetime import datetime, timedelta


# Contexto para hashing de contraseñas
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Aumentado para mayor seguridad
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_random_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def validate_password_strength(password: str, username: str = None, email: str = None) -> tuple[bool, Optional[str]]:
    """Validación completa de fortaleza de contraseña"""
    if len(password) < 12:
        return False, "La contraseña debe tener al menos 12 caracteres"
    
    if len(password) > 128:
        return False, "La contraseña no puede exceder 128 caracteres"
    
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe contener al menos una mayúscula"
    
    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe contener al menos una minúscula"
    
    if not re.search(r"\d", password):
        return False, "La contraseña debe contener al menos un número"
    
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False, "La contraseña debe contener al menos un carácter especial"
    
    # Verificar patrones comunes débiles
    weak_patterns = [
        r"123456", r"password", r"qwerty", r"abc123", r"letmein",
        r"welcome", r"monkey", r"dragon", r"master", r"sunshine",
        r"(.)\1{3,}",  # Más de 3 caracteres repetidos
    ]
    
    for pattern in weak_patterns:
        if re.search(pattern, password, re.IGNORECASE):
            return False, "La contraseña contiene patrones débiles comunes"
    
    # No permitir nombre de usuario en la contraseña
    if username and len(username) >= 3:
        if username.lower() in password.lower():
            return False, "La contraseña no puede contener el nombre de usuario"
    
    # No permitir email en la contraseña
    if email:
        email_parts = email.lower().split('@')
        if email_parts[0] in password.lower():
            return False, "La contraseña no puede contener partes del email"
    
    # Verificar secuencias comunes
    sequences = ['abcd', '1234', 'qwer', 'asdf', 'zxcv']
    for seq in sequences:
        if seq in password.lower():
            return False, "La contraseña no puede contener secuencias comunes del teclado"
    
    return True, None


def sanitize_input(input_str: str, max_length: int = 255) -> str:
    if not input_str:
        return ""
    
    # Truncar a longitud máxima
    sanitized = input_str[:max_length]
    
    # Remover caracteres de control
    sanitized = "".join(char for char in sanitized if char.isprintable())
    
    # Strip whitespace
    sanitized = sanitized.strip()
    
    return sanitized


def validate_username(username: str, check_reserved: bool = True) -> tuple[bool, Optional[str]]:
    """Validación completa de nombre de usuario
    
    Args:
        username: Nombre de usuario a validar
        check_reserved: Si es True, valida palabras reservadas (usar False en login)
    """
    if not username:
        return False, "El nombre de usuario es requerido"
    
    if len(username) < 3:
        return False, "El nombre de usuario debe tener al menos 3 caracteres"
    
    if len(username) > 50:
        return False, "El nombre de usuario no puede exceder 50 caracteres"
    
    # Solo permitir letras, números, guiones y guiones bajos
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return False, "El nombre de usuario solo puede contener letras, números, guiones y guiones bajos"
    
    # No permitir que sea un email
    if '@' in username or '.' in username:
        return False, "El nombre de usuario no puede ser un email"
    
    # No permitir palabras reservadas (solo en creación, no en login)
    if check_reserved:
        reserved_words = [
            'root', 'system', 'administrator',
            'user', 'test', 'demo', 'guest', 'public', 'api', 'null',
            'undefined', 'default', 'config', 'settings'
        ]
        
        if username.lower() in reserved_words:
            return False, f"El nombre de usuario '{username}' está reservado"
    
    # No permitir que empiece con números
    if username[0].isdigit():
        return False, "El nombre de usuario no puede empezar con un número"
    
    return True, None


def is_token_expired(exp_timestamp: datetime) -> bool:
    return datetime.utcnow() > exp_timestamp


def validate_email_format(email: str) -> tuple[bool, Optional[str]]:
    """Validación avanzada de formato de email"""
    if not email:
        return False, "El email es requerido"
    
    if len(email) > 254:
        return False, "El email no puede exceder 254 caracteres"
    
    # Patrón RFC 5322 simplificado
    email_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Formato de email inválido"
    
    # Validar que no tenga caracteres peligrosos
    dangerous_chars = ['<', '>', '"', "'", '\\', ';', '(', ')']
    if any(char in email for char in dangerous_chars):
        return False, "El email contiene caracteres no permitidos"
    
    # Validar dominios temporales/desechables comunes
    disposable_domains = [
        'tempmail.com', '10minutemail.com', 'guerrillamail.com',
        'mailinator.com', 'throwaway.email', 'temp-mail.org'
    ]
    
    domain = email.split('@')[1].lower()
    if domain in disposable_domains:
        return False, "No se permiten emails temporales o desechables"
    
    return True, None


def validate_nombre_completo(nombre: str) -> tuple[bool, Optional[str]]:
    """Validación de nombre completo"""
    if not nombre:
        return True, None  # Es opcional
    
    if len(nombre) < 3:
        return False, "El nombre completo debe tener al menos 3 caracteres"
    
    if len(nombre) > 100:
        return False, "El nombre completo no puede exceder 100 caracteres"
    
    # No permitir números en el nombre
    if re.search(r'\d', nombre):
        return False, "El nombre completo no puede contener números"
    
    # Solo permitir letras, espacios, acentos y algunos caracteres especiales
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'-]+$", nombre):
        return False, "El nombre completo contiene caracteres no permitidos"
    
    # No permitir múltiples espacios consecutivos
    if '  ' in nombre:
        return False, "El nombre completo no puede tener espacios múltiples"
    
    return True, None


def sanitize_email(email: str) -> str:
    """Sanitizar y normalizar email"""
    if not email:
        return ""
    
    # Convertir a minúsculas
    email = email.lower().strip()
    
    # Remover espacios
    email = email.replace(' ', '')
    
    return email


def detect_sql_injection(input_str: str) -> bool:
    """Detectar intentos de inyección SQL"""
    sql_patterns = [
        r"('|(\-\-)|(;)|(\|\|)|(\*))",
        r"\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b",
        r"\b(or|and)\b.*[=<>]",
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, input_str, re.IGNORECASE):
            return True
    
    return False


def detect_xss(input_str: str) -> bool:
    """Detectar intentos de XSS"""
    xss_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe',
        r'<object',
        r'<embed',
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, input_str, re.IGNORECASE):
            return True
    
    return False


def validate_input_security(input_str: str, field_name: str = "campo") -> tuple[bool, Optional[str]]:
    """Validación de seguridad para inputs"""
    if not input_str:
        return True, None
    
    if detect_sql_injection(input_str):
        return False, f"El {field_name} contiene patrones sospechosos de inyección SQL"
    
    if detect_xss(input_str):
        return False, f"El {field_name} contiene patrones sospechosos de XSS"
    
    # Verificar caracteres de control
    if any(ord(char) < 32 and char not in '\n\r\t' for char in input_str):
        return False, f"El {field_name} contiene caracteres de control no permitidos"
    
    return True, None


def calculate_expiration(minutes: int = None, days: int = None) -> datetime:
    now = datetime.utcnow()
    
    if minutes:
        return now + timedelta(minutes=minutes)
    elif days:
        return now + timedelta(days=days)
    else:
        return now + timedelta(minutes=30)  # Default 30 minutos
