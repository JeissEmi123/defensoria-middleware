"""
Revision ID: 005_add_password_history
Revises: 004_add_access_token_to_sesion
Create Date: 2025-12-01
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '005_add_password_history'
down_revision = '004_add_access_token_to_sesion'
branch_labels = None
depends_on = None

def upgrade():
    # Crear tabla password_history
    op.create_table(
        'password_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('contrasena_hash', sa.String(255), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE')
    )
    
    # Crear índices
    op.create_index('ix_password_history_id', 'password_history', ['id'])
    op.create_index('ix_password_history_usuario_id', 'password_history', ['usuario_id'])
    op.create_index('ix_password_history_fecha_creacion', 'password_history', ['fecha_creacion'])

def downgrade():
    op.drop_index('ix_password_history_fecha_creacion', 'password_history')
    op.drop_index('ix_password_history_usuario_id', 'password_history')
    op.drop_index('ix_password_history_id', 'password_history')
    op.drop_table('password_history')
