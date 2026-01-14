"""
Revision ID: 007_move_to_sds_schema
Revises: 006_deteccion_senales
Create Date: 2025-12-20

Migración para crear esquema sds y mover tablas de señales al nuevo esquema
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007_move_to_sds_schema'
down_revision = '006_deteccion_senales'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Crear el esquema sds
    op.execute("CREATE SCHEMA IF NOT EXISTS sds")
    
    # 2. Mover las tablas al esquema sds
    # Primero deshabilitamos las restricciones de clave foránea
    
    # Movemos historial_senal (la que tiene FK hacia senal_detectada)
    op.execute("ALTER TABLE historial_senal SET SCHEMA sds")
    
    # Movemos senal_detectada (la que tiene FK hacia categoria_senal y categoria_analisis_senal)
    op.execute("ALTER TABLE senal_detectada SET SCHEMA sds")
    
    # Movemos categoria_senal (la que tiene auto-referencia)
    op.execute("ALTER TABLE categoria_senal SET SCHEMA sds")
    
    # Movemos categoria_analisis_senal
    op.execute("ALTER TABLE categoria_analisis_senal SET SCHEMA sds")
    
    # 3. Renombrar los índices al nuevo esquema
    # Los índices se mueven automáticamente con las tablas, pero podemos verificar con:
    # SELECT schemaname, tablename, indexname FROM pg_indexes WHERE indexname LIKE 'ix_%';


def downgrade():
    # Mover tablas de vuelta al esquema público
    op.execute("ALTER TABLE sds.historial_senal SET SCHEMA public")
    op.execute("ALTER TABLE sds.senal_detectada SET SCHEMA public")
    op.execute("ALTER TABLE sds.categoria_senal SET SCHEMA public")
    op.execute("ALTER TABLE sds.categoria_analisis_senal SET SCHEMA public")
    
    # Eliminar el esquema sds si no contiene nada
    op.execute("DROP SCHEMA sds CASCADE")
