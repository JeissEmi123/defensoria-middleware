from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.core.dependencies import get_current_user
from app.database.models import Usuario
from sqlalchemy import text

router = APIRouter(prefix="/api/v1/crud-unificado", tags=["CRUD Unificado"])

@router.get("/categorias-observacion")
async def listar_categorias_observacion(
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(text("""
        SELECT 
            id_categoria_observacion,
            codigo_categoria_observacion,
            nombre_categoria_observacion,
            descripcion_categoria_observacion
        FROM sds.categoria_observacion
        ORDER BY codigo_categoria_observacion
    """))
    return [
        {
            "id_categoria_observacion": row[0],
            "codigo_categoria_observacion": row[1],
            "nombre_categoria_observacion": row[2],
            "descripcion_categoria_observacion": row[3]
        }
        for row in result.fetchall()
    ]

@router.get("/figuras-publicas/categoria/{id_categoria}")
async def listar_figuras_publicas(
    id_categoria: int,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(text("""
        SELECT 
            id_figura_publica,
            nombre_actor,
            peso_actor,
            id_categoria_observacion
        FROM sds.figuras_publicas
        WHERE id_categoria_observacion = :id_categoria
        ORDER BY nombre_actor
    """), {"id_categoria": id_categoria})
    return [
        {
            "id_figura_publica": row[0],
            "nombre_actor": row[1],
            "peso_actor": float(row[2]) if row[2] else None,
            "id_categoria_observacion": row[3]
        }
        for row in result.fetchall()
    ]

@router.get("/medios-digitales/categoria/{id_categoria}")
async def listar_medios_digitales(
    id_categoria: int,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(text("""
        SELECT 
            id_medio_digital,
            nombre_medio_digital,
            peso_medio_digital,
            id_categoria_observacion
        FROM sds.medios_digitales
        WHERE id_categoria_observacion = :id_categoria
        ORDER BY nombre_medio_digital
    """), {"id_categoria": id_categoria})
    return [
        {
            "id_medio_digital": row[0],
            "nombre_medio_digital": row[1],
            "peso_medio_digital": float(row[2]) if row[2] else None,
            "id_categoria_observacion": row[3]
        }
        for row in result.fetchall()
    ]

@router.get("/influencers/categoria/{id_categoria}")
async def listar_influencers(
    id_categoria: int,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(text("""
        SELECT 
            id_influencer,
            nombre_influencer,
            peso_influencer,
            id_categoria_observacion
        FROM sds.influencers
        WHERE id_categoria_observacion = :id_categoria
        ORDER BY nombre_influencer
    """), {"id_categoria": id_categoria})
    return [
        {
            "id_influencer": row[0],
            "nombre_influencer": row[1],
            "peso_influencer": float(row[2]) if row[2] else None,
            "id_categoria_observacion": row[3]
        }
        for row in result.fetchall()
    ]

@router.get("/entidades/categoria/{id_categoria}")
async def listar_entidades(
    id_categoria: int,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(text("""
        SELECT 
            id_entidades,
            nombre_entidad,
            peso_entidad,
            id_categoria_observacion
        FROM sds.entidades
        WHERE id_categoria_observacion = :id_categoria
        ORDER BY nombre_entidad
    """), {"id_categoria": id_categoria})
    return [
        {
            "id_entidad": row[0],
            "nombre_entidad": row[1],
            "peso_entidad": float(row[2]) if row[2] else None,
            "id_categoria_observacion": row[3]
        }
        for row in result.fetchall()
    ]
