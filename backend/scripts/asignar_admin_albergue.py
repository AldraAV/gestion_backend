import uuid
import psycopg
from app.core.config import settings

cadena = str(settings.DATABASE_URL).replace("+psycopg", "")
with psycopg.connect(cadena) as conn:
    with conn.cursor() as cur:
        # 1. Obtener ID de admin@proteccioncivil.gob.mx
        cur.execute('SELECT id, email, full_name FROM "user" WHERE email = %s', ('admin@proteccioncivil.gob.mx',))
        fila_admin = cur.fetchone()
        if not fila_admin:
            print("ERROR: No se encontro admin@proteccioncivil.gob.mx")
            exit(1)
        admin_id, admin_email, admin_nombre = fila_admin

        # 2. Obtener Polideportivo Oriente
        cur.execute("SELECT id, nombre FROM albergue WHERE folio_identificador = 'sh-polideportivo' OR nombre ILIKE '%Polideportivo%' LIMIT 1")
        fila_albergue = cur.fetchone()
        if not fila_albergue:
            print("ERROR: No se encontro Polideportivo Oriente")
            exit(1)
        albergue_id, albergue_nombre = fila_albergue

        # 3. Asignar en albergue_usuario con UUID generado
        cur.execute('''
            SELECT id FROM albergue_usuario 
            WHERE usuario_id = %s AND albergue_id = %s
        ''', (admin_id, albergue_id))
        asignacion_existente = cur.fetchone()

        if asignacion_existente:
            cur.execute('''
                UPDATE albergue_usuario
                SET rol = 'administrador_albergue', area = 'general', activo = true, fecha_asignacion = NOW()
                WHERE id = %s
            ''', (asignacion_existente[0],))
            print(f"Asignacion actualizada para {admin_email} en {albergue_nombre}")
        else:
            nuevo_id = uuid.uuid4()
            cur.execute('''
                INSERT INTO albergue_usuario (id, usuario_id, albergue_id, rol, area, activo, fecha_asignacion)
                VALUES (%s, %s, %s, 'administrador_albergue', 'general', true, NOW())
            ''', (nuevo_id, admin_id, albergue_id))
            print(f"Asignacion CREADA (id={nuevo_id}) para {admin_email} en {albergue_nombre}")

        # 4. Asegurar que en "user" el rol sea administrador_albergue
        cur.execute('''
            UPDATE "user"
            SET rol = 'administrador_albergue'
            WHERE id = %s
        ''', (admin_id,))
        print(f"Rol en 'user' actualizado a 'administrador_albergue' para {admin_email}")

        conn.commit()
        print("Commit completado exitosamente en Supabase.")
