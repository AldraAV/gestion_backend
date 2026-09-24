import psycopg
from app.core.config import settings

cadena = str(settings.DATABASE_URL).replace("+psycopg", "")
with psycopg.connect(cadena) as conn:
    with conn.cursor() as cur:
        cur.execute('SELECT id, email, full_name, rol, is_superuser FROM "user"')
        print("--- USUARIOS EN EL SISTEMA ---")
        for fila in cur.fetchall():
            print(fila)
        
        cur.execute('''
            SELECT au.id, au.usuario_id, u.email, au.albergue_id, a.nombre, au.rol, au.activo
            FROM albergue_usuario au
            JOIN "user" u ON u.id = au.usuario_id
            JOIN albergue a ON a.id = au.albergue_id
        ''')
        print("--- ASIGNACIONES EN ALBERGUE_USUARIO ---")
        for fila in cur.fetchall():
            print(fila)

        cur.execute('SELECT id, folio_identificador, nombre, municipio, direccion FROM albergue LIMIT 5')
        print("--- ALBERGUES MUESTRA ---")
        for fila in cur.fetchall():
            print(fila)
