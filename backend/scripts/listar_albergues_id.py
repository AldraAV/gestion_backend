from sqlalchemy import text

from app.core.db import engine

with engine.connect() as conn:
    filas = conn.execute(
        text(
            "SELECT id, folio_identificador, nombre, municipio FROM albergue ORDER BY nombre"
        )
    ).fetchall()
    for f in filas:
        print(f"ID: {f[0]} | Folio: {f[1]} | Nombre: {f[2]} | Municipio: {f[3]}")
