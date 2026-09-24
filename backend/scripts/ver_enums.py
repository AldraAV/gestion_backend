import psycopg
from app.core.config import settings

cadena = str(settings.DATABASE_URL).replace("+psycopg", "")
with psycopg.connect(cadena) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE typname = 'areafuncional'")
        print("AREAS:", [r[0] for r in cur.fetchall()])
        cur.execute("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE typname = 'roloperativo'")
        print("ROLES:", [r[0] for r in cur.fetchall()])
        cur.execute("SELECT usuario_id, albergue_id, rol, area FROM albergue_usuario")
        print("ASIGNACIONES DETALLE:", cur.fetchall())
