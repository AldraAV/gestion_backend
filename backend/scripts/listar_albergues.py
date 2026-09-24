import psycopg
from app.core.config import settings

cadena = str(settings.DATABASE_URL).replace("+psycopg", "")
with psycopg.connect(cadena) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, folio_identificador, nombre, municipio, direccion FROM albergue ORDER BY nombre")
        filas = cur.fetchall()
        print(f"TOTAL ALBERGUES EN BD: {len(filas)}")
        for f in filas:
            print(f)
