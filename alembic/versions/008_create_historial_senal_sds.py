"""
Revision ID: 008_create_historial_senal_sds
Revises: 007_move_to_sds_schema
Create Date: 2025-12-28

Crear tabla historial_senal en esquema sds para trazabilidad
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "008_create_historial_senal_sds"
down_revision = "007_move_to_sds_schema"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "historial_senal",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_senal_detectada", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("accion", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("estado_anterior", sa.String(50), nullable=True),
        sa.Column("estado_nuevo", sa.String(50), nullable=True),
        sa.Column("datos_adicionales", sa.JSON(), nullable=True),
        sa.Column("fecha_registro", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["id_senal_detectada"], ["sds.senal_detectada.id_senal_detectada"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="SET NULL"),
        schema="sds",
    )
    op.create_index("ix_historial_senal_id", "historial_senal", ["id"], schema="sds")
    op.create_index("ix_historial_senal_senal_id", "historial_senal", ["id_senal_detectada"], schema="sds")
    op.create_index("ix_historial_senal_usuario_id", "historial_senal", ["usuario_id"], schema="sds")
    op.create_index("ix_historial_senal_fecha_registro", "historial_senal", ["fecha_registro"], schema="sds")
    op.create_index("ix_historial_senal_accion", "historial_senal", ["accion"], schema="sds")


def downgrade():
    op.drop_index("ix_historial_senal_accion", table_name="historial_senal", schema="sds")
    op.drop_index("ix_historial_senal_fecha_registro", table_name="historial_senal", schema="sds")
    op.drop_index("ix_historial_senal_usuario_id", table_name="historial_senal", schema="sds")
    op.drop_index("ix_historial_senal_senal_id", table_name="historial_senal", schema="sds")
    op.drop_index("ix_historial_senal_id", table_name="historial_senal", schema="sds")
    op.drop_table("historial_senal", schema="sds")
