#!/usr/bin/env python3
"""
Script de diagnóstico para errores 500 en el módulo de detección de señales
Analiza los posibles problemas que pueden causar errores del servidor
"""

import asyncio
import sys
import os
import traceback
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database.session import get_db_session
from app.services.senal_service_v2 import SenalServiceV2
from app.database.models_sds import SenalDetectada, CategoriaSenal, CategoriaAnalisisSenal
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

class DiagnosticoSenales:
    def __init__(self):
        self.errores = []
        self.warnings = []
        self.info = []

    def log_error(self, mensaje):
        self.errores.append(f"❌ ERROR: {mensaje}")
        print(f"❌ ERROR: {mensaje}")

    def log_warning(self, mensaje):
        self.warnings.append(f"⚠️  WARNING: {mensaje}")
        print(f"⚠️  WARNING: {mensaje}")

    def log_info(self, mensaje):
        self.info.append(f"ℹ️  INFO: {mensaje}")
        print(f"ℹ️  INFO: {mensaje}")

    async def verificar_conexion_db(self, db: AsyncSession):
        """Verificar conexión a la base de datos"""
        try:
            result = await db.execute(text("SELECT 1"))
            if result.scalar() == 1:
                self.log_info("Conexión a base de datos: OK")
                return True
        except Exception as e:
            self.log_error(f"Error de conexión a base de datos: {str(e)}")
            return False

    async def verificar_esquema_sds(self, db: AsyncSession):
        """Verificar que el esquema SDS existe"""
        try:
            result = await db.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name = 'sds'
            """))
            if result.scalar():
                self.log_info("Esquema SDS: OK")
                return True
            else:
                self.log_error("Esquema SDS no existe")
                return False
        except Exception as e:
            self.log_error(f"Error verificando esquema SDS: {str(e)}")
            return False

    async def verificar_tablas_principales(self, db: AsyncSession):
        """Verificar que las tablas principales existen"""
        tablas_requeridas = [
            'senal_detectada',
            'categoria_senal', 
            'categoria_analisis_senal',
            'resultado_observacion_senal'
        ]
        
        tablas_ok = []
        for tabla in tablas_requeridas:
            try:
                result = await db.execute(text(f"""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'sds' AND table_name = '{tabla}'
                """))
                if result.scalar():
                    tablas_ok.append(tabla)
                    self.log_info(f"Tabla sds.{tabla}: OK")
                else:
                    self.log_error(f"Tabla sds.{tabla}: NO EXISTE")
            except Exception as e:
                self.log_error(f"Error verificando tabla {tabla}: {str(e)}")
        
        return len(tablas_ok) == len(tablas_requeridas)

    async def verificar_columnas_senal_detectada(self, db: AsyncSession):
        """Verificar columnas de la tabla senal_detectada"""
        try:
            result = await db.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'sds' AND table_name = 'senal_detectada'
                ORDER BY column_name
            """))
            columnas = result.fetchall()
            
            columnas_esperadas = [
                'id_senal_detectada',
                'fecha_deteccion',
                'score_riesgo',
                'id_categoria_senal',
                'estado'
            ]
            
            columnas_encontradas = [col[0] for col in columnas]
            
            self.log_info(f"Columnas encontradas en senal_detectada: {columnas_encontradas}")
            
            # Verificar columnas críticas
            for col in columnas_esperadas:
                if col in columnas_encontradas:
                    self.log_info(f"Columna {col}: OK")
                else:
                    self.log_warning(f"Columna {col}: NO ENCONTRADA")
            
            # Verificar columna de categoría de análisis (puede tener nombres diferentes)
            col_analisis_encontrada = False
            for col_name in ['id_categoria_analisis', 'id_categoria_analisis_senal']:
                if col_name in columnas_encontradas:
                    self.log_info(f"Columna de análisis {col_name}: OK")
                    col_analisis_encontrada = True
                    break
            
            if not col_analisis_encontrada:
                self.log_error("No se encontró columna de categoría de análisis")
            
            return True
            
        except Exception as e:
            self.log_error(f"Error verificando columnas de senal_detectada: {str(e)}")
            return False

    async def verificar_datos_basicos(self, db: AsyncSession):
        """Verificar que hay datos básicos en las tablas"""
        try:
            # Verificar señales
            result = await db.execute(text("SELECT COUNT(*) FROM sds.senal_detectada"))
            count_senales = result.scalar()
            self.log_info(f"Total señales detectadas: {count_senales}")
            
            # Verificar categorías de señal
            result = await db.execute(text("SELECT COUNT(*) FROM sds.categoria_senal"))
            count_cat_senal = result.scalar()
            self.log_info(f"Total categorías de señal: {count_cat_senal}")
            
            # Verificar categorías de análisis
            result = await db.execute(text("SELECT COUNT(*) FROM sds.categoria_analisis_senal"))
            count_cat_analisis = result.scalar()
            self.log_info(f"Total categorías de análisis: {count_cat_analisis}")
            
            if count_cat_senal == 0:
                self.log_warning("No hay categorías de señal configuradas")
            if count_cat_analisis == 0:
                self.log_warning("No hay categorías de análisis configuradas")
                
            return True
            
        except Exception as e:
            self.log_error(f"Error verificando datos básicos: {str(e)}")
            return False

    async def probar_endpoints_criticos(self, db: AsyncSession):
        """Probar los endpoints más críticos del servicio"""
        try:
            service = SenalServiceV2(db)
            
            # Test 1: Obtener señales recientes
            try:
                senales = await service.obtener_senales_recientes(limite=5)
                self.log_info(f"Endpoint señales recientes: OK ({len(senales)} señales)")
            except Exception as e:
                self.log_error(f"Error en señales recientes: {str(e)}")
            
            # Test 2: Obtener estadísticas home
            try:
                stats = await service.obtener_estadisticas_home()
                self.log_info(f"Endpoint estadísticas home: OK")
            except Exception as e:
                self.log_error(f"Error en estadísticas home: {str(e)}")
            
            # Test 3: Listar categorías de señal
            try:
                categorias = await service.listar_categorias_senal()
                self.log_info(f"Endpoint categorías señal: OK ({len(categorias)} categorías)")
            except Exception as e:
                self.log_error(f"Error en categorías señal: {str(e)}")
            
            # Test 4: Listar categorías de análisis
            try:
                categorias_analisis = await service.listar_categorias_analisis()
                self.log_info(f"Endpoint categorías análisis: OK ({len(categorias_analisis)} categorías)")
            except Exception as e:
                self.log_error(f"Error en categorías análisis: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_error(f"Error general probando endpoints: {str(e)}")
            return False

    async def verificar_permisos_usuario(self, db: AsyncSession):
        """Verificar permisos del usuario de base de datos"""
        try:
            # Verificar permisos de SELECT
            result = await db.execute(text("""
                SELECT has_table_privilege(current_user, 'sds.senal_detectada', 'SELECT') as can_select,
                       has_table_privilege(current_user, 'sds.senal_detectada', 'INSERT') as can_insert,
                       has_table_privilege(current_user, 'sds.senal_detectada', 'UPDATE') as can_update
            """))
            permisos = result.fetchone()
            
            if permisos[0]:
                self.log_info("Permisos SELECT: OK")
            else:
                self.log_error("Sin permisos SELECT en senal_detectada")
            
            if permisos[1]:
                self.log_info("Permisos INSERT: OK")
            else:
                self.log_warning("Sin permisos INSERT en senal_detectada")
            
            if permisos[2]:
                self.log_info("Permisos UPDATE: OK")
            else:
                self.log_warning("Sin permisos UPDATE en senal_detectada")
            
            return True
            
        except Exception as e:
            self.log_error(f"Error verificando permisos: {str(e)}")
            return False

    async def buscar_errores_comunes(self, db: AsyncSession):
        """Buscar errores comunes que causan 500"""
        try:
            # Error 1: Inconsistencia en nombres de columnas
            result = await db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'sds' 
                AND table_name = 'categoria_senal' 
                AND column_name LIKE '%id_categoria%'
            """))
            cols_categoria = [row[0] for row in result.fetchall()]
            
            if 'id_categoria_senales' in cols_categoria and 'id_categoria_senal' in cols_categoria:
                self.log_warning("Posible inconsistencia: ambas columnas id_categoria_senales e id_categoria_senal existen")
            
            # Error 2: Datos huérfanos
            result = await db.execute(text("""
                SELECT COUNT(*) 
                FROM sds.senal_detectada sd 
                LEFT JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.id_categoria_senales 
                WHERE cs.id_categoria_senales IS NULL
            """))
            huerfanos = result.scalar()
            
            if huerfanos > 0:
                self.log_warning(f"Encontradas {huerfanos} señales con categorías inexistentes")
            
            return True
            
        except Exception as e:
            self.log_error(f"Error buscando problemas comunes: {str(e)}")
            return False

    def generar_reporte(self):
        """Generar reporte final"""
        print("\n" + "="*60)
        print("REPORTE DE DIAGNÓSTICO - MÓDULO DETECCIÓN DE SEÑALES")
        print("="*60)
        
        print(f"\n📊 RESUMEN:")
        print(f"   Errores encontrados: {len(self.errores)}")
        print(f"   Warnings: {len(self.warnings)}")
        print(f"   Información: {len(self.info)}")
        
        if self.errores:
            print(f"\n🚨 ERRORES CRÍTICOS:")
            for error in self.errores:
                print(f"   {error}")
        
        if self.warnings:
            print(f"\n⚠️  ADVERTENCIAS:")
            for warning in self.warnings:
                print(f"   {warning}")
        
        print(f"\n💡 RECOMENDACIONES:")
        if len(self.errores) == 0:
            print("   ✅ No se encontraron errores críticos")
            print("   ✅ El módulo debería funcionar correctamente")
        else:
            print("   🔧 Revisar y corregir los errores críticos listados arriba")
            print("   🔧 Verificar logs de la aplicación para más detalles")
            print("   🔧 Considerar ejecutar migraciones de base de datos")
        
        if len(self.warnings) > 0:
            print("   ⚠️  Revisar las advertencias para optimizar el funcionamiento")

async def main():
    """Función principal de diagnóstico"""
    print("🔍 Iniciando diagnóstico del módulo de detección de señales...")
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    diagnostico = DiagnosticoSenales()
    
    try:
        # Obtener sesión de base de datos
        async for db in get_db_session():
            # Ejecutar todas las verificaciones
            await diagnostico.verificar_conexion_db(db)
            await diagnostico.verificar_esquema_sds(db)
            await diagnostico.verificar_tablas_principales(db)
            await diagnostico.verificar_columnas_senal_detectada(db)
            await diagnostico.verificar_datos_basicos(db)
            await diagnostico.verificar_permisos_usuario(db)
            await diagnostico.buscar_errores_comunes(db)
            await diagnostico.probar_endpoints_criticos(db)
            break
            
    except Exception as e:
        diagnostico.log_error(f"Error general en diagnóstico: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
    
    # Generar reporte final
    diagnostico.generar_reporte()
    
    # Código de salida
    return 1 if diagnostico.errores else 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)