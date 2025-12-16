from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_password_reset'
down_revision = '001_initial_rbac'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar campos a tabla usuarios
    op.add_column('usuarios', sa.Column('reset_token', sa.String(255), nullable=True))
    op.add_column('usuarios', sa.Column('reset_token_expira', sa.DateTime(), nullable=True))
    # Crear índice para búsquedas por token
    op.create_index('idx_usuario_reset_token', 'usuarios', ['reset_token'])


def downgrade() -> None:
    # Eliminar índice
    op.drop_index('idx_usuario_reset_token', 'usuarios')
    # Eliminar columnas
    op.drop_column('usuarios', 'reset_token_expira')
    op.drop_column('usuarios', 'reset_token')
