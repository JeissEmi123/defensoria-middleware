"""
Script de prueba para insertar señales detectadas de ejemplo
Basado en el SQL proporcionado con datos de prueba
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.database.models import (
    CategoriaAnalisisSenal,
    CategoriaSenal,
    SenalDetectada,
    HistorialSenal
)
from app.config import get_settings


async def insertar_datos_prueba():
    """Insertar datos de prueba en las tablas de señales"""
    
    settings = get_settings()
    
    # Crear engine y session
    engine = create_async_engine(settings.database_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            print("🔍 Verificando categorías existentes...")
            
            # Verificar categorías de análisis
            result = await session.execute(select(CategoriaAnalisisSenal))
            categorias_analisis = result.scalars().all()
            print(f"✅ Categorías de análisis encontradas: {len(categorias_analisis)}")
            for cat in categorias_analisis:
                print(f"   - {cat.id}: {cat.nombre_categoria_analisis}")
            
            # Verificar categorías de señal
            result = await session.execute(select(CategoriaSenal))
            categorias_senal = result.scalars().all()
            print(f"✅ Categorías de señal encontradas: {len(categorias_senal)}")
            for cat in categorias_senal:
                print(f"   - {cat.id_categoria_senal}: {cat.nombre_categoria_senal} (Nivel {cat.nivel})")
            
            print("\n📝 Insertando señales detectadas de prueba...")
            
            # Señales de prueba basadas en el SQL proporcionado
            senales_prueba = [
                {
                    "fecha_deteccion": datetime(2024, 1, 15, 14, 30, 0),
                    "id_categoria_senal": 3,  # CRISIS
                    "id_categoria_analisis": 1,  # Reclutamiento
                    "score_riesgo": Decimal("85.00"),
                    "categorias_observacion": {
                        "categorias": [1, 2],
                        "intensidad": "alta",
                        "frecuencia": "diaria"
                    },
                    "plataformas_digitales": ["Twitter", "Facebook"],
                    "contenido_detectado": "Publicación con llamados a reclutamiento de menores en zonas de conflicto",
                    "metadatos": {
                        "autor": "usuario_anonimo_123",
                        "ubicacion": "Norte de Santander",
                        "fecha_publicacion": "2024-01-15T12:00:00"
                    },
                    "estado": "DETECTADA",
                    "url_origen": "https://twitter.com/example/status/123456"
                },
                {
                    "fecha_deteccion": datetime(2024, 1, 16, 9, 15, 0),
                    "id_categoria_senal": 3,  # CRISIS
                    "id_categoria_analisis": 2,  # Violencia política
                    "score_riesgo": Decimal("92.00"),
                    "categorias_observacion": {
                        "categorias": [2],
                        "datos_expuestos": ["dirección", "teléfono"],
                        "severidad": "crítica"
                    },
                    "plataformas_digitales": ["Foros", "Telegram"],
                    "contenido_detectado": "Doxxing de líder social con datos personales expuestos",
                    "metadatos": {
                        "autor": "usuario_malicioso_456",
                        "tipo_ataque": "doxxing",
                        "victima": "líder_comunitario"
                    },
                    "estado": "EN_REVISION",
                    "url_origen": "https://example-forum.com/thread/789"
                },
                {
                    "fecha_deteccion": datetime(2024, 1, 17, 18, 45, 0),
                    "id_categoria_senal": 2,  # PARACRISIS
                    "id_categoria_analisis": 3,  # Violencia digital de género
                    "score_riesgo": Decimal("78.00"),
                    "categorias_observacion": {
                        "categorias": [3],
                        "grupo_afectado": "defensoras",
                        "alcance": "regional"
                    },
                    "plataformas_digitales": ["Twitter", "Instagram"],
                    "contenido_detectado": "Campaña coordinada de acoso contra defensora de DDHH",
                    "metadatos": {
                        "num_cuentas_involucradas": 25,
                        "tipo_violencia": "acoso_digital"
                    },
                    "estado": "DETECTADA"
                },
                {
                    "fecha_deteccion": datetime(2024, 1, 18, 11, 20, 0),
                    "id_categoria_senal": 2,  # PARACRISIS
                    "id_categoria_analisis": 3,  # Violencia digital de género
                    "score_riesgo": Decimal("65.00"),
                    "categorias_observacion": {
                        "categorias": [3],
                        "tipo_contenido": "video_manipulado",
                        "victima": "figura_pública"
                    },
                    "plataformas_digitales": ["YouTube", "Reddit"],
                    "contenido_detectado": "Deepfake con contenido sexualizado de candidata política",
                    "metadatos": {
                        "tecnologia": "deepfake",
                        "impacto_potencial": "alto"
                    },
                    "estado": "VALIDADA"
                },
                {
                    "fecha_deteccion": datetime(2024, 1, 19, 16, 30, 0),
                    "id_categoria_senal": 3,  # CRISIS
                    "id_categoria_analisis": 1,  # Reclutamiento
                    "score_riesgo": Decimal("88.00"),
                    "categorias_observacion": {
                        "categorias": [1],
                        "grupo_objetivo": "adolescentes",
                        "metodo": "engaño"
                    },
                    "plataformas_digitales": ["WhatsApp", "TikTok"],
                    "contenido_detectado": "Captación de menores mediante ofertas falsas de empleo",
                    "metadatos": {
                        "modalidad": "trabajo_infantil_forzado",
                        "zona_geografica": "Cauca"
                    },
                    "estado": "EN_REVISION"
                },
                {
                    "fecha_deteccion": datetime(2024, 1, 20, 21, 10, 0),
                    "id_categoria_senal": 3,  # CRISIS
                    "id_categoria_analisis": 2,  # Violencia política
                    "score_riesgo": Decimal("95.00"),
                    "categorias_observacion": {
                        "categorias": [2],
                        "inmediata": True,
                        "reporte_policial": True
                    },
                    "plataformas_digitales": ["WhatsApp", "Signal"],
                    "contenido_detectado": "Amenaza directa con ubicación específica contra líder indígena",
                    "metadatos": {
                        "nivel_urgencia": "critico",
                        "autoridades_notificadas": True
                    },
                    "estado": "RESUELTA",
                    "fecha_resolucion": datetime(2024, 1, 21, 10, 0, 0),
                    "notas_resolucion": "Amenaza reportada a autoridades. Líder trasladado a lugar seguro."
                },
                {
                    "fecha_deteccion": datetime(2024, 1, 21, 8, 45, 0),
                    "id_categoria_senal": 1,  # RUIDO
                    "id_categoria_analisis": 2,  # Violencia política
                    "score_riesgo": Decimal("40.00"),
                    "categorias_observacion": {
                        "categorias": [2],
                        "cuentas_falsas": 3,
                        "impacto": "bajo"
                    },
                    "plataformas_digitales": ["Facebook", "LinkedIn"],
                    "contenido_detectado": "Intento de suplantación de identidad sin mayor impacto",
                    "estado": "RECHAZADA",
                    "notas_resolucion": "Falso positivo - actividad normal de redes sociales"
                },
                {
                    "fecha_deteccion": datetime(2024, 1, 22, 13, 25, 0),
                    "id_categoria_senal": 2,  # PARACRISIS
                    "id_categoria_analisis": 3,  # Violencia digital de género
                    "score_riesgo": Decimal("82.00"),
                    "categorias_observacion": {
                        "categorias": [3],
                        "género_victima": "mujer",
                        "contexto": "espacio_político"
                    },
                    "plataformas_digitales": ["Twitter", "TikTok"],
                    "contenido_detectado": "Discurso de odio misógino contra candidata en campaña",
                    "metadatos": {
                        "num_interacciones": 15000,
                        "alcance_estimado": "alto"
                    },
                    "estado": "VALIDADA"
                },
                {
                    "fecha_deteccion": datetime(2024, 1, 23, 17, 50, 0),
                    "id_categoria_senal": 1,  # RUIDO
                    "id_categoria_analisis": 1,  # Reclutamiento
                    "score_riesgo": Decimal("35.00"),
                    "categorias_observacion": {
                        "categorias": [1],
                        "bots_involucrados": 5,
                        "tendencia": False
                    },
                    "plataformas_digitales": ["Twitter", "Facebook"],
                    "contenido_detectado": "Noticias sin verificar sobre grupos armados - baja credibilidad",
                    "estado": "RECHAZADA"
                },
                {
                    "fecha_deteccion": datetime(2024, 1, 24, 10, 5, 0),
                    "id_categoria_senal": 2,  # PARACRISIS
                    "id_categoria_analisis": 3,  # Violencia digital de género
                    "score_riesgo": Decimal("75.00"),
                    "categorias_observacion": {
                        "categorias": [3],
                        "edad_victima": "adolescente",
                        "contexto": "escolar"
                    },
                    "plataformas_digitales": ["Instagram", "Snapchat"],
                    "contenido_detectado": "Ciberbullying sostenido con componente de género",
                    "metadatos": {
                        "duracion": "2_semanas",
                        "participantes": 12
                    },
                    "estado": "EN_REVISION"
                }
            ]
            
            # Insertar señales
            for idx, senal_data in enumerate(senales_prueba, 1):
                senal = SenalDetectada(**senal_data)
                session.add(senal)
                print(f"   ✅ Señal {idx}/10 agregada: Score {senal_data['score_riesgo']}, Estado: {senal_data['estado']}")
            
            # Commit de todas las señales
            await session.commit()
            print(f"\n✅ {len(senales_prueba)} señales insertadas exitosamente")
            
            # Verificar inserción
            result = await session.execute(select(SenalDetectada))
            senales = result.scalars().all()
            print(f"\n📊 Total de señales en base de datos: {len(senales)}")
            
            # Crear historial para algunas señales
            print("\n📝 Creando historial de trazabilidad...")
            
            if senales:
                # Historial para la primera señal
                historial_items = [
                    HistorialSenal(
                        id_senal_detectada=senales[0].id_senal_detectada,
                        accion="CREACION",
                        descripcion="Señal detectada automáticamente por el sistema",
                        estado_nuevo="DETECTADA",
                        datos_adicionales={"origen": "sistema_automatico"},
                        ip_address="127.0.0.1"
                    ),
                    HistorialSenal(
                        id_senal_detectada=senales[1].id_senal_detectada,
                        accion="CREACION",
                        descripcion="Señal detectada automáticamente por el sistema",
                        estado_nuevo="DETECTADA",
                        datos_adicionales={"origen": "sistema_automatico"},
                        ip_address="127.0.0.1"
                    ),
                    HistorialSenal(
                        id_senal_detectada=senales[1].id_senal_detectada,
                        accion="CAMBIO_ESTADO",
                        descripcion="Señal movida a revisión manual",
                        estado_anterior="DETECTADA",
                        estado_nuevo="EN_REVISION",
                        datos_adicionales={"analista": "sistema"},
                        ip_address="127.0.0.1"
                    )
                ]
                
                for hist in historial_items:
                    session.add(hist)
                
                await session.commit()
                print(f"   ✅ {len(historial_items)} entradas de historial creadas")
            
            # Estadísticas finales
            print("\n" + "="*60)
            print("📊 RESUMEN DE DATOS INSERTADOS")
            print("="*60)
            
            # Por estado
            from sqlalchemy import func
            result = await session.execute(
                select(SenalDetectada.estado, func.count(SenalDetectada.id_senal_detectada))
                .group_by(SenalDetectada.estado)
            )
            print("\n🔸 Señales por Estado:")
            for estado, count in result:
                print(f"   - {estado}: {count}")
            
            # Por categoría de señal
            result = await session.execute(
                select(CategoriaSenal.nombre_categoria_senal, func.count(SenalDetectada.id_senal_detectada))
                .join(SenalDetectada, SenalDetectada.id_categoria_senal == CategoriaSenal.id_categoria_senal)
                .group_by(CategoriaSenal.nombre_categoria_senal)
            )
            print("\n🔸 Señales por Categoría:")
            for categoria, count in result:
                print(f"   - {categoria}: {count}")
            
            # Por categoría de análisis
            result = await session.execute(
                select(CategoriaAnalisisSenal.nombre_categoria_analisis, func.count(SenalDetectada.id_senal_detectada))
                .join(SenalDetectada, SenalDetectada.id_categoria_analisis == CategoriaAnalisisSenal.id)
                .group_by(CategoriaAnalisisSenal.nombre_categoria_analisis)
            )
            print("\n🔸 Señales por Tipo de Violencia:")
            for categoria, count in result:
                print(f"   - {categoria[:50]}...: {count}")
            
            print("\n" + "="*60)
            print("✅ DATOS DE PRUEBA INSERTADOS EXITOSAMENTE")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ Error al insertar datos: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("="*60)
    print("🚀 SCRIPT DE INSERCIÓN DE DATOS DE PRUEBA")
    print("   Sistema de Detección de Señales - Defensoría del Pueblo")
    print("="*60)
    print()
    
    asyncio.run(insertar_datos_prueba())
