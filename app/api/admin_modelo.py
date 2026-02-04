from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.core.dependencies import get_current_user
from app.database.models import Usuario
from app.database.models_sds import CategoriaAnalisisSenal, ConductaVulneratoria, PalabraClave, Emoticon, FraseClave
from sqlalchemy import text, select, func

router = APIRouter(prefix="/admin-modelo", tags=["Admin Modelo"])

@router.get("/categorias-analisis")
async def listar_categorias_analisis(
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(select(CategoriaAnalisisSenal))
    categorias = result.scalars().all()
    
    lista = []
    for cat in categorias:
        # Contar relacionados
        conductas_count = await db.execute(
            select(func.count()).select_from(ConductaVulneratoria)
            .where(ConductaVulneratoria.id_categoria_analisis_senal == cat.id_categoria_analisis_senal)
        )
        palabras_count = await db.execute(
            select(func.count()).select_from(PalabraClave)
            .where(PalabraClave.id_categoria_analisis_senal == cat.id_categoria_analisis_senal)
        )
        emoticones_count = await db.execute(
            select(func.count()).select_from(Emoticon)
            .where(Emoticon.id_categoria_analisis_senal == cat.id_categoria_analisis_senal)
        )
        frases_count = await db.execute(
            select(func.count()).select_from(FraseClave)
            .where(FraseClave.id_categoria_analisis_senal == cat.id_categoria_analisis_senal)
        )
        
        lista.append({
            "id_categoria_analisis_senal": cat.id_categoria_analisis_senal,
            "nombre_categoria_analisis": cat.nombre_categoria_analisis,
            "descripcion_categoria_analisis": cat.descripcion_categoria_analisis,
            "total_conductas": conductas_count.scalar(),
            "total_palabras": palabras_count.scalar(),
            "total_emoticones": emoticones_count.scalar(),
            "total_frases": frases_count.scalar()
        })
    
    return lista

@router.get("/categorias-analisis/{id_categoria}")
async def obtener_categoria_analisis(
    id_categoria: int,
    db: AsyncSession = Depends(get_db_session)
):
    # Obtener categoría
    cat_result = await db.execute(text("""
        SELECT id_categoria_analisis_senal, nombre_categoria_analisis, descripcion_categoria_analisis
        FROM sds.categoria_analisis_senal
        WHERE id_categoria_analisis_senal = :id
    """), {"id": id_categoria})
    cat_row = cat_result.fetchone()
    if not cat_row:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    return {
        "categoria": {
            "id_categoria_analisis_senal": cat_row[0],
            "nombre_categoria_analisis": cat_row[1],
            "descripcion_categoria_analisis": cat_row[2]
        },
        "conductas": [],
        "palabras_clave": [],
        "emoticones": [],
        "frases_clave": []
    }

@router.put("/categorias-analisis/{id_categoria}")
async def actualizar_categoria_analisis(
    id_categoria: int,
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(
        select(CategoriaAnalisisSenal).where(CategoriaAnalisisSenal.id_categoria_analisis_senal == id_categoria)
    )
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    if "nombre_categoria_analisis" in data:
        cat.nombre_categoria_analisis = data["nombre_categoria_analisis"]
    if "descripcion_categoria_analisis" in data:
        cat.descripcion_categoria_analisis = data["descripcion_categoria_analisis"]
    
    await db.commit()
    return {"success": True}

# CONDUCTAS
@router.post("/categorias-analisis/{id_categoria}/conductas")
async def crear_conducta(
    id_categoria: int,
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(text("SELECT COALESCE(MAX(id_conducta_vulneratorias), 0) + 1 FROM sds.conducta_vulneratoria"))
    nuevo_id = result.scalar()
    
    nueva = ConductaVulneratoria(
        id_conducta_vulneratoria=nuevo_id,
        nombre_conducta=data.get("nombre_conducta_vulneratoria"),
        descripcion_conducta=data.get("definicion_conducta_vulneratoria"),
        peso_conducta=data.get("peso_conducta_vulneratoria", 0),
        id_categoria_analisis_senal=id_categoria
    )
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return {"id_conducta_vulneratoria": nueva.id_conducta_vulneratoria, "success": True}

@router.put("/categorias-analisis/{id_categoria}/conductas/{conducta_id}")
async def actualizar_conducta(
    id_categoria: int,
    conducta_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(
        select(ConductaVulneratoria).where(ConductaVulneratoria.id_conducta_vulneratoria == conducta_id)
    )
    conducta = result.scalar_one_or_none()
    if not conducta:
        raise HTTPException(status_code=404, detail="Conducta no encontrada")
    
    if "nombre_conducta_vulneratoria" in data:
        conducta.nombre_conducta = data["nombre_conducta_vulneratoria"]
    if "definicion_conducta_vulneratoria" in data:
        conducta.descripcion_conducta = data["definicion_conducta_vulneratoria"]
    if "peso_conducta_vulneratoria" in data:
        conducta.peso_conducta = data["peso_conducta_vulneratoria"]
    
    await db.commit()
    return {"success": True}

@router.delete("/categorias-analisis/{id_categoria}/conductas/{conducta_id}")
async def eliminar_conducta(
    id_categoria: int,
    conducta_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(
        select(ConductaVulneratoria).where(ConductaVulneratoria.id_conducta_vulneratoria == conducta_id)
    )
    conducta = result.scalar_one_or_none()
    if not conducta:
        raise HTTPException(status_code=404, detail="Conducta no encontrada")
    
    await db.delete(conducta)
    await db.commit()
    return {"success": True}

# PALABRAS CLAVE
@router.post("/categorias-analisis/{id_categoria}/palabras")
async def crear_palabra(
    id_categoria: int,
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(text("SELECT COALESCE(MAX(id_palabra_clave), 0) + 1 FROM sds.palabra_clave"))
    nuevo_id = result.scalar()
    
    nueva = PalabraClave(
        id_palabra_clave=nuevo_id,
        palabra_clave=data.get("nombre_palabra_clave"),
        contexto=data.get("contexto"),
        id_categoria_analisis_senal=id_categoria
    )
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return {"id_palabra_clave": nueva.id_palabra_clave, "success": True}

@router.put("/categorias-analisis/{id_categoria}/palabras/{palabra_id}")
async def actualizar_palabra(
    id_categoria: int,
    palabra_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(
        select(PalabraClave).where(PalabraClave.id_palabra_clave == palabra_id)
    )
    palabra = result.scalar_one_or_none()
    if not palabra:
        raise HTTPException(status_code=404, detail="Palabra no encontrada")
    
    if "nombre_palabra_clave" in data:
        palabra.palabra_clave = data["nombre_palabra_clave"]
    if "contexto" in data:
        palabra.contexto = data["contexto"]
    
    await db.commit()
    return {"success": True}

@router.delete("/categorias-analisis/{id_categoria}/palabras/{palabra_id}")
async def eliminar_palabra(
    id_categoria: int,
    palabra_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(
        select(PalabraClave).where(PalabraClave.id_palabra_clave == palabra_id)
    )
    palabra = result.scalar_one_or_none()
    if not palabra:
        raise HTTPException(status_code=404, detail="Palabra no encontrada")
    
    await db.delete(palabra)
    await db.commit()
    return {"success": True}

# EMOTICONES
@router.post("/categorias-analisis/{id_categoria}/emoticones")
async def crear_emoticon(
    id_categoria: int,
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(text("SELECT COALESCE(MAX(id_emoticon), 0) + 1 FROM sds.emoticon"))
    nuevo_id = result.scalar()
    
    nuevo = Emoticon(
        id_emoticon=nuevo_id,
        codigo_emoticon=data.get("tipo_emoticon"),
        descripcion_emoticon=data.get("descripcion_emoticon"),
        id_categoria_analisis_senal=id_categoria
    )
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return {"id_emoticon": nuevo.id_emoticon, "success": True}

@router.put("/categorias-analisis/{id_categoria}/emoticones/{emoticon_id}")
async def actualizar_emoticon(
    id_categoria: int,
    emoticon_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(
        select(Emoticon).where(Emoticon.id_emoticon == emoticon_id)
    )
    emoticon = result.scalar_one_or_none()
    if not emoticon:
        raise HTTPException(status_code=404, detail="Emoticon no encontrado")
    
    if "tipo_emoticon" in data:
        emoticon.codigo_emoticon = data["tipo_emoticon"]
    if "descripcion_emoticon" in data:
        emoticon.descripcion_emoticon = data["descripcion_emoticon"]
    
    await db.commit()
    return {"success": True}

@router.delete("/categorias-analisis/{id_categoria}/emoticones/{emoticon_id}")
async def eliminar_emoticon(
    id_categoria: int,
    emoticon_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(
        select(Emoticon).where(Emoticon.id_emoticon == emoticon_id)
    )
    emoticon = result.scalar_one_or_none()
    if not emoticon:
        raise HTTPException(status_code=404, detail="Emoticon no encontrado")
    
    await db.delete(emoticon)
    await db.commit()
    return {"success": True}

# FRASES CLAVE
@router.post("/categorias-analisis/{id_categoria}/frases")
async def crear_frase(
    id_categoria: int,
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(text("SELECT COALESCE(MAX(id_frase_clave), 0) + 1 FROM sds.frase_clave"))
    nuevo_id = result.scalar()
    
    nueva = FraseClave(
        id_frase_clave=nuevo_id,
        frase=data.get("nombre_frase_clave"),
        contexto=data.get("contexto"),
        id_categoria_analisis_senal=id_categoria
    )
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return {"id_frase_clave": nueva.id_frase_clave, "success": True}

@router.put("/categorias-analisis/{id_categoria}/frases/{frase_id}")
async def actualizar_frase(
    id_categoria: int,
    frase_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(
        select(FraseClave).where(FraseClave.id_frase_clave == frase_id)
    )
    frase = result.scalar_one_or_none()
    if not frase:
        raise HTTPException(status_code=404, detail="Frase no encontrada")
    
    if "nombre_frase_clave" in data:
        frase.frase = data["nombre_frase_clave"]
    if "contexto" in data:
        frase.contexto = data["contexto"]
    
    await db.commit()
    return {"success": True}

@router.delete("/categorias-analisis/{id_categoria}/frases/{frase_id}")
async def eliminar_frase(
    id_categoria: int,
    frase_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(
        select(FraseClave).where(FraseClave.id_frase_clave == frase_id)
    )
    frase = result.scalar_one_or_none()
    if not frase:
        raise HTTPException(status_code=404, detail="Frase no encontrada")
    
    await db.delete(frase)
    await db.commit()
    return {"success": True}
