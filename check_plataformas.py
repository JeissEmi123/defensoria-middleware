#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar que las plataformas_digitales se devuelvan correctamente
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.database.session import get_async_session_maker
from sqlalchemy import select
from app.database.models import SenalDetectada

async def check_plataformas():
    async with get_async_session_maker()() as session:
        result = await session.execute(
            select(SenalDetectada).limit(5)
        )
        senales = result.scalars().all()
        
        print("=" * 80)
        print("VERIFICACIÓN DE PLATAFORMAS DIGITALES")
        print("=" * 80)
        
        for s in senales:
            print(f"\nID: {s.id_senal_detectada}")
            print(f"  Plataformas: {s.plataformas_digitales}")
            print(f"  Ubicación: {s.metadatos.get('ubicacion') if s.metadatos else 'N/A'}")
            print(f"  Contenido: {s.contenido_detectado[:60] if s.contenido_detectado else 'N/A'}...")

asyncio.run(check_plataformas())
