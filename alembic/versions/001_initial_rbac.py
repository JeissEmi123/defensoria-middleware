from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_rbac'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear enum para tipo de autenticación
    tipo_autenticacion = postgresql.ENUM('local', 'ldap', 'azure_ad', name='tipo_autenticacion', create_type=False)
    tipo_autenticacion.create(op.get_bind(), checkfirst=True)
    
    # Tabla: usuarios
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre_usuario', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('nombre_completo', sa.String(length=255), nullable=True),
        sa.Column('contrasena_hash', sa.String(length=255), nullable=True),
        sa.Column('tipo_autenticacion', tipo_autenticacion, nullable=False, server_default='local'),
        sa.Column('id_externo', sa.String(length=255), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('es_superusuario', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('ultimo_acceso', sa.DateTime(), nullable=True),
        sa.Column('ultimo_cambio_contrasena', sa.DateTime(), nullable=True),
        sa.Column('intentos_login_fallidos', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('fecha_bloqueo', sa.DateTime(), nullable=True),
        sa.Column('requiere_cambio_contrasena', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('departamento', sa.String(length=100), nullable=True),
        sa.Column('cargo', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre_usuario'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_usuarios_nombre_usuario', 'usuarios', ['nombre_usuario'])
    op.create_index('ix_usuarios_email', 'usuarios', ['email'])
    op.create_index('ix_usuarios_activo', 'usuarios', ['activo'])
    op.create_index('ix_usuarios_id_externo', 'usuarios', ['id_externo'])
    
    # Tabla: roles
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=50), nullable=False),
        sa.Column('descripcion', sa.String(length=255), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('es_sistema', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre')
    )
    op.create_index('ix_roles_nombre', 'roles', ['nombre'])
    op.create_index('ix_roles_activo', 'roles', ['activo'])
    
    # Tabla: permisos
    op.create_table(
        'permisos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codigo', sa.String(length=100), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('descripcion', sa.String(length=255), nullable=True),
        sa.Column('recurso', sa.String(length=50), nullable=False),
        sa.Column('accion', sa.String(length=50), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo')
    )
    op.create_index('ix_permisos_codigo', 'permisos', ['codigo'])
    op.create_index('ix_permisos_recurso', 'permisos', ['recurso'])
    
    # Tabla: usuarios_roles (many-to-many)
    op.create_table(
        'usuarios_roles',
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('rol_id', sa.Integer(), nullable=False),
        sa.Column('fecha_asignacion', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['rol_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('usuario_id', 'rol_id')
    )
    op.create_index('ix_usuarios_roles_usuario_id', 'usuarios_roles', ['usuario_id'])
    op.create_index('ix_usuarios_roles_rol_id', 'usuarios_roles', ['rol_id'])
    
    # Tabla: roles_permisos (many-to-many)
    op.create_table(
        'roles_permisos',
        sa.Column('rol_id', sa.Integer(), nullable=False),
        sa.Column('permiso_id', sa.Integer(), nullable=False),
        sa.Column('fecha_asignacion', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['permiso_id'], ['permisos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rol_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('rol_id', 'permiso_id')
    )
    op.create_index('ix_roles_permisos_rol_id', 'roles_permisos', ['rol_id'])
    op.create_index('ix_roles_permisos_permiso_id', 'roles_permisos', ['permiso_id'])
    
    # Tabla: sesiones
    op.create_table(
        'sesiones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('token_acceso', sa.Text(), nullable=False),
        sa.Column('token_refresco', sa.Text(), nullable=False),
        sa.Column('fecha_expiracion', sa.DateTime(), nullable=False),
        sa.Column('fecha_expiracion_refresco', sa.DateTime(), nullable=False),
        sa.Column('valida', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('direccion_ip', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('fecha_ultimo_acceso', sa.DateTime(), nullable=True),
        sa.Column('fecha_invalidacion', sa.DateTime(), nullable=True),
        sa.Column('razon_invalidacion', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sesiones_usuario_id', 'sesiones', ['usuario_id'])
    op.create_index('ix_sesiones_valida', 'sesiones', ['valida'])
    op.create_index('ix_sesiones_fecha_expiracion', 'sesiones', ['fecha_expiracion'])
    
    # Tabla: eventos_auditoria
    op.create_table(
        'eventos_auditoria',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('tipo_evento', sa.String(length=50), nullable=False),
        sa.Column('recurso', sa.String(length=100), nullable=True),
        sa.Column('accion', sa.String(length=50), nullable=True),
        sa.Column('resultado', sa.String(length=20), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('detalles', sa.JSON(), nullable=True),
        sa.Column('fecha_evento', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eventos_auditoria_usuario_id', 'eventos_auditoria', ['usuario_id'])
    op.create_index('ix_eventos_auditoria_tipo_evento', 'eventos_auditoria', ['tipo_evento'])
    op.create_index('ix_eventos_auditoria_fecha_evento', 'eventos_auditoria', ['fecha_evento'])
    op.create_index('ix_eventos_auditoria_resultado', 'eventos_auditoria', ['resultado'])
    
    # Tabla: configuracion_sistema
    op.create_table(
        'configuracion_sistema',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('clave', sa.String(length=100), nullable=False),
        sa.Column('valor', sa.Text(), nullable=True),
        sa.Column('tipo_dato', sa.String(length=20), nullable=False, server_default='string'),
        sa.Column('descripcion', sa.String(length=255), nullable=True),
        sa.Column('categoria', sa.String(length=50), nullable=True),
        sa.Column('es_sensible', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('clave')
    )
    op.create_index('ix_configuracion_sistema_clave', 'configuracion_sistema', ['clave'])
    op.create_index('ix_configuracion_sistema_categoria', 'configuracion_sistema', ['categoria'])


def downgrade() -> None:
    # Eliminar tablas en orden inverso (respetando foreign keys)
    op.drop_table('configuracion_sistema')
    op.drop_table('eventos_auditoria')
    op.drop_table('sesiones')
    op.drop_table('roles_permisos')
    op.drop_table('usuarios_roles')
    op.drop_table('permisos')
    op.drop_table('roles')
    op.drop_table('usuarios')
    
    # Eliminar enum
    tipo_autenticacion = postgresql.ENUM('local', 'ldap', 'azure_ad', name='tipo_autenticacion')
    tipo_autenticacion.drop(op.get_bind())
