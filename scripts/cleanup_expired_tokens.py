import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import click

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, and_, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.database.models import Sesion, Usuario
from app.core.logging import get_logger, configure_logging

configure_logging()
logger = get_logger(__name__)


class TokenCleanupService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def limpiar_sesiones_expiradas(self, dias_retencion: int = 30) -> dict:
        fecha_limite = datetime.utcnow() - timedelta(days=dias_retencion)
        
        # Contar sesiones a eliminar
        count_query = select(func.count(Sesion.id)).where(
            and_(
                Sesion.valida == False,
                Sesion.fecha_expiracion < fecha_limite
            )
        )
        result = await self.db.execute(count_query)
        count_invalidas = result.scalar()
        
        # Eliminar sesiones inválidas antiguas
        delete_invalidas = delete(Sesion).where(
            and_(
                Sesion.valida == False,
                Sesion.fecha_expiracion < fecha_limite
            )
        )
        await self.db.execute(delete_invalidas)
        
        # Contar sesiones expiradas válidas (inconsistencia)
        count_expiradas_query = select(func.count(Sesion.id)).where(
            and_(
                Sesion.valida == True,
                Sesion.fecha_expiracion < datetime.utcnow()
            )
        )
        result = await self.db.execute(count_expiradas_query)
        count_expiradas = result.scalar()
        
        # Marcar como inválidas las sesiones expiradas
        if count_expiradas > 0:
            result = await self.db.execute(
                select(Sesion).where(
                    and_(
                        Sesion.valida == True,
                        Sesion.fecha_expiracion < datetime.utcnow()
                    )
                )
            )
            sesiones_expiradas = result.scalars().all()
            
            for sesion in sesiones_expiradas:
                sesion.valida = False
                sesion.fecha_invalidacion = datetime.utcnow()
                sesion.razon_invalidacion = "expirada_automaticamente"
        
        await self.db.commit()
        
        logger.info(
            "sesiones_limpiadas",
            sesiones_eliminadas=count_invalidas,
            sesiones_marcadas_invalidas=count_expiradas,
            dias_retencion=dias_retencion
        )
        
        return {
            "sesiones_eliminadas": count_invalidas,
            "sesiones_marcadas_invalidas": count_expiradas,
            "total_procesadas": count_invalidas + count_expiradas
        }
    
    async def limpiar_tokens_reset_expirados(self, dias_retencion: int = 7) -> dict:
        fecha_limite = datetime.utcnow() - timedelta(days=dias_retencion)
        
        # Contar tokens expirados
        count_query = select(func.count(Usuario.id)).where(
            and_(
                Usuario.reset_token.isnot(None),
                Usuario.reset_token_expira < fecha_limite
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar()
        
        # Limpiar tokens expirados
        result = await self.db.execute(
            select(Usuario).where(
                and_(
                    Usuario.reset_token.isnot(None),
                    Usuario.reset_token_expira < fecha_limite
                )
            )
        )
        usuarios = result.scalars().all()
        
        for usuario in usuarios:
            usuario.reset_token = None
            usuario.reset_token_expira = None
        
        await self.db.commit()
        
        logger.info(
            "tokens_reset_limpiados",
            tokens_eliminados=count,
            dias_retencion=dias_retencion
        )
        
        return {
            "tokens_eliminados": count
        }
    
    async def obtener_estadisticas(self) -> dict:
        # Sesiones totales
        result = await self.db.execute(select(func.count(Sesion.id)))
        total_sesiones = result.scalar()
        
        # Sesiones activas
        result = await self.db.execute(
            select(func.count(Sesion.id)).where(Sesion.valida == True)
        )
        sesiones_activas = result.scalar()
        
        # Sesiones expiradas pero marcadas como válidas (inconsistencia)
        result = await self.db.execute(
            select(func.count(Sesion.id)).where(
                and_(
                    Sesion.valida == True,
                    Sesion.fecha_expiracion < datetime.utcnow()
                )
            )
        )
        sesiones_inconsistentes = result.scalar()
        
        # Tokens de reset activos
        result = await self.db.execute(
            select(func.count(Usuario.id)).where(
                and_(
                    Usuario.reset_token.isnot(None),
                    Usuario.reset_token_expira > datetime.utcnow()
                )
            )
        )
        tokens_reset_activos = result.scalar()
        
        # Tokens de reset expirados
        result = await self.db.execute(
            select(func.count(Usuario.id)).where(
                and_(
                    Usuario.reset_token.isnot(None),
                    Usuario.reset_token_expira < datetime.utcnow()
                )
            )
        )
        tokens_reset_expirados = result.scalar()
        
        return {
            "sesiones": {
                "total": total_sesiones,
                "activas": sesiones_activas,
                "inactivas": total_sesiones - sesiones_activas,
                "inconsistentes": sesiones_inconsistentes
            },
            "tokens_reset": {
                "activos": tokens_reset_activos,
                "expirados": tokens_reset_expirados,
                "total": tokens_reset_activos + tokens_reset_expirados
            }
        }


@click.command()
@click.option(
    '--dry-run',
    is_flag=True,
    help='Mostrar qué se eliminaría sin hacer cambios'
)
@click.option(
    '--days',
    default=30,
    type=int,
    help='Días de retención para sesiones expiradas (default: 30)'
)
@click.option(
    '--reset-days',
    default=7,
    type=int,
    help='Días de retención para tokens de reset (default: 7)'
)
@click.option(
    '--stats',
    is_flag=True,
    help='Solo mostrar estadísticas sin limpiar'
)
def main(dry_run: bool, days: int, reset_days: int, stats: bool):
    async def _ejecutar():
        click.echo("=" * 60)
        click.echo(" Limpieza de Tokens y Sesiones Expiradas")
        click.echo("=" * 60)
        click.echo()
        
        async for db in get_db_session():
            try:
                service = TokenCleanupService(db)
                
                # Obtener estadísticas
                click.echo(" Estadísticas antes de la limpieza:")
                click.echo("-" * 60)
                stats_antes = await service.obtener_estadisticas()
                
                click.echo(f"Sesiones totales: {stats_antes['sesiones']['total']}")
                click.echo(f"   Activas: {stats_antes['sesiones']['activas']}")
                click.echo(f"   Inactivas: {stats_antes['sesiones']['inactivas']}")
                click.echo(f"    Inconsistentes: {stats_antes['sesiones']['inconsistentes']}")
                click.echo()
                click.echo(f"Tokens de reset: {stats_antes['tokens_reset']['total']}")
                click.echo(f"   Activos: {stats_antes['tokens_reset']['activos']}")
                click.echo(f"   Expirados: {stats_antes['tokens_reset']['expirados']}")
                click.echo()
                
                if stats:
                    click.echo(" Solo estadísticas solicitadas. No se realizó limpieza.")
                    return
                
                if dry_run:
                    click.echo(" MODO DRY-RUN (sin cambios)")
                    click.echo()
                    click.echo(f"Se eliminarían aproximadamente:")
                    click.echo(f"  - Sesiones inválidas > {days} días")
                    click.echo(f"  - Tokens de reset > {reset_days} días")
                    click.echo()
                    click.echo("Ejecuta sin --dry-run para aplicar cambios.")
                    return
                
                # Limpiar sesiones
                click.echo(" Limpiando sesiones expiradas...")
                resultado_sesiones = await service.limpiar_sesiones_expiradas(days)
                click.echo(f"   Sesiones eliminadas: {resultado_sesiones['sesiones_eliminadas']}")
                click.echo(f"   Sesiones marcadas como inválidas: {resultado_sesiones['sesiones_marcadas_invalidas']}")
                click.echo()
                
                # Limpiar tokens de reset
                click.echo(" Limpiando tokens de reset expirados...")
                resultado_tokens = await service.limpiar_tokens_reset_expirados(reset_days)
                click.echo(f"   Tokens eliminados: {resultado_tokens['tokens_eliminados']}")
                click.echo()
                
                # Estadísticas después
                click.echo(" Estadísticas después de la limpieza:")
                click.echo("-" * 60)
                stats_despues = await service.obtener_estadisticas()
                
                click.echo(f"Sesiones totales: {stats_despues['sesiones']['total']}")
                click.echo(f"   Activas: {stats_despues['sesiones']['activas']}")
                click.echo(f"   Inactivas: {stats_despues['sesiones']['inactivas']}")
                click.echo()
                click.echo(f"Tokens de reset: {stats_despues['tokens_reset']['total']}")
                click.echo(f"   Activos: {stats_despues['tokens_reset']['activos']}")
                click.echo(f"   Expirados: {stats_despues['tokens_reset']['expirados']}")
                click.echo()
                
                click.echo("=" * 60)
                click.echo(" Limpieza completada exitosamente")
                click.echo("=" * 60)
                
            except Exception as e:
                logger.error("error_limpieza_tokens", error=str(e))
                click.echo(f" Error: {str(e)}", err=True)
                sys.exit(1)
            
            break  # Solo usar la primera sesión
    
    asyncio.run(_ejecutar())


if __name__ == "__main__":
    main()
