import asyncio
import sys
from pathlib import Path
import click

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.database.session import get_db_session
from app.database.models import Usuario, Rol
from app.core.security import hash_password
from app.core.logging import configure_logging, get_logger
from app.schemas.auth import TipoAutenticacion
from app.services.rbac_service import RBACService

configure_logging()
logger = get_logger(__name__)


@click.group()
def cli():
    pass

@cli.command()
@click.option('--usuario', prompt=True, help='Nombre de usuario')
@click.option('--email', prompt=True, help='Email')
@click.option('--nombre', prompt=True, help='Nombre completo')
@click.option('--contrasena', prompt=True, hide_input=True, confirmation_prompt=True, help='Contraseña')
@click.option('--superuser', is_flag=True, help='Es superusuario')
def crear(usuario, email, nombre, contrasena, superuser):
    async def _crear():
        async for db in get_db_session():
            try:
                # Verificar si existe
                result = await db.execute(
                    select(Usuario).where(Usuario.nombre_usuario == usuario)
                )
                if result.scalar_one_or_none():
                    click.echo(f" El usuario '{usuario}' ya existe")
                    return
                # Crear usuario
                nuevo_usuario = Usuario(
                    nombre_usuario=usuario,
                    email=email,
                    nombre_completo=nombre,
                    contrasena_hash=hash_password(contrasena),
                    es_superusuario=superuser,
                    activo=True,
                    tipo_autenticacion=TipoAutenticacion.LOCAL
                )
                
                db.add(nuevo_usuario)
                await db.commit()
                await db.refresh(nuevo_usuario)
                
                click.echo(f" Usuario '{usuario}' creado exitosamente (ID: {nuevo_usuario.id})")
                
            except Exception as e:
                click.echo(f" Error: {str(e)}")
            finally:
                break
    
    asyncio.run(_crear())


@cli.command()
def listar():
    async def _listar():
        async for db in get_db_session():
            try:
                result = await db.execute(select(Usuario))
                usuarios = result.scalars().all()
                if not usuarios:
                    click.echo("No hay usuarios registrados")
                    return
                
                click.echo("\n" + "="*100)
                click.echo(f"{'ID':<5} {'Usuario':<20} {'Email':<30} {'Nombre':<25} {'Activo':<7} {'Super':<6}")
                click.echo("="*100)
                
                for user in usuarios:
                    click.echo(
                        f"{user.id:<5} "
                        f"{user.nombre_usuario:<20} "
                        f"{user.email or 'N/A':<30} "
                        f"{user.nombre_completo or 'N/A':<25} "
                        f"{'Sí' if user.activo else 'No':<7} "
                        f"{'Sí' if user.es_superusuario else 'No':<6}"
                    )
                
                click.echo("="*100 + "\n")
                
            except Exception as e:
                click.echo(f" Error: {str(e)}")
            finally:
                break
    
    asyncio.run(_listar())


@cli.command()
@click.argument('usuario_id', type=int)
@click.option('--email', help='Nuevo email')
@click.option('--nombre', help='Nuevo nombre completo')
@click.option('--activo', type=bool, help='Estado activo (True/False)')
def actualizar(usuario_id, email, nombre, activo):
    async def _actualizar():
        async for db in get_db_session():
            try:
                result = await db.execute(
                    select(Usuario).where(Usuario.id == usuario_id)
                )
                usuario = result.scalar_one_or_none()
                if not usuario:
                    click.echo(f" Usuario con ID {usuario_id} no encontrado")
                    return
                
                # Actualizar campos
                if email:
                    usuario.email = email
                if nombre:
                    usuario.nombre_completo = nombre
                if activo is not None:
                    usuario.activo = activo
                
                await db.commit()
                click.echo(f" Usuario '{usuario.nombre_usuario}' actualizado")
                
            except Exception as e:
                click.echo(f" Error: {str(e)}")
            finally:
                break
    
    asyncio.run(_actualizar())


@cli.command()
@click.argument('usuario_id', type=int)
@click.option('--contrasena', prompt=True, hide_input=True, confirmation_prompt=True, help='Nueva contraseña')
def cambiar_contrasena(usuario_id, contrasena):
    async def _cambiar():
        async for db in get_db_session():
            try:
                result = await db.execute(
                    select(Usuario).where(Usuario.id == usuario_id)
                )
                usuario = result.scalar_one_or_none()
                if not usuario:
                    click.echo(f" Usuario con ID {usuario_id} no encontrado")
                    return
                
                usuario.contrasena_hash = hash_password(contrasena)
                await db.commit()
                
                click.echo(f" Contraseña de '{usuario.nombre_usuario}' actualizada")
                
            except Exception as e:
                click.echo(f" Error: {str(e)}")
            finally:
                break
    
    asyncio.run(_cambiar())


@cli.command()
@click.argument('usuario_id', type=int)
@click.argument('rol_nombre')
def asignar_rol(usuario_id, rol_nombre):
    async def _asignar():
        async for db in get_db_session():
            try:
                # Verificar usuario
                result = await db.execute(
                    select(Usuario).where(Usuario.id == usuario_id)
                )
                usuario = result.scalar_one_or_none()
                if not usuario:
                    click.echo(f" Usuario con ID {usuario_id} no encontrado")
                    return
                
                # Buscar rol
                result = await db.execute(
                    select(Rol).where(Rol.nombre == rol_nombre)
                )
                rol = result.scalar_one_or_none()
                
                if not rol:
                    click.echo(f" Rol '{rol_nombre}' no encontrado")
                    return
                
                # Asignar rol usando RBACService
                rbac_service = RBACService(db)
                await rbac_service.asignar_roles_a_usuario(
                    usuario_id,
                    [rol.id],
                    1  # System user
                )
                
                click.echo(f" Rol '{rol_nombre}' asignado a '{usuario.nombre_usuario}'")
                
            except Exception as e:
                click.echo(f" Error: {str(e)}")
            finally:
                break
    
    asyncio.run(_asignar())


@cli.command()
@click.argument('usuario_id', type=int)
def ver_roles(usuario_id):
    async def _ver():
        async for db in get_db_session():
            try:
                rbac_service = RBACService(db)
                roles = await rbac_service.obtener_roles_usuario(usuario_id)
                if not roles:
                    click.echo(f"El usuario no tiene roles asignados")
                    return
                
                click.echo("\nRoles asignados:")
                click.echo("="*60)
                for rol in roles:
                    click.echo(f"  • {rol.nombre}: {rol.descripcion}")
                click.echo("="*60 + "\n")
                
            except Exception as e:
                click.echo(f" Error: {str(e)}")
            finally:
                break
    
    asyncio.run(_ver())


@cli.command()
def listar_roles():
    async def _listar():
        async for db in get_db_session():
            try:
                result = await db.execute(select(Rol))
                roles = result.scalars().all()
                if not roles:
                    click.echo("No hay roles registrados")
                    return
                
                click.echo("\n" + "="*80)
                click.echo(f"{'ID':<5} {'Nombre':<20} {'Descripción':<40} {'Sistema':<8}")
                click.echo("="*80)
                
                for rol in roles:
                    click.echo(
                        f"{rol.id:<5} "
                        f"{rol.nombre:<20} "
                        f"{(rol.descripcion or 'N/A')[:40]:<40} "
                        f"{'Sí' if rol.es_sistema else 'No':<8}"
                    )
                
                click.echo("="*80 + "\n")
                
            except Exception as e:
                click.echo(f" Error: {str(e)}")
            finally:
                break
    
    asyncio.run(_listar())


if __name__ == '__main__':
    cli()
