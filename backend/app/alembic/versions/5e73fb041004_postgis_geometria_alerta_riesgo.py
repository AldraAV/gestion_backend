"""activar postgis y agregar columna geometria a alerta_zona_riesgo

Revision ID: 5e73fb041004
Revises: 4d62fa930003
Create Date: 2026-09-24 00:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5e73fb041004'
down_revision = '4d62fa930003'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Activar extension PostGIS en Supabase
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # 2. Agregar columna geometria con tipo geometry (SRID 4326 = WGS84)
    # Se usa texto directo porque geoalchemy2 no soporta AddColumn via op.add_column
    op.execute("""
        ALTER TABLE alerta_zona_riesgo
        ADD COLUMN IF NOT EXISTS geometria geometry(Geometry, 4326);
    """)

    # 3. Crear indice espacial GIST para consultas eficientes
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_alerta_zona_riesgo_geometria
        ON alerta_zona_riesgo USING GIST (geometria);
    """)


def downgrade():
    # Eliminar indice espacial
    op.execute("DROP INDEX IF EXISTS idx_alerta_zona_riesgo_geometria;")

    # Eliminar columna geometria
    op.execute("ALTER TABLE alerta_zona_riesgo DROP COLUMN IF EXISTS geometria;")

    # NO eliminamos la extension PostGIS porque puede ser usada por otros
