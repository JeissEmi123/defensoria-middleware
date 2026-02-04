from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.core.dependencies import get_current_user
from app.database.models import Usuario
from app.services.senal_service_v2 import SenalServiceV2

router = APIRouter(prefix="/admin-modelo", tags=["Admin Modelo"])

@router.get("/categorias-analisis")
async def listar_categorias_analisis(
    db: AsyncSession = Depends(get_db_session)
):
    service = SenalServiceV2(db)
    categorias = await service.listar_categorias_analisis()
    return [
        {
            "id_categoria_analisis_senal": cat.id_categoria_analisis_senal,
            "nombre_categoria_analisis": cat.nombre_categoria_analisis,
            "descripcion_categoria_analisis": cat.descripcion_categoria_analisis,
        }
        for cat in categorias
    ]

@router.get("/categorias-analisis/{id_categoria}")
async def obtener_categoria_analisis(
    id_categoria: int,
    db: AsyncSession = Depends(get_db_session)
):
    service = SenalServiceV2(db)
    categorias = await service.listar_categorias_analisis(id_categoria)
    if not categorias:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    cat = categorias[0]
    return {
        "id_categoria_analisis_senal": cat.id_categoria_analisis_senal,
        "nombre_categoria_analisis": cat.nombre_categoria_analisis,
        "descripcion_categoria_analisis": cat.descripcion_categoria_analisis,
    }
