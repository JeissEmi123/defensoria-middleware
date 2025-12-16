import os
import sys
from pathlib import Path

# Colores para terminal
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class ConfigValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []
        
    def error(self, msg):
        self.errors.append(msg)
        print(f"{RED} ERROR: {msg}{RESET}")
    
    def warning(self, msg):
        self.warnings.append(msg)
        print(f"{YELLOW}  WARNING: {msg}{RESET}")
    
    def success(self, msg):
        self.passed.append(msg)
        print(f"{GREEN} {msg}{RESET}")
    
    def info(self, msg):
        print(f"{BLUE}ℹ  {msg}{RESET}")
    
    def check_env_file_exists(self):
        self.info("Verificando archivo .env...")
        if not Path(".env").exists():
            self.error("Archivo .env no encontrado. Copiar de .env.example")
            return False
        self.success("Archivo .env encontrado")
        return True
    def check_required_vars(self):
        self.info("Verificando variables de entorno obligatorias...")
        required_vars = [
            "SECRET_KEY",
            "JWT_SECRET_KEY", 
            "JWT_REFRESH_SECRET_KEY",
            "DATABASE_URL"
        ]
        
        missing = []
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing.append(var)
        
        if missing:
            self.error(f"Variables faltantes: {', '.join(missing)}")
            return False
        
        self.success("Todas las variables obligatorias están configuradas")
        return True
    
    def check_secret_keys(self):
        self.info("Verificando seguridad de secret keys...")
        insecure_patterns = [
            "CHANGE",
            "change",
            "dev-",
            "development",
            "test",
            "example",
            "secret",
            "password",
            "123456"
        ]
        
        keys_to_check = {
            "SECRET_KEY": os.getenv("SECRET_KEY", ""),
            "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", ""),
            "JWT_REFRESH_SECRET_KEY": os.getenv("JWT_REFRESH_SECRET_KEY", "")
        }
        
        for key_name, key_value in keys_to_check.items():
            # Verificar longitud
            if len(key_value) < 32:
                self.error(f"{key_name} debe tener al menos 32 caracteres (tiene {len(key_value)})")
            
            # Verificar patrones inseguros
            for pattern in insecure_patterns:
                if pattern.lower() in key_value.lower():
                    self.error(f"{key_name} contiene patrón inseguro: '{pattern}'")
            
            # Verificar que no sean iguales
            for other_key, other_value in keys_to_check.items():
                if key_name != other_key and key_value == other_value:
                    self.error(f"{key_name} y {other_key} son iguales (deben ser diferentes)")
        
        if len(self.errors) == 0:
            self.success("Secret keys son seguras")
            return True
        return False
    
    def check_database_url(self):
        self.info("Verificando configuración de base de datos...")
        db_url = os.getenv("DATABASE_URL", "")
        
        # Verificar que no use credenciales inseguras
        insecure_patterns = ["postgres:postgres", "admin:admin", "root:root", ":123456", ":password"]
        
        for pattern in insecure_patterns:
            if pattern in db_url:
                self.error(f"Database URL contiene credenciales inseguras: '{pattern}'")
        
        # Verificar que no use localhost en producción
        if os.getenv("APP_ENV") == "production" and "localhost" in db_url:
            self.warning("Database URL usa 'localhost' en producción")
        
        if len(self.errors) == 0:
            self.success("Configuración de base de datos es segura")
            return True
        return False
    
    def check_debug_mode(self):
        self.info("Verificando modo DEBUG...")
        debug = os.getenv("DEBUG", "false").lower()
        app_env = os.getenv("APP_ENV", "development").lower()
        
        if app_env == "production" and debug == "true":
            self.error("DEBUG está habilitado en producción (debe ser false)")
            return False
        
        self.success("Modo DEBUG correctamente configurado")
        return True
    
    def check_cors(self):
        self.info("Verificando configuración de CORS...")
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "[]")
        app_env = os.getenv("APP_ENV", "development").lower()
        
        if app_env == "production":
            if "localhost" in allowed_origins:
                self.warning("ALLOWED_ORIGINS contiene 'localhost' en producción")
            
            if "*" in allowed_origins:
                self.error("ALLOWED_ORIGINS usa wildcard '*' en producción")
                return False
            
            if "http://" in allowed_origins:
                self.warning("ALLOWED_ORIGINS contiene URLs HTTP (usar HTTPS)")
        
        self.success("Configuración de CORS verificada")
        return True
    
    def check_admin_password(self):
        self.info("Verificando contraseña de admin...")
        admin_pwd = os.getenv("ADMIN_DEFAULT_PASSWORD", "")
        
        if len(admin_pwd) < 12:
            self.warning("ADMIN_DEFAULT_PASSWORD debería tener al menos 12 caracteres")
        
        weak_passwords = ["admin", "password", "123456", "Admin123", "Password123"]
        if admin_pwd in weak_passwords:
            self.error(f"ADMIN_DEFAULT_PASSWORD es muy débil: '{admin_pwd}'")
            return False
        
        self.success("Contraseña de admin tiene formato seguro")
        self.warning("Recuerda cambiar la contraseña de admin en el primer login")
        return True
    
    def check_https_settings(self):
        self.info("Verificando configuración de HTTPS...")
        app_env = os.getenv("APP_ENV", "development").lower()
        
        if app_env == "production":
            https_redirect = os.getenv("ENABLE_HTTPS_REDIRECT", "false").lower()
            cookie_secure = os.getenv("SESSION_COOKIE_SECURE", "false").lower()
            
            if https_redirect != "true":
                self.warning("ENABLE_HTTPS_REDIRECT debería estar en 'true' para producción")
            
            if cookie_secure != "true":
                self.warning("SESSION_COOKIE_SECURE debería estar en 'true' para producción")
        
        self.success("Configuración de HTTPS verificada")
        return True
    
    def run_all_checks(self):
        print("\n" + "="*80)
        print(f"{BLUE} VALIDACIÓN DE CONFIGURACIÓN - DEFENSORIA MIDDLEWARE{RESET}")
        print("="*80 + "\n")
        # Cargar variables de entorno desde .env
        if Path(".env").exists():
            from dotenv import load_dotenv
            load_dotenv()
        
        # Ejecutar checks
        self.check_env_file_exists()
        self.check_required_vars()
        self.check_secret_keys()
        self.check_database_url()
        self.check_debug_mode()
        self.check_cors()
        self.check_admin_password()
        self.check_https_settings()
        
        # Resumen
        print("\n" + "="*80)
        print(f"{BLUE} RESUMEN DE VALIDACIÓN{RESET}")
        print("="*80)
        print(f"{GREEN} Checks exitosos: {len(self.passed)}{RESET}")
        print(f"{YELLOW}  Warnings: {len(self.warnings)}{RESET}")
        print(f"{RED} Errores: {len(self.errors)}{RESET}")
        print("="*80 + "\n")
        
        # Determinar resultado
        if self.errors:
            print(f"{RED} VALIDACIÓN FALLIDA - Corregir errores antes de continuar{RESET}")
            print(f"\n{RED}Errores encontrados:{RESET}")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
            return False
        elif self.warnings:
            print(f"{YELLOW}  VALIDACIÓN CON WARNINGS - Revisar advertencias{RESET}")
            print(f"\n{YELLOW}Advertencias:{RESET}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
            return True
        else:
            print(f"{GREEN} VALIDACIÓN EXITOSA - Configuración lista para producción{RESET}")
            return True


def main():
    validator = ConfigValidator()
    success = validator.run_all_checks()
    
    if not success:
        print(f"\n{YELLOW} Consulta SECURITY.md para más información sobre configuración segura{RESET}\n")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
