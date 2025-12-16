"""
Revision ID: 004_add_access_token_to_sesion
Revises: 003_add_reset_token_to_usuario
Create Date: 2025-11-27
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_add_access_token_to_sesion'
down_revision = '003_add_reset_token_to_usuario'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('sesiones', sa.Column('access_token', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('sesiones', 'access_token')
