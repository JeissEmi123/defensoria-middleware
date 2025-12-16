#!/usr/bin/env python3
"""
Script para crear usuario administrador en la base de datos
"""
import asyncio
import sys
from datetime import datetime
from passlib.context import CryptContext
import asyncpg

# Configuración de la conexión
DB_CONFIG = {
    "host": "db",  # Nombre del servicio en docker-compose
    "port": 5432,
    "database": "defensoria_db",
    "user": "defensoria_dev",
    "password": "defensoria_dev_password"
}

# Contexto de encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def crear_usuario_admin():
    """Crear usuario administrador en la base de datos"""
    
    # Datos del usuario administrador
    nombre_usuario = "admin"
    email = "admin@defensoria.gov.co"
    nombre_completo = "Administrador del Sistema"
    contrasena = "Admin123456!"  # Cambiar en producción
    
    print("=" * 60)
    print("CREACIÓN DE USUARIO ADMINISTRADOR")
    print("=" * 60)
    print(f"\nUsuario: {nombre_usuario}")
    print(f"Email: {email}")
    print(f"Nombre: {nombre_completo}")
    print(f"Contraseña: {contrasena}")
    print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login\n")
    
    try:
        # Conectar a la base de datos
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ Conexión exitosa a la base de datos")
        
        # Verificar si el usuario ya existe
        existe = await conn.fetchval(
            "SELECT id FROM usuarios WHERE nombre_usuario = $1 OR email = $2",
            nombre_usuario,
            email
        )
        
        if existe:
            print(f"\n⚠️  El usuario '{nombre_usuario}' ya existe con ID: {existe}")
            
            # Preguntar si desea actualizar
            respuesta = input("\n¿Desea actualizar la contraseña? (s/n): ")
            if respuesta.lower() == 's':
                contrasena_hash = pwd_context.hash(contrasena)
                await conn.execute(
                    """
                    UPDATE usuarios 
                    SET contrasena_hash = $1,
                        ultimo_cambio_contrasena = $2,
                        activo = true,
                        es_superusuario = true,
                        intentos_login_fallidos = 0,
                        fecha_bloqueo = NULL,
                        fecha_actualizacion = $2
                    WHERE id = $3
                    """,
                    contrasena_hash,
                    datetime.utcnow(),
                    existe
                )
                print("✅ Contraseña actualizada exitosamente")
            else:
                print("❌ Operación cancelada")
            
            await conn.close()
            return
        
        # Hashear la contraseña
        contrasena_hash = pwd_context.hash(contrasena)
        
        # Crear el usuario
        usuario_id = await conn.fetchval(
            """
            INSERT INTO usuarios (
                nombre_usuario,
                email,
                nombre_completo,
                contrasena_hash,
                tipo_autenticacion,
                activo,
                es_superusuario,
                fecha_creacion,
                fecha_actualizacion,
                ultimo_cambio_contrasena,
                intentos_login_fallidos,
                requiere_cambio_contrasena
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING id
            """,
            nombre_usuario,
            email,
            nombre_completo,
            contrasena_hash,
            "local",
            True,  # activo
            True,  # es_superusuario
            datetime.utcnow(),
            datetime.utcnow(),
            datetime.utcnow(),
            0,  # intentos_login_fallidos
            False  # requiere_cambio_contrasena
        )
        
        print(f"\n✅ Usuario creado exitosamente con ID: {usuario_id}")
        
        # Verificar si existe el rol de Administrador
        rol_admin_id = await conn.fetchval(
            "SELECT id FROM roles WHERE nombre = $1",
            "Administrador"
        )
        
        if not rol_admin_id:
            # Crear el rol de Administrador
            rol_admin_id = await conn.fetchval(
                """
                INSERT INTO roles (
                    nombre,
                    descripcion,
                    activo,
                    es_sistema,
                    fecha_creacion,
                    fecha_actualizacion
                ) VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
                """,
                "Administrador",
                "Rol con acceso completo al sistema",
                True,
                True,
                datetime.utcnow(),
                datetime.utcnow()
            )
            print(f"✅ Rol 'Administrador' creado con ID: {rol_admin_id}")
        else:
            print(f"✅ Rol 'Administrador' encontrado con ID: {rol_admin_id}")
        
        # Asignar el rol al usuario
        await conn.execute(
            """
            INSERT INTO usuarios_roles (usuario_id, rol_id, fecha_asignacion)
            VALUES ($1, $2, $3)
            ON CONFLICT DO NOTHING
            """,
            usuario_id,
            rol_admin_id,
            datetime.utcnow()
        )
        
        print(f"✅ Rol 'Administrador' asignado al usuario")
        
        # Crear permisos básicos si no existen
        permisos_basicos = [
            ("usuarios.leer", "Leer Usuarios", "Permite ver la lista de usuarios", "usuarios", "leer"),
            ("usuarios.crear", "Crear Usuarios", "Permite crear nuevos usuarios", "usuarios", "crear"),
            ("usuarios.actualizar", "Actualizar Usuarios", "Permite editar usuarios", "usuarios", "actualizar"),
            ("usuarios.eliminar", "Eliminar Usuarios", "Permite eliminar usuarios", "usuarios", "eliminar"),
            ("roles.leer", "Leer Roles", "Permite ver roles", "roles", "leer"),
            ("roles.crear", "Crear Roles", "Permite crear roles", "roles", "crear"),
            ("roles.actualizar", "Actualizar Roles", "Permite editar roles", "roles", "actualizar"),
            ("roles.eliminar", "Eliminar Roles", "Permite eliminar roles", "roles", "eliminar"),
        ]
        
        print("\n📝 Creando permisos básicos...")
        permisos_ids = []
        for codigo, nombre, descripcion, recurso, accion in permisos_basicos:
            permiso_id = await conn.fetchval(
                """
                INSERT INTO permisos (codigo, nombre, descripcion, recurso, accion, fecha_creacion)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (codigo) DO UPDATE SET nombre = $2
                RETURNING id
                """,
                codigo,
                nombre,
                descripcion,
                recurso,
                accion,
                datetime.utcnow()
            )
            permisos_ids.append(permiso_id)
            print(f"  ✓ {codigo}")
        
        # Asignar todos los permisos al rol de Administrador
        for permiso_id in permisos_ids:
            await conn.execute(
                """
                INSERT INTO roles_permisos (rol_id, permiso_id, fecha_asignacion)
                VALUES ($1, $2, $3)
                ON CONFLICT DO NOTHING
                """,
                rol_admin_id,
                permiso_id,
                datetime.utcnow()
            )
        
        print(f"✅ {len(permisos_ids)} permisos asignados al rol 'Administrador'")
        
        # Registrar en auditoría
        await conn.execute(
            """
            INSERT INTO eventos_auditoria (
                usuario_id,
                tipo_evento,
                recurso,
                accion,
                resultado,
                detalles,
                fecha_evento
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            usuario_id,
            "usuario_creado",
            "usuarios",
            "crear",
            "exito",
            f'{{"usuario": "{nombre_usuario}", "origen": "script_inicializacion"}}',
            datetime.utcnow()
        )
        
        print("\n" + "=" * 60)
        print("✅ USUARIO ADMINISTRADOR CREADO EXITOSAMENTE")
        print("=" * 60)
        print(f"\n📋 Credenciales de acceso:")
        print(f"   Usuario: {nombre_usuario}")
        print(f"   Contraseña: {contrasena}")
        print(f"\n🔐 Por seguridad, cambia la contraseña en el primer login")
        print("=" * 60 + "\n")
        
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(crear_usuario_admin())
