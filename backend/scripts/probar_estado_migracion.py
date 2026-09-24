from sqlalchemy import text

from app.core.db import engine

with engine.connect() as conn:
    version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    print(f"Version actual de alembic: {version}")

    # Verificar si se creo ocupacion_actual
    cols_albergue = [
        r[0]
        for r in conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'albergue'"
            )
        ).fetchall()
    ]
    print(f"ocupacion_actual en albergue: {'ocupacion_actual' in cols_albergue}")

    # Verificar si existe reporte_ciudadano
    tablas = [
        r[0]
        for r in conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
        ).fetchall()
    ]
    print(f"reporte_ciudadano en tablas: {'reporte_ciudadano' in tablas}")
