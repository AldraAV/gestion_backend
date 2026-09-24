"""Saneamiento sigras: ocupacion atomica, reporte ciudadano, renombramiento extintores y vista dashboard

Revision ID: 3c51ef829002
Revises: 2b42df719001
Create Date: 2026-09-23 22:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql

revision = '3c51ef829002'
down_revision = '2b42df719001'
branch_labels = None
depends_on = None


def upgrade():
    # --------------------------------------------------------------------------
    # 1. Contador de ocupacion atomico en albergue + Backfill
    # --------------------------------------------------------------------------
    op.add_column(
        'albergue',
        sa.Column('ocupacion_actual', sa.Integer(), server_default='0', nullable=False)
    )

    # Backfill con personas activas en refugio
    op.execute("""
        UPDATE albergue a
        SET ocupacion_actual = COALESCE((
            SELECT COUNT(*)
            FROM persona_refugiada p
            WHERE p.albergue_id = a.id
              AND p.estado_estancia IN ('albergado', 'salida_temporal')
        ), 0);
    """)

    # --------------------------------------------------------------------------
    # 2. Creacion de tipos ENUM y tabla fisica reporte_ciudadano
    # --------------------------------------------------------------------------
    tipoemergenciaciudadana = postgresql.ENUM(
        'inundacion_severa', 'persona_atrapada', 'deslave_bloqueo_camino',
        'requiere_evacuacion', 'desabasto_suministros', 'atencion_medica_urgente', 'otro',
        name='tipoemergenciaciudadana', create_type=False
    )
    nivelprioridademergencia = postgresql.ENUM(
        'baja', 'media', 'alta', 'critica_vida_en_riesgo',
        name='nivelprioridademergencia', create_type=False
    )
    estadoreporteciudadano = postgresql.ENUM(
        'recibido', 'en_verificacion', 'brigada_asignada', 'atendido', 'cancelado',
        name='estadoreporteciudadano', create_type=False
    )

    tipoemergenciaciudadana.create(op.get_bind(), checkfirst=True)
    nivelprioridademergencia.create(op.get_bind(), checkfirst=True)
    estadoreporteciudadano.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'reporte_ciudadano',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('folio_reporte', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('tipo_emergencia', tipoemergenciaciudadana, nullable=False),
        sa.Column('descripcion', sqlmodel.sql.sqltypes.AutoString(length=2000), nullable=False),
        sa.Column('latitud', sa.Float(), nullable=False),
        sa.Column('longitud', sa.Float(), nullable=False),
        sa.Column('direccion_referencia', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column('municipio', sqlmodel.sql.sqltypes.AutoString(length=150), nullable=False),
        sa.Column('localidad', sqlmodel.sql.sqltypes.AutoString(length=150), nullable=True),
        sa.Column('nivel_prioridad', nivelprioridademergencia, nullable=False),
        sa.Column('estado_reporte', estadoreporteciudadano, nullable=False),
        sa.Column('personas_afectadas', sa.Integer(), server_default='1', nullable=False),
        sa.Column('personas_vulnerables', sa.Integer(), server_default='0', nullable=False),
        sa.Column('telefono_contacto', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column('url_evidencia_multimedia', sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True),
        sa.Column('brigada_asignada_id', sa.UUID(), nullable=True),
        sa.Column('fecha_reporte', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_atencion', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['brigada_asignada_id'], ['user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reporte_ciudadano_folio_reporte'), 'reporte_ciudadano', ['folio_reporte'], unique=True)
    op.create_index(op.f('ix_reporte_ciudadano_municipio'), 'reporte_ciudadano', ['municipio'], unique=False)
    op.create_index(op.f('ix_reporte_ciudadano_estado_reporte'), 'reporte_ciudadano', ['estado_reporte'], unique=False)
    op.create_index(op.f('ix_reporte_ciudadano_nivel_prioridad'), 'reporte_ciudadano', ['nivel_prioridad'], unique=False)
    op.create_index(op.f('ix_reporte_ciudadano_tipo_emergencia'), 'reporte_ciudadano', ['tipo_emergencia'], unique=False)
    op.create_index(op.f('ix_reporte_ciudadano_latitud'), 'reporte_ciudadano', ['latitud'], unique=False)
    op.create_index(op.f('ix_reporte_ciudadano_longitud'), 'reporte_ciudadano', ['longitud'], unique=False)

    # --------------------------------------------------------------------------
    # 3. Renombrar columnas ambiguas de extintores
    # --------------------------------------------------------------------------
    op.alter_column('inventario_infraestructura', 'extintores', new_column_name='extintores_instalados')
    op.alter_column('inventario_suministro', 'extintores', new_column_name='extintores_reserva')

    # --------------------------------------------------------------------------
    # 4. Creacion de la vista SQL consolidada para el dashboard
    # --------------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE VIEW vista_dashboard_albergue AS
        SELECT 
            a.id AS albergue_id,
            a.folio_identificador,
            a.nombre,
            a.municipio,
            a.localidad,
            a.direccion,
            a.estado_operativo,
            a.ocupacion_actual,
            COALESCE(inf.capacidad_maxima, 0) AS capacidad_maxima,
            GREATEST(0, COALESCE(inf.capacidad_maxima, 0) - a.ocupacion_actual) AS cupo_disponible,
            ROUND(
                CASE 
                    WHEN COALESCE(inf.capacidad_maxima, 0) = 0 THEN (0.0)::numeric
                    ELSE ((a.ocupacion_actual::numeric / inf.capacidad_maxima::numeric) * 100.0::numeric)
                END, 2
            ) AS porcentaje_ocupacion,
            CASE
                WHEN a.estado_operativo IN ('cerrado', 'fuera_de_servicio') THEN 'inactivo'
                WHEN COALESCE(inf.capacidad_maxima, 0) = 0 OR a.ocupacion_actual >= inf.capacidad_maxima THEN 'rojo'
                WHEN (a.ocupacion_actual::numeric / inf.capacidad_maxima::numeric) >= 0.75 THEN 'ambar'
                ELSE 'verde'
            END AS semaforo,
            -- Infraestructura
            COALESCE(inf.dormitorios, 0) AS dormitorios,
            COALESCE(inf.banos, 0) AS banos,
            COALESCE(inf.regaderas, 0) AS regaderas,
            COALESCE(inf.cocina, 0) AS cocina,
            COALESCE(inf.comedor, 0) AS comedor,
            COALESCE(inf.consultorio, 0) AS consultorio,
            COALESCE(inf.bodega, 0) AS bodega,
            COALESCE(inf.salidas_emergencia, 0) AS salidas_emergencia,
            COALESCE(inf.extintores_instalados, 0) AS extintores_instalados,
            COALESCE(inf.accesos_silla_ruedas, false) AS accesos_silla_ruedas,
            COALESCE(inf.planta_electrica, false) AS planta_electrica,
            COALESCE(inf.sistema_agua, 'sin_especificar') AS sistema_agua,
            COALESCE(inf.estado_inmueble, 'sin_dictamen') AS estado_inmueble,
            -- Recursos Humanos
            COALESCE(rh.administrador, 0) AS personal_administracion,
            COALESCE(rh.medicos, 0) AS personal_medicos,
            COALESCE(rh.enfermeria, 0) AS personal_enfermeria,
            COALESCE(rh.psicologia, 0) AS personal_psicologia,
            COALESCE(rh.cocineros, 0) AS personal_cocineros,
            COALESCE(rh.personal_limpieza, 0) AS personal_limpieza,
            COALESCE(rh.seguridad, 0) AS personal_seguridad,
            COALESCE(rh.voluntarios, 0) AS personal_voluntarios,
            (COALESCE(rh.medicos, 0) + COALESCE(rh.enfermeria, 0)) AS total_personal_salud,
            -- Suministros y ratios per capita
            COALESCE(sum.agua_potable, 0.0) AS agua_potable_litros,
            ROUND(
                CASE 
                    WHEN a.ocupacion_actual = 0 THEN (COALESCE(sum.agua_potable, 0.0))::numeric
                    ELSE ((COALESCE(sum.agua_potable, 0.0))::numeric / a.ocupacion_actual::numeric)
                END, 2
            ) AS agua_litros_por_persona,
            CASE 
                WHEN a.ocupacion_actual > 0 AND ((COALESCE(sum.agua_potable, 0.0))::numeric / a.ocupacion_actual::numeric) < 3.0 THEN true
                ELSE false
            END AS alerta_agua_critica,
            COALESCE(sum.alimentos_no_perecederos, 0) AS raciones_alimentos,
            ROUND(
                CASE 
                    WHEN a.ocupacion_actual = 0 THEN (COALESCE(sum.alimentos_no_perecederos, 0))::numeric
                    ELSE ((COALESCE(sum.alimentos_no_perecederos, 0))::numeric / a.ocupacion_actual::numeric)
                END, 2
            ) AS raciones_por_persona,
            CASE 
                WHEN a.ocupacion_actual > 0 AND ((COALESCE(sum.alimentos_no_perecederos, 0))::numeric / a.ocupacion_actual::numeric) < 2.0 THEN true
                ELSE false
            END AS alerta_alimentos_critica,
            COALESCE(sum.colchonetas, 0) AS colchonetas_disponibles,
            (COALESCE(sum.colchonetas, 0) < a.ocupacion_actual) AS alerta_colchonetas_deficit,
            COALESCE(sum.cobijas, 0) AS cobijas_disponibles,
            COALESCE(sum.kits_higiene, 0) AS kits_higiene_disponibles,
            COALESCE(sum.medicamentos_basicos, 0) AS medicamentos_cajas,
            COALESCE(sum.material_curacion, 0) AS material_curacion_paquetes,
            COALESCE(sum.extintores_reserva, 0) AS extintores_reserva,
            COALESCE(inf.fecha_actualizacion, a.fecha_actualizacion) AS fecha_ultimo_corte
        FROM albergue a
        LEFT JOIN inventario_infraestructura inf ON inf.albergue_id = a.id
        LEFT JOIN inventario_recurso_humano rh ON rh.albergue_id = a.id
        LEFT JOIN inventario_suministro sum ON sum.albergue_id = a.id;
    """)


def downgrade():
    op.execute("DROP VIEW IF EXISTS vista_dashboard_albergue")
    op.alter_column('inventario_suministro', 'extintores_reserva', new_column_name='extintores')
    op.alter_column('inventario_infraestructura', 'extintores_instalados', new_column_name='extintores')
    op.drop_table('reporte_ciudadano')
    op.execute("DROP TYPE IF EXISTS estadoreporteciudadano")
    op.execute("DROP TYPE IF EXISTS nivelprioridademergencia")
    op.execute("DROP TYPE IF EXISTS tipoemergenciaciudadana")
    op.drop_column('albergue', 'ocupacion_actual')
