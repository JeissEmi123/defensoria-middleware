"""
Revision ID: 003_add_reset_token_to_usuario
Revises: 002_password_reset
Create Date: 2025-11-27
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_reset_token_to_usuario'
down_revision = '002_password_reset'
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
