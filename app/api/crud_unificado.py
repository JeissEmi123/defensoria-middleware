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

@router.put("/figuras-publicas/{id_figura}")
async def actualizar_figura_publica(
    id_figura: int,
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    await db.execute(text("""
        UPDATE sds.figuras_publicas
        SET nombre_actor = :nombre, peso_actor = :peso
        WHERE id_figura_publica = :id
    """), {"id": id_figura, "nombre": data.get("nombre_actor"), "peso": data.get("peso_actor")})
    await db.commit()
    return {"success": True}

@router.delete("/figuras-publicas/{id_figura}")
async def eliminar_figura_publica(
    id_figura: int,
    db: AsyncSession = Depends(get_db_session)
):
    await db.execute(text("DELETE FROM sds.figuras_publicas WHERE id_figura_publica = :id"), {"id": id_figura})
    await db.commit()
    return {"success": True}

@router.post("/figuras-publicas")
async def crear_figura_publica(
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(text("""
        INSERT INTO sds.figuras_publicas (nombre_actor, peso_actor, id_categoria_observacion)
        VALUES (:nombre, :peso, :id_categoria)
        RETURNING id_figura_publica
    """), {"nombre": data.get("nombre_actor"), "peso": data.get("peso_actor"), "id_categoria": data.get("id_categoria_observacion")})
    await db.commit()
    return {"id_figura_publica": result.scalar()}

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

@router.put("/medios-digitales/{id_medio}")
async def actualizar_medio_digital(
    id_medio: int,
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    await db.execute(text("""
        UPDATE sds.medios_digitales
        SET nombre_medio_digital = :nombre, peso_medio_digital = :peso
        WHERE id_medio_digital = :id
    """), {"id": id_medio, "nombre": data.get("nombre_medio_digital"), "peso": data.get("peso_medio_digital")})
    await db.commit()
    return {"success": True}

@router.delete("/medios-digitales/{id_medio}")
async def eliminar_medio_digital(
    id_medio: int,
    db: AsyncSession = Depends(get_db_session)
):
    await db.execute(text("DELETE FROM sds.medios_digitales WHERE id_medio_digital = :id"), {"id": id_medio})
    await db.commit()
    return {"success": True}

@router.post("/medios-digitales")
async def crear_medio_digital(
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(text("""
        INSERT INTO sds.medios_digitales (nombre_medio_digital, peso_medio_digital, id_categoria_observacion)
        VALUES (:nombre, :peso, :id_categoria)
        RETURNING id_medio_digital
    """), {"nombre": data.get("nombre_medio_digital"), "peso": data.get("peso_medio_digital"), "id_categoria": data.get("id_categoria_observacion")})
    await db.commit()
    return {"id_medio_digital": result.scalar()}

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

@router.put("/influencers/{id_influencer}")
async def actualizar_influencer(
    id_influencer: int,
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    await db.execute(text("""
        UPDATE sds.influencers
        SET nombre_influencer = :nombre, peso_influencer = :peso
        WHERE id_influencer = :id
    """), {"id": id_influencer, "nombre": data.get("nombre_influencer"), "peso": data.get("peso_influencer")})
    await db.commit()
    return {"success": True}

@router.delete("/influencers/{id_influencer}")
async def eliminar_influencer(
    id_influencer: int,
    db: AsyncSession = Depends(get_db_session)
):
    await db.execute(text("DELETE FROM sds.influencers WHERE id_influencer = :id"), {"id": id_influencer})
    await db.commit()
    return {"success": True}

@router.post("/influencers")
async def crear_influencer(
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(text("""
        INSERT INTO sds.influencers (nombre_influencer, peso_influencer, id_categoria_observacion)
        VALUES (:nombre, :peso, :id_categoria)
        RETURNING id_influencer
    """), {"nombre": data.get("nombre_influencer"), "peso": data.get("peso_influencer"), "id_categoria": data.get("id_categoria_observacion")})
    await db.commit()
    return {"id_influencer": result.scalar()}

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

@router.put("/entidades/{id_entidad}")
async def actualizar_entidad(
    id_entidad: int,
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    await db.execute(text("""
        UPDATE sds.entidades
        SET nombre_entidad = :nombre, peso_entidad = :peso
        WHERE id_entidades = :id
    """), {"id": id_entidad, "nombre": data.get("nombre_entidad"), "peso": data.get("peso_entidad")})
    await db.commit()
    return {"success": True}

@router.delete("/entidades/{id_entidad}")
async def eliminar_entidad(
    id_entidad: int,
    db: AsyncSession = Depends(get_db_session)
):
    await db.execute(text("DELETE FROM sds.entidades WHERE id_entidades = :id"), {"id": id_entidad})
    await db.commit()
    return {"success": True}

@router.post("/entidades")
async def crear_entidad(
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(text("""
        INSERT INTO sds.entidades (nombre_entidad, peso_entidad, id_categoria_observacion)
        VALUES (:nombre, :peso, :id_categoria)
        RETURNING id_entidades
    """), {"nombre": data.get("nombre_entidad"), "peso": data.get("peso_entidad"), "id_categoria": data.get("id_categoria_observacion")})
    await db.commit()
    return {"id_entidad": result.scalar()}
