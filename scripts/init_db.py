"""Inicializa la base de datos con datos semilla."""
import asyncio
import logging
import pathlib
import sys
from sqlalchemy.future import select

# Agregar el directorio raíz del proyecto al sys.path
# para permitir importaciones relativas desde la app.
ROOT_DIR = pathlib.Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from app.core.logging import get_logger
from app.core.security import hash_password
from app.database.session import get_db_context
from app.database.models import Usuario, Rol
from app.services.rbac_service import RBACService
from app.config import settings

logger = get_logger(__name__)

async def main():
    """
    Función principal para inicializar la base de datos con datos semilla.
    """
    logger.info("Iniciando la inicialización de datos del sistema...")

    async with get_db_context() as db:
        try:
            # 1. Inicializar Roles y Permisos del Sistema
            logger.info("Paso 1/3: Inicializando roles y permisos del sistema...")
            rbac_service = RBACService(db)
            await rbac_service.inicializar_roles_sistema()
            logger.info("Roles y permisos del sistema creados o verificados.")

            # 2. Crear el usuario administrador
            logger.info("Paso 2/3: Creando usuario administrador...")
            admin_username = "admin"
            
            result = await db.execute(
                select(Usuario).where(Usuario.nombre_usuario == admin_username)
            )
            admin_user = result.scalar_one_or_none()

            if admin_user:
                logger.warning(f"El usuario '{admin_username}' ya existe. Saltando creación.")
            else:
                if not settings.admin_default_password:
                    logger.error("La variable de entorno ADMIN_DEFAULT_PASSWORD no está configurada.")
                    raise ValueError("ADMIN_DEFAULT_PASSWORD no puede estar vacía.")

                admin_user = Usuario(
                    nombre_usuario=admin_username,
                    email="admin@defensoria.gob.pe",
                    nombre_completo="Administrador del Sistema",
                    contrasena_hash=hash_password(settings.admin_default_password),
                    es_superusuario=True,
                    activo=True,
                )
                db.add(admin_user)
                await db.flush()  # Para obtener el ID del usuario creado
                logger.info(f"Usuario '{admin_username}' creado con éxito.")

            # 3. Asignar el rol 'Administrador' al usuario admin
            logger.info("Paso 3/3: Asignando rol 'Administrador' al superusuario...")
            result = await db.execute(select(Rol).where(Rol.nombre == "Administrador"))
            admin_rol = result.scalar_one_or_none()
            
            if not admin_rol:
                logger.error("El rol 'Administrador' no fue encontrado. No se pudo asignar.")
                # Considerar si lanzar una excepción aquí
            elif admin_user and admin_rol not in admin_user.roles:
                admin_user.roles.append(admin_rol)
                logger.info("Rol 'Administrador' asignado al usuario 'admin'.")
            elif admin_user and admin_rol in admin_user.roles:
                 logger.warning("El usuario 'admin' ya tiene el rol 'Administrador'.")
            
            await db.commit()

        except Exception as e:
            logger.error(f"Ocurrió un error durante la inicialización: {e}", exc_info=True)
            await db.rollback()
            # Levantar la excepción para que el script falle si algo sale mal
            raise

    logger.info("Inicialización de datos del sistema completada con éxito.")


if __name__ == "__main__":
    # Configurar logging básico si el script se ejecuta directamente
    logging.basicConfig(level=logging.INFO)
    
    # Python 3.7+
    asyncio.run(main())