"""Crear tablas albergue e inventarios y refugiados

Revision ID: 2b42df719001
Revises: 1a31ce608336
Create Date: 2026-09-23 11:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2b42df719001'
down_revision = 'fe56fa70289e'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Definicion de tipos ENUM de PostgreSQL
    roloperativo = postgresql.ENUM(
        'administrador_albergue', 'responsable_area', 'personal_operativo',
        name='roloperativo', create_type=False
    )
    areafuncional = postgresql.ENUM(
        'recepcion_registro', 'alojamiento', 'bodega_suministros', 'salud_medica',
        'alimentacion', 'seguridad', 'psicologia', 'limpieza_mantenimiento', 'general',
        name='areafuncional', create_type=False
    )
    estadoestancia = postgresql.ENUM(
        'albergado', 'salida_temporal', 'egreso_definitivo', 'trasladado',
        name='estadoestancia', create_type=False
    )
    estadooperativoalbergue = postgresql.ENUM(
        'planeado', 'disponible', 'activado', 'lleno', 'cerrado', 'fuera_de_servicio',
        name='estadooperativoalbergue', create_type=False
    )

    roloperativo.create(op.get_bind(), checkfirst=True)
    areafuncional.create(op.get_bind(), checkfirst=True)
    estadoestancia.create(op.get_bind(), checkfirst=True)
    estadooperativoalbergue.create(op.get_bind(), checkfirst=True)

    # 2. Tabla albergue
    op.create_table(
        'albergue',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('folio_identificador', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('nombre', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('direccion', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column('municipio', sqlmodel.sql.sqltypes.AutoString(length=150), nullable=False),
        sa.Column('localidad', sqlmodel.sql.sqltypes.AutoString(length=150), nullable=True),
        sa.Column('estado_republica', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('latitud', sa.Float(), nullable=True),
        sa.Column('longitud', sa.Float(), nullable=True),
        sa.Column('tipo_inmueble', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column('telefono_contacto', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column('admite_mascotas', sa.Boolean(), nullable=False),
        sa.Column('estado_operativo', estadooperativoalbergue, nullable=False),
        sa.Column('observaciones', sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True),
        sa.Column('responsable_id', sa.UUID(), nullable=True),
        sa.Column('fecha_registro', sa.DateTime(timezone=True), nullable=False),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['responsable_id'], ['user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_albergue_estado_operativo'), 'albergue', ['estado_operativo'], unique=False)
    op.create_index(op.f('ix_albergue_folio_identificador'), 'albergue', ['folio_identificador'], unique=True)
    op.create_index(op.f('ix_albergue_municipio'), 'albergue', ['municipio'], unique=False)
    op.create_index(op.f('ix_albergue_nombre'), 'albergue', ['nombre'], unique=False)

    # 3. Tabla albergue_usuario
    op.create_table(
        'albergue_usuario',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('albergue_id', sa.UUID(), nullable=False),
        sa.Column('usuario_id', sa.UUID(), nullable=False),
        sa.Column('rol', roloperativo, nullable=False),
        sa.Column('area', areafuncional, nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.Column('fecha_asignacion', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['albergue_id'], ['albergue.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['usuario_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_albergue_usuario_albergue_id'), 'albergue_usuario', ['albergue_id'], unique=False)
    op.create_index(op.f('ix_albergue_usuario_area'), 'albergue_usuario', ['area'], unique=False)
    op.create_index(op.f('ix_albergue_usuario_rol'), 'albergue_usuario', ['rol'], unique=False)
    op.create_index(op.f('ix_albergue_usuario_usuario_id'), 'albergue_usuario', ['usuario_id'], unique=False)

    # 4. Tabla grupo_familiar
    op.create_table(
        'grupo_familiar',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('albergue_id', sa.UUID(), nullable=False),
        sa.Column('codigo_familia', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('nombre_referente', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('total_integrantes', sa.Integer(), nullable=False),
        sa.Column('comunidad_origen', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('necesidades_especiales', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column('fecha_registro', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['albergue_id'], ['albergue.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_grupo_familiar_albergue_id'), 'grupo_familiar', ['albergue_id'], unique=False)
    op.create_index(op.f('ix_grupo_familiar_codigo_familia'), 'grupo_familiar', ['codigo_familia'], unique=False)

    # 5. Tabla persona_refugiada
    op.create_table(
        'persona_refugiada',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('albergue_id', sa.UUID(), nullable=False),
        sa.Column('grupo_familiar_id', sa.UUID(), nullable=True),
        sa.Column('folio_identificacion', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('nombre', sqlmodel.sql.sqltypes.AutoString(length=150), nullable=False),
        sa.Column('apellido_paterno', sqlmodel.sql.sqltypes.AutoString(length=150), nullable=False),
        sa.Column('apellido_materno', sqlmodel.sql.sqltypes.AutoString(length=150), nullable=True),
        sa.Column('curp', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
        sa.Column('fecha_nacimiento', sa.DateTime(timezone=True), nullable=True),
        sa.Column('genero', sqlmodel.sql.sqltypes.AutoString(length=30), nullable=True),
        sa.Column('municipio_origen', sqlmodel.sql.sqltypes.AutoString(length=150), nullable=True),
        sa.Column('localidad_origen', sqlmodel.sql.sqltypes.AutoString(length=150), nullable=True),
        sa.Column('telefono_contacto', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column('contacto_emergencia_nombre', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('contacto_emergencia_telefono', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column('condicion_medica', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column('discapacidad', sa.Boolean(), nullable=False),
        sa.Column('embarazo', sa.Boolean(), nullable=False),
        sa.Column('adulto_mayor', sa.Boolean(), nullable=False),
        sa.Column('menor_de_edad', sa.Boolean(), nullable=False),
        sa.Column('necesidad_especial', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column('dormitorio_asignado', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column('numero_cama_colchoneta', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column('estado_estancia', estadoestancia, nullable=False),
        sa.Column('motivo_salida', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('destino_salida', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('observaciones', sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True),
        sa.Column('registrado_por_id', sa.UUID(), nullable=True),
        sa.Column('egreso_por_id', sa.UUID(), nullable=True),
        sa.Column('fecha_ingreso', sa.DateTime(timezone=True), nullable=False),
        sa.Column('fecha_salida', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['albergue_id'], ['albergue.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['egreso_por_id'], ['user.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['grupo_familiar_id'], ['grupo_familiar.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['registrado_por_id'], ['user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_persona_refugiada_albergue_id'), 'persona_refugiada', ['albergue_id'], unique=False)
    op.create_index(op.f('ix_persona_refugiada_curp'), 'persona_refugiada', ['curp'], unique=False)
    op.create_index(op.f('ix_persona_refugiada_estado_estancia'), 'persona_refugiada', ['estado_estancia'], unique=False)
    op.create_index(op.f('ix_persona_refugiada_folio_identificacion'), 'persona_refugiada', ['folio_identificacion'], unique=True)
    op.create_index(op.f('ix_persona_refugiada_grupo_familiar_id'), 'persona_refugiada', ['grupo_familiar_id'], unique=False)

    # 6. Tabla inventario_suministro
    op.create_table(
        'inventario_suministro',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('albergue_id', sa.UUID(), nullable=False),
        sa.Column('agua_potable', sa.Float(), nullable=False),
        sa.Column('alimentos_no_perecederos', sa.Integer(), nullable=False),
        sa.Column('formula_infantil', sa.Integer(), nullable=False),
        sa.Column('medicamentos_basicos', sa.Integer(), nullable=False),
        sa.Column('material_curacion', sa.Integer(), nullable=False),
        sa.Column('cobijas', sa.Integer(), nullable=False),
        sa.Column('colchonetas', sa.Integer(), nullable=False),
        sa.Column('ropa', sa.Integer(), nullable=False),
        sa.Column('kits_higiene', sa.Integer(), nullable=False),
        sa.Column('panales', sa.Integer(), nullable=False),
        sa.Column('cubrebocas', sa.Integer(), nullable=False),
        sa.Column('productos_limpieza', sa.Integer(), nullable=False),
        sa.Column('bolsas_residuos', sa.Integer(), nullable=False),
        sa.Column('linternas', sa.Integer(), nullable=False),
        sa.Column('pilas', sa.Integer(), nullable=False),
        sa.Column('extintores', sa.Integer(), nullable=False),
        sa.Column('herramientas', sa.Integer(), nullable=False),
        sa.Column('material_oficina', sa.Integer(), nullable=False),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['albergue_id'], ['albergue.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('albergue_id')
    )
    op.create_index(op.f('ix_inventario_suministro_albergue_id'), 'inventario_suministro', ['albergue_id'], unique=True)

    # 7. Tabla inventario_infraestructura
    op.create_table(
        'inventario_infraestructura',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('albergue_id', sa.UUID(), nullable=False),
        sa.Column('capacidad_maxima', sa.Integer(), nullable=False),
        sa.Column('dormitorios', sa.Integer(), nullable=False),
        sa.Column('banos', sa.Integer(), nullable=False),
        sa.Column('regaderas', sa.Integer(), nullable=False),
        sa.Column('cocina', sa.Integer(), nullable=False),
        sa.Column('comedor', sa.Integer(), nullable=False),
        sa.Column('consultorio', sa.Integer(), nullable=False),
        sa.Column('bodega', sa.Integer(), nullable=False),
        sa.Column('salidas_emergencia', sa.Integer(), nullable=False),
        sa.Column('extintores', sa.Integer(), nullable=False),
        sa.Column('accesos_silla_ruedas', sa.Boolean(), nullable=False),
        sa.Column('planta_electrica', sa.Boolean(), nullable=False),
        sa.Column('sistema_agua', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('estado_inmueble', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['albergue_id'], ['albergue.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('albergue_id')
    )
    op.create_index(op.f('ix_inventario_infraestructura_albergue_id'), 'inventario_infraestructura', ['albergue_id'], unique=True)

    # 8. Tabla inventario_recurso_humano
    op.create_table(
        'inventario_recurso_humano',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('albergue_id', sa.UUID(), nullable=False),
        sa.Column('administrador', sa.Integer(), nullable=False),
        sa.Column('medicos', sa.Integer(), nullable=False),
        sa.Column('enfermeria', sa.Integer(), nullable=False),
        sa.Column('psicologia', sa.Integer(), nullable=False),
        sa.Column('cocineros', sa.Integer(), nullable=False),
        sa.Column('personal_limpieza', sa.Integer(), nullable=False),
        sa.Column('seguridad', sa.Integer(), nullable=False),
        sa.Column('trabajadores_sociales', sa.Integer(), nullable=False),
        sa.Column('traductores', sa.Integer(), nullable=False),
        sa.Column('voluntarios', sa.Integer(), nullable=False),
        sa.Column('conductores', sa.Integer(), nullable=False),
        sa.Column('responsables_bodega', sa.Integer(), nullable=False),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['albergue_id'], ['albergue.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('albergue_id')
    )
    op.create_index(op.f('ix_inventario_recurso_humano_albergue_id'), 'inventario_recurso_humano', ['albergue_id'], unique=True)


def downgrade():
    op.drop_table('inventario_recurso_humano')
    op.drop_table('inventario_infraestructura')
    op.drop_table('inventario_suministro')
    op.drop_table('persona_refugiada')
    op.drop_table('grupo_familiar')
    op.drop_table('albergue_usuario')
    op.drop_table('albergue')

    op.execute('DROP TYPE IF EXISTS estadooperativoalbergue')
    op.execute('DROP TYPE IF EXISTS estadoestancia')
    op.execute('DROP TYPE IF EXISTS areafuncional')
    op.execute('DROP TYPE IF EXISTS roloperativo')
