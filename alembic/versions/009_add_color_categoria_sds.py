"""
Revision ID: 009_add_color_categoria_sds
Revises: 008_create_historial_senal_sds
Create Date: 2025-12-28

Agregar color_categoria a sds.categoria_senal
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "009_add_color_categoria_sds"
down_revision = "008_create_historial_senal_sds"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "categoria_senal",
        sa.Column("color_categoria", sa.String(length=20), nullable=True),
        schema="sds",
    )
    op.execute(
        """
        UPDATE sds.categoria_senal
        SET color_categoria = CASE
            WHEN id_categoria_senales = 1 THEN '#808080'
            WHEN id_categoria_senales = 2 THEN '#FFA500'
            WHEN id_categoria_senales = 3 THEN '#FF0000'
            WHEN id_categoria_senales = 4 THEN '#FF0000'
            WHEN id_categoria_senales = 5 THEN '#FFFF00'
            WHEN id_categoria_senales = 6 THEN '#00FF00'
            ELSE '#CCCCCC'
        END
        WHERE color_categoria IS NULL
        """
    )


def downgrade():
    op.drop_column("categoria_senal", "color_categoria", schema="sds")
