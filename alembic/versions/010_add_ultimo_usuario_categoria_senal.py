"""
Revision ID: 010_add_ultimo_usuario_categoria_senal
Revises: 009_add_color_categoria_sds
Create Date: 2025-12-28

Agregar campos de ultimo usuario en sds.categoria_senal
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "010_add_ultimo_usuario_categoria_senal"
down_revision = "009_add_color_categoria_sds"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "categoria_senal",
        sa.Column("ultimo_usuario_id", sa.Integer(), nullable=True),
        schema="sds",
    )
    op.add_column(
        "categoria_senal",
        sa.Column("ultimo_usuario_nombre", sa.String(length=100), nullable=True),
        schema="sds",
    )
    op.add_column(
        "categoria_senal",
        sa.Column("ultima_actualizacion", sa.DateTime(), nullable=True),
        schema="sds",
    )


def downgrade():
    op.drop_column("categoria_senal", "ultima_actualizacion", schema="sds")
    op.drop_column("categoria_senal", "ultimo_usuario_nombre", schema="sds")
    op.drop_column("categoria_senal", "ultimo_usuario_id", schema="sds")
