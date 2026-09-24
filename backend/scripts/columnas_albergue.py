import psycopg
from app.core.config import settings

cadena = str(settings.DATABASE_URL).replace("+psycopg", "")
with psycopg.connect(cadena) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'albergue'
        """)
        for c in cur.fetchall():
            print(c)
