import psycopg
from app.core.config import settings

cadena = str(settings.DATABASE_URL).replace("+psycopg", "")
with psycopg.connect(cadena) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT a.folio_identificador, a.nombre, a.latitud, a.longitud, ii.capacidad_total, a.ocupacion_actual
            FROM albergue a
            LEFT JOIN inventario_infraestructura ii ON ii.albergue_id = a.id
            ORDER BY a.folio_identificador
        """)
        for r in cur.fetchall():
            print(r)
