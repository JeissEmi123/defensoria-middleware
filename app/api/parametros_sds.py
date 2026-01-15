"""
Endpoints CRUD para la configuración de parámetros SDS (categorías y catálogos).
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.models import Usuario
from app.database.models_sds import (
    CategoriaAnalisisSenal,
    CategoriaObservacion,
    CategoriaSenal,
    ConductaVulneratoria,
    Entidad,
    Emoticon,
    FiguraPublica,
    FraseClave,
    Influencer,
    MedioDigital,
    PalabraClave,
    SenalDetectada,
)
from app.database.session import get_db_session
from app.schemas.parametros_sds import (
    CategoriaAnalisisCreate,
    CategoriaAnalisisResponse,
    CategoriaAnalisisUpdate,
    CategoriaSenalCreate,
    CategoriaSenalResponse,
    CategoriaSenalUpdate,
    ConductaVulneratoriaCreate,
    ConductaVulneratoriaResponse,
    ConductaVulneratoriaUpdate,
    EmoticonCreate,
    EmoticonResponse,
    EmoticonUpdate,
    EntidadCreate,
    EntidadResponse,
    EntidadUpdate,
    FiguraPublicaCreate,
    FiguraPublicaResponse,
    FiguraPublicaUpdate,
    FraseClaveCreate,
    FraseClaveResponse,
    FraseClaveUpdate,
    InfluencerCreate,
    InfluencerResponse,
    InfluencerUpdate,
    MedioDigitalCreate,
    MedioDigitalResponse,
    MedioDigitalUpdate,
    PalabraClaveCreate,
    PalabraClaveResponse,
    PalabraClaveUpdate,
)

router = APIRouter(prefix="/api/v2/parametros", tags=["Parámetros SDS"])


async def _get_or_404(db: AsyncSession, model, id_column, value, description: str):
    result = await db.execute(select(model).where(id_column == value))
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail=f"{description} no encontrada")
    return entity


async def _next_id(db: AsyncSession, column):
    result = await db.execute(select(func.coalesce(func.max(column), 0) + 1))
    return result.scalar()


async def _ensure_unique(
    db: AsyncSession,
    model,
    column,
    value: str,
    description: str,
    id_column=None,
    current_id=None,
):
    if not value:
        return
    query = select(model).where(func.lower(column) == value.lower())
    if id_column is not None and current_id is not None:
        query = query.where(id_column != current_id)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"{description} ya existe")


async def _ensure_categoria_analisis_exists(db: AsyncSession, categoria_id: int):
    await _get_or_404(db, CategoriaAnalisisSenal, CategoriaAnalisisSenal.id_categoria_analisis_senal, categoria_id, "Categoría de análisis")


async def _ensure_categoria_observacion_exists(db: AsyncSession, categoria_id: Optional[int]):
    if categoria_id is None:
        return
    await _get_or_404(db, CategoriaObservacion, CategoriaObservacion.id_categoria_observacion, categoria_id, "Categoría de observación")


@router.get("/categorias-analisis", response_model=List[CategoriaAnalisisResponse])
async def listar_categorias_analisis(
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    query = select(CategoriaAnalisisSenal).order_by(CategoriaAnalisisSenal.nombre_categoria_analisis)
    result = await db.execute(query)
    categorias = result.scalars().all()
    return [CategoriaAnalisisResponse.model_validate(item) for item in categorias]


@router.get("/categorias-analisis/{id_categoria}", response_model=CategoriaAnalisisResponse)
async def obtener_categoria_analisis(
    id_categoria: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    categoria = await _get_or_404(
        db,
        CategoriaAnalisisSenal,
        CategoriaAnalisisSenal.id_categoria_analisis_senal,
        id_categoria,
        "Categoría de análisis",
    )
    return CategoriaAnalisisResponse.model_validate(categoria)


@router.post("/categorias-analisis", response_model=CategoriaAnalisisResponse, status_code=status.HTTP_201_CREATED)
async def crear_categoria_analisis(
    payload: CategoriaAnalisisCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    await _ensure_unique(
        db,
        CategoriaAnalisisSenal,
        CategoriaAnalisisSenal.nombre_categoria_analisis,
        payload.nombre_categoria_analisis,
        "Categoría de análisis",
    )
    nuevo_id = await _next_id(db, CategoriaAnalisisSenal.id_categoria_analisis_senal)
    categoria = CategoriaAnalisisSenal(
        id_categoria_analisis_senal=nuevo_id,
        **payload.model_dump(),
    )
    db.add(categoria)
    try:
        await db.commit()
        await db.refresh(categoria)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error al crear categoría de análisis")
    return CategoriaAnalisisResponse.model_validate(categoria)


@router.put("/categorias-analisis/{id_categoria}", response_model=CategoriaAnalisisResponse)
async def actualizar_categoria_analisis(
    id_categoria: int,
    payload: CategoriaAnalisisUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    categoria = await _get_or_404(
        db,
        CategoriaAnalisisSenal,
        CategoriaAnalisisSenal.id_categoria_analisis_senal,
        id_categoria,
        "Categoría de análisis",
    )
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Debe enviar al menos un campo para actualizar")
    if "nombre_categoria_analisis" in updates:
        await _ensure_unique(
            db,
            CategoriaAnalisisSenal,
            CategoriaAnalisisSenal.nombre_categoria_analisis,
            updates["nombre_categoria_analisis"],
            "Categoría de análisis",
            id_column=CategoriaAnalisisSenal.id_categoria_analisis_senal,
            current_id=id_categoria,
        )
    for field, value in updates.items():
        setattr(categoria, field, value)
    await db.commit()
    await db.refresh(categoria)
    return CategoriaAnalisisResponse.model_validate(categoria)


@router.delete("/categorias-analisis/{id_categoria}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_categoria_analisis(
    id_categoria: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    categoria = await _get_or_404(
        db,
        CategoriaAnalisisSenal,
        CategoriaAnalisisSenal.id_categoria_analisis_senal,
        id_categoria,
        "Categoría de análisis",
    )
    try:
        await db.delete(categoria)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="No se puede eliminar, tiene dependencias")


@router.get("/conductas-vulneratorias", response_model=List[ConductaVulneratoriaResponse])
async def listar_conductas_vulneratorias(
    id_categoria_analisis_senal: Optional[int] = Query(None, description="Filtrar por categoría de análisis"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    query = select(ConductaVulneratoria).order_by(ConductaVulneratoria.nombre_conducta)
    if id_categoria_analisis_senal is not None:
        query = query.where(ConductaVulneratoria.id_categoria_analisis_senal == id_categoria_analisis_senal)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/conductas-vulneratorias", response_model=ConductaVulneratoriaResponse, status_code=status.HTTP_201_CREATED)
async def crear_conducta_vulneratoria(
    payload: ConductaVulneratoriaCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    await _ensure_categoria_analisis_exists(db, payload.id_categoria_analisis_senal)
    conducta = ConductaVulneratoria(**payload.model_dump())
    db.add(conducta)
    try:
        await db.commit()
        await db.refresh(conducta)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error al crear conducta vulneratoria")
    return conducta


@router.put("/conductas-vulneratorias/{id_conducta}", response_model=ConductaVulneratoriaResponse)
async def actualizar_conducta_vulneratoria(
    id_conducta: int,
    payload: ConductaVulneratoriaUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    conducta = await _get_or_404(
        db,
        ConductaVulneratoria,
        ConductaVulneratoria.id_conducta_vulneratoria,
        id_conducta,
        "Conducta vulneratoria",
    )
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Debe enviar al menos un campo para actualizar")
    if "id_categoria_analisis_senal" in updates:
        await _ensure_categoria_analisis_exists(db, updates["id_categoria_analisis_senal"])
    for field, value in updates.items():
        setattr(conducta, field, value)
    await db.commit()
    await db.refresh(conducta)
    return conducta


@router.delete("/conductas-vulneratorias/{id_conducta}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_conducta_vulneratoria(
    id_conducta: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    conducta = await _get_or_404(
        db,
        ConductaVulneratoria,
        ConductaVulneratoria.id_conducta_vulneratoria,
        id_conducta,
        "Conducta vulneratoria",
    )
    await db.delete(conducta)
    await db.commit()


@router.get("/palabras-clave", response_model=List[PalabraClaveResponse])
async def listar_palabras_clave(
    id_categoria_analisis_senal: Optional[int] = Query(None, description="Filtrar por categoría de análisis"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    query = select(PalabraClave).order_by(PalabraClave.palabra_clave)
    if id_categoria_analisis_senal is not None:
        query = query.where(PalabraClave.id_categoria_analisis_senal == id_categoria_analisis_senal)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/palabras-clave", response_model=PalabraClaveResponse, status_code=status.HTTP_201_CREATED)
async def crear_palabra_clave(
    payload: PalabraClaveCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    await _ensure_categoria_analisis_exists(db, payload.id_categoria_analisis_senal)
    palabra = PalabraClave(**payload.model_dump())
    db.add(palabra)
    try:
        await db.commit()
        await db.refresh(palabra)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error al crear palabra clave")
    return palabra


@router.put("/palabras-clave/{id_palabra}", response_model=PalabraClaveResponse)
async def actualizar_palabra_clave(
    id_palabra: int,
    payload: PalabraClaveUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    palabra = await _get_or_404(
        db,
        PalabraClave,
        PalabraClave.id_palabra_clave,
        id_palabra,
        "Palabra clave",
    )
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Debe enviar al menos un campo para actualizar")
    if "id_categoria_analisis_senal" in updates:
        await _ensure_categoria_analisis_exists(db, updates["id_categoria_analisis_senal"])
    for field, value in updates.items():
        setattr(palabra, field, value)
    await db.commit()
    await db.refresh(palabra)
    return palabra


@router.delete("/palabras-clave/{id_palabra}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_palabra_clave(
    id_palabra: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    palabra = await _get_or_404(
        db,
        PalabraClave,
        PalabraClave.id_palabra_clave,
        id_palabra,
        "Palabra clave",
    )
    await db.delete(palabra)
    await db.commit()


@router.get("/emoticonos", response_model=List[EmoticonResponse])
async def listar_emoticonos(
    id_categoria_analisis_senal: Optional[int] = Query(None, description="Filtrar por categoría de análisis"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    query = select(Emoticon).order_by(Emoticon.codigo_emoticon)
    if id_categoria_analisis_senal is not None:
        query = query.where(Emoticon.id_categoria_analisis_senal == id_categoria_analisis_senal)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/emoticonos", response_model=EmoticonResponse, status_code=status.HTTP_201_CREATED)
async def crear_emoticono(
    payload: EmoticonCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    await _ensure_categoria_analisis_exists(db, payload.id_categoria_analisis_senal)
    emoticono = Emoticon(**payload.model_dump())
    db.add(emoticono)
    try:
        await db.commit()
        await db.refresh(emoticono)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error al crear emoticono")
    return emoticono


@router.put("/emoticonos/{id_emoticon}", response_model=EmoticonResponse)
async def actualizar_emoticono(
    id_emoticon: int,
    payload: EmoticonUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    emoticono = await _get_or_404(
        db,
        Emoticon,
        Emoticon.id_emoticon,
        id_emoticon,
        "Emoticono",
    )
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Debe enviar al menos un campo para actualizar")
    if "id_categoria_analisis_senal" in updates:
        await _ensure_categoria_analisis_exists(db, updates["id_categoria_analisis_senal"])
    for field, value in updates.items():
        setattr(emoticono, field, value)
    await db.commit()
    await db.refresh(emoticono)
    return emoticono


@router.delete("/emoticonos/{id_emoticon}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_emoticono(
    id_emoticon: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    emoticono = await _get_or_404(
        db,
        Emoticon,
        Emoticon.id_emoticon,
        id_emoticon,
        "Emoticono",
    )
    await db.delete(emoticono)
    await db.commit()


@router.get("/frases-clave", response_model=List[FraseClaveResponse])
async def listar_frases_clave(
    id_categoria_analisis_senal: Optional[int] = Query(None, description="Filtrar por categoría de análisis"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    query = select(FraseClave).order_by(FraseClave.frase)
    if id_categoria_analisis_senal is not None:
        query = query.where(FraseClave.id_categoria_analisis_senal == id_categoria_analisis_senal)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/frases-clave", response_model=FraseClaveResponse, status_code=status.HTTP_201_CREATED)
async def crear_frase_clave(
    payload: FraseClaveCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    await _ensure_categoria_analisis_exists(db, payload.id_categoria_analisis_senal)
    frase = FraseClave(**payload.model_dump())
    db.add(frase)
    try:
        await db.commit()
        await db.refresh(frase)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error al crear frase clave")
    return frase


@router.put("/frases-clave/{id_frase}", response_model=FraseClaveResponse)
async def actualizar_frase_clave(
    id_frase: int,
    payload: FraseClaveUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    frase = await _get_or_404(
        db,
        FraseClave,
        FraseClave.id_frase_clave,
        id_frase,
        "Frase clave",
    )
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Debe enviar al menos un campo para actualizar")
    if "id_categoria_analisis_senal" in updates:
        await _ensure_categoria_analisis_exists(db, updates["id_categoria_analisis_senal"])
    for field, value in updates.items():
        setattr(frase, field, value)
    await db.commit()
    await db.refresh(frase)
    return frase


@router.delete("/frases-clave/{id_frase}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_frase_clave(
    id_frase: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    frase = await _get_or_404(
        db,
        FraseClave,
        FraseClave.id_frase_clave,
        id_frase,
        "Frase clave",
    )
    await db.delete(frase)
    await db.commit()


@router.get("/categorias-senal", response_model=List[CategoriaSenalResponse])
async def listar_categorias_senal(
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    query = select(CategoriaSenal).order_by(CategoriaSenal.nivel, CategoriaSenal.nombre_categoria_senal)
    result = await db.execute(query)
    categorias = result.scalars().all()
    return [CategoriaSenalResponse.model_validate(item) for item in categorias]


@router.post("/categorias-senal", response_model=CategoriaSenalResponse, status_code=status.HTTP_201_CREATED)
async def crear_categoria_senal(
    payload: CategoriaSenalCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    await _ensure_unique(
        db,
        CategoriaSenal,
        CategoriaSenal.nombre_categoria_senal,
        payload.nombre_categoria_senal,
        "Categoría de señal",
    )
    if payload.id_parent_categoria_senales is not None:
        await _get_or_404(
            db,
            CategoriaSenal,
            CategoriaSenal.id_categoria_senal,
            payload.id_parent_categoria_senales,
            "Categoría padre",
        )
    nuevo_id = await _next_id(db, CategoriaSenal.id_categoria_senal)
    payload_data = payload.model_dump(exclude_unset=True)
    categoria_data = {
        "nombre_categoria_senal": payload_data.get("nombre_categoria_senal"),
        "descripcion": payload_data.get("descripcion_categoria_senal"),
        "color": payload_data.get("color_categoria"),
        "nivel": payload_data.get("nivel"),
        "parent_categoria_senal_id": payload_data.get("id_parent_categoria_senales"),
    }
    categoria = CategoriaSenal(
        id_categoria_senal=nuevo_id,
        **{k: v for k, v in categoria_data.items() if v is not None},
    )
    db.add(categoria)
    try:
        await db.commit()
        await db.refresh(categoria)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error al crear categoría de señal")
    return CategoriaSenalResponse.model_validate(categoria)


@router.put("/categorias-senal/{id_categoria}", response_model=CategoriaSenalResponse)
async def actualizar_categoria_senal(
    id_categoria: int,
    payload: CategoriaSenalUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    categoria = await _get_or_404(
        db,
        CategoriaSenal,
        CategoriaSenal.id_categoria_senal,
        id_categoria,
        "Categoría de señal",
    )
    raw_updates = payload.model_dump(exclude_unset=True)
    updates = {}
    if "nombre_categoria_senal" in raw_updates:
        updates["nombre_categoria_senal"] = raw_updates["nombre_categoria_senal"]
    if "descripcion_categoria_senal" in raw_updates:
        updates["descripcion"] = raw_updates["descripcion_categoria_senal"]
    if "color_categoria" in raw_updates:
        updates["color"] = raw_updates["color_categoria"]
    if "nivel" in raw_updates:
        updates["nivel"] = raw_updates["nivel"]
    if "id_parent_categoria_senales" in raw_updates:
        updates["parent_categoria_senal_id"] = raw_updates["id_parent_categoria_senales"]
    if not updates:
        raise HTTPException(status_code=400, detail="Debe enviar al menos un campo para actualizar")
    if "nombre_categoria_senal" in updates:
        await _ensure_unique(
            db,
            CategoriaSenal,
            CategoriaSenal.nombre_categoria_senal,
            updates["nombre_categoria_senal"],
            "Categoría de señal",
            id_column=CategoriaSenal.id_categoria_senal,
            current_id=id_categoria,
        )
    if "parent_categoria_senal_id" in updates and updates["parent_categoria_senal_id"] is not None:
        await _get_or_404(
            db,
            CategoriaSenal,
            CategoriaSenal.id_categoria_senal,
            updates["parent_categoria_senal_id"],
            "Categoría padre",
        )
    for field, value in updates.items():
        setattr(categoria, field, value)
    await db.commit()
    await db.refresh(categoria)
    return CategoriaSenalResponse.model_validate(categoria)


@router.delete("/categorias-senal/{id_categoria}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_categoria_senal(
    id_categoria: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    categoria = await _get_or_404(
        db,
        CategoriaSenal,
        CategoriaSenal.id_categoria_senal,
        id_categoria,
        "Categoría de señal",
    )
    result = await db.execute(
        select(func.count())
        .select_from(SenalDetectada)
        .where(SenalDetectada.id_categoria_senal == id_categoria)
    )
    total = result.scalar()
    if total > 0:
        raise HTTPException(status_code=400, detail="La categoría tiene señales asociadas")
    try:
        await db.delete(categoria)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="No se puede eliminar la categoría")


@router.get("/figuras-publicas", response_model=List[FiguraPublicaResponse])
async def listar_figuras_publicas(
    id_categoria_observacion: Optional[int] = Query(None, description="Filtrar por categoría de observación"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    query = select(FiguraPublica).order_by(FiguraPublica.nombre_actor)
    if id_categoria_observacion is not None:
        query = query.where(FiguraPublica.id_categoria_observacion == id_categoria_observacion)
    result = await db.execute(query)
    figuras = result.scalars().all()
    return [FiguraPublicaResponse.model_validate(item) for item in figuras]


@router.post("/figuras-publicas", response_model=FiguraPublicaResponse, status_code=status.HTTP_201_CREATED)
async def crear_figura_publica(
    payload: FiguraPublicaCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    await _ensure_categoria_observacion_exists(db, payload.id_categoria_observacion)
    nuevo_id = await _next_id(db, FiguraPublica.id_figura_publica)
    figura = FiguraPublica(id_figura_publica=nuevo_id, **payload.model_dump())
    db.add(figura)
    await db.commit()
    await db.refresh(figura)
    return FiguraPublicaResponse.model_validate(figura)


@router.put("/figuras-publicas/{id_figura}", response_model=FiguraPublicaResponse)
async def actualizar_figura_publica(
    id_figura: int,
    payload: FiguraPublicaUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    figura = await _get_or_404(
        db,
        FiguraPublica,
        FiguraPublica.id_figura_publica,
        id_figura,
        "Figura pública",
    )
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Debe enviar al menos un campo para actualizar")
    if "id_categoria_observacion" in updates:
        await _ensure_categoria_observacion_exists(db, updates["id_categoria_observacion"])
    for field, value in updates.items():
        setattr(figura, field, value)
    await db.commit()
    await db.refresh(figura)
    return FiguraPublicaResponse.model_validate(figura)


@router.delete("/figuras-publicas/{id_figura}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_figura_publica(
    id_figura: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    figura = await _get_or_404(
        db,
        FiguraPublica,
        FiguraPublica.id_figura_publica,
        id_figura,
        "Figura pública",
    )
    await db.delete(figura)
    await db.commit()


@router.get("/influencers", response_model=List[InfluencerResponse])
async def listar_influencers(
    id_categoria_observacion: Optional[int] = Query(None, description="Filtrar por categoría de observación"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    query = select(Influencer).order_by(Influencer.nombre_influencer)
    if id_categoria_observacion is not None:
        query = query.where(Influencer.id_categoria_observacion == id_categoria_observacion)
    result = await db.execute(query)
    influencers = result.scalars().all()
    return [InfluencerResponse.model_validate(item) for item in influencers]


@router.post("/influencers", response_model=InfluencerResponse, status_code=status.HTTP_201_CREATED)
async def crear_influencer(
    payload: InfluencerCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    await _ensure_categoria_observacion_exists(db, payload.id_categoria_observacion)
    nuevo_id = await _next_id(db, Influencer.id_influencer)
    influencer = Influencer(id_influencer=nuevo_id, **payload.model_dump())
    db.add(influencer)
    await db.commit()
    await db.refresh(influencer)
    return InfluencerResponse.model_validate(influencer)


@router.put("/influencers/{id_influencer}", response_model=InfluencerResponse)
async def actualizar_influencer(
    id_influencer: int,
    payload: InfluencerUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    influencer = await _get_or_404(
        db,
        Influencer,
        Influencer.id_influencer,
        id_influencer,
        "Influencer",
    )
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Debe enviar al menos un campo para actualizar")
    if "id_categoria_observacion" in updates:
        await _ensure_categoria_observacion_exists(db, updates["id_categoria_observacion"])
    for field, value in updates.items():
        setattr(influencer, field, value)
    await db.commit()
    await db.refresh(influencer)
    return InfluencerResponse.model_validate(influencer)


@router.delete("/influencers/{id_influencer}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_influencer(
    id_influencer: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    influencer = await _get_or_404(
        db,
        Influencer,
        Influencer.id_influencer,
        id_influencer,
        "Influencer",
    )
    await db.delete(influencer)
    await db.commit()


@router.get("/medios-digitales", response_model=List[MedioDigitalResponse])
async def listar_medios_digitales(
    id_categoria_observacion: Optional[int] = Query(None, description="Filtrar por categoría de observación"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    query = select(MedioDigital).order_by(MedioDigital.nombre_medio_digital)
    if id_categoria_observacion is not None:
        query = query.where(MedioDigital.id_categoria_observacion == id_categoria_observacion)
    result = await db.execute(query)
    medios = result.scalars().all()
    return [MedioDigitalResponse.model_validate(item) for item in medios]


@router.post("/medios-digitales", response_model=MedioDigitalResponse, status_code=status.HTTP_201_CREATED)
async def crear_medio_digital(
    payload: MedioDigitalCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    await _ensure_categoria_observacion_exists(db, payload.id_categoria_observacion)
    nuevo_id = await _next_id(db, MedioDigital.id_medio_digital)
    medio = MedioDigital(id_medio_digital=nuevo_id, **payload.model_dump())
    db.add(medio)
    await db.commit()
    await db.refresh(medio)
    return MedioDigitalResponse.model_validate(medio)


@router.put("/medios-digitales/{id_medio}", response_model=MedioDigitalResponse)
async def actualizar_medio_digital(
    id_medio: int,
    payload: MedioDigitalUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    medio = await _get_or_404(
        db,
        MedioDigital,
        MedioDigital.id_medio_digital,
        id_medio,
        "Medio digital",
    )
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Debe enviar al menos un campo para actualizar")
    if "id_categoria_observacion" in updates:
        await _ensure_categoria_observacion_exists(db, updates["id_categoria_observacion"])
    for field, value in updates.items():
        setattr(medio, field, value)
    await db.commit()
    await db.refresh(medio)
    return MedioDigitalResponse.model_validate(medio)


@router.delete("/medios-digitales/{id_medio}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_medio_digital(
    id_medio: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    medio = await _get_or_404(
        db,
        MedioDigital,
        MedioDigital.id_medio_digital,
        id_medio,
        "Medio digital",
    )
    await db.delete(medio)
    await db.commit()


@router.get("/entidades", response_model=List[EntidadResponse])
async def listar_entidades(
    id_categoria_observacion: Optional[int] = Query(None, description="Filtrar por categoría de observación"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    query = select(Entidad).order_by(Entidad.nombre_entidad)
    if id_categoria_observacion is not None:
        query = query.where(Entidad.id_categoria_observacion == id_categoria_observacion)
    result = await db.execute(query)
    entidades = result.scalars().all()
    return [EntidadResponse.model_validate(item) for item in entidades]


@router.post("/entidades", response_model=EntidadResponse, status_code=status.HTTP_201_CREATED)
async def crear_entidad(
    payload: EntidadCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    await _ensure_categoria_observacion_exists(db, payload.id_categoria_observacion)
    nuevo_id = await _next_id(db, Entidad.id_entidades)
    entidad = Entidad(id_entidades=nuevo_id, **payload.model_dump())
    db.add(entidad)
    await db.commit()
    await db.refresh(entidad)
    return EntidadResponse.model_validate(entidad)


@router.put("/entidades/{id_entidad}", response_model=EntidadResponse)
async def actualizar_entidad(
    id_entidad: int,
    payload: EntidadUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    entidad = await _get_or_404(
        db,
        Entidad,
        Entidad.id_entidades,
        id_entidad,
        "Entidad",
    )
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Debe enviar al menos un campo para actualizar")
    if "id_categoria_observacion" in updates:
        await _ensure_categoria_observacion_exists(db, updates["id_categoria_observacion"])
    for field, value in updates.items():
        setattr(entidad, field, value)
    await db.commit()
    await db.refresh(entidad)
    return EntidadResponse.model_validate(entidad)


@router.delete("/entidades/{id_entidad}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_entidad(
    id_entidad: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    entidad = await _get_or_404(
        db,
        Entidad,
        Entidad.id_entidades,
        id_entidad,
        "Entidad",
    )
    await db.delete(entidad)
    await db.commit()
