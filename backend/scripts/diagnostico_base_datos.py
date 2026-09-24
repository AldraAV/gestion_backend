import psycopg

from app.core.config import settings

cadena_conexion = str(settings.DATABASE_URL).replace("+psycopg", "")

with psycopg.connect(cadena_conexion) as conn:
    with conn.cursor() as cur:
        # Tablas publicas
        cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
        )
        tablas = [r[0] for r in cur.fetchall()]
        print("TABLAS ENCONTRADAS:", tablas)

        # Revisar tablas de usuarios (user o usuario)
        for t in ["user", "usuario"]:
            if t in tablas:
                cur.execute(
                    f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}'"
                )
                cols = cur.fetchall()
                print(f"\nCOLUMNAS DE '{t}':", [c[0] for c in cols])
                cur.execute(f'SELECT count(*) FROM "{t}"')
                print(f"TOTAL REGISTROS EN '{t}':", cur.fetchone()[0])
                cur.execute(f'SELECT * FROM "{t}" LIMIT 5')
                print(f"EJEMPLO REGISTROS EN '{t}':", cur.fetchall())
