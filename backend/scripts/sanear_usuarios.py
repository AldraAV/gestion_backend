import datetime
import uuid

import psycopg

from app.core.config import settings
from app.core.security import get_password_hash

cadena_conexion = str(settings.DATABASE_URL).replace("+psycopg", "")


def sanear_base_datos_usuarios():
    ahora = datetime.datetime.now(datetime.UTC)
    hash_admin = get_password_hash("Admin1234!")

    with psycopg.connect(cadena_conexion) as conn:
        with conn.cursor() as cur:
            # 1. Asegurar columnas de roles operativos en tabla user
            print("1. Verificando columnas operativas en tabla 'user'...")
            cur.execute("""
                ALTER TABLE "user" 
                ADD COLUMN IF NOT EXISTS rol VARCHAR(50) DEFAULT 'personal_operativo';
            """)
            cur.execute("""
                ALTER TABLE "user" 
                ADD COLUMN IF NOT EXISTS alcance_id UUID;
            """)

            # 2. Saneamiento del superusuario administrador
            correo_admin = "admin@proteccioncivil.gob.mx"
            nombre_admin = "Administrador General de Proteccion Civil"
            rol_admin = "coordinador_emergencias"

            cur.execute('SELECT id FROM "user" WHERE email = %s', (correo_admin,))
            registro = cur.fetchone()

            if registro:
                print(
                    f"2. Actualizando usuario existente: {correo_admin} (ID: {registro[0]})..."
                )
                cur.execute(
                    """
                    UPDATE "user" SET
                        full_name = %s,
                        hashed_password = %s,
                        is_active = TRUE,
                        is_superuser = TRUE,
                        rol = %s
                    WHERE id = %s
                """,
                    (nombre_admin, hash_admin, rol_admin, registro[0]),
                )
                print("   Usuario actualizado exitosamente.")
            else:
                id_nuevo = uuid.uuid4()
                print(
                    f"2. Creando superusuario administrador: {correo_admin} (ID: {id_nuevo})..."
                )
                cur.execute(
                    """
                    INSERT INTO "user" (
                        id, email, hashed_password, full_name, is_active, is_superuser, rol, created_at
                    ) VALUES (
                        %s, %s, %s, %s, TRUE, TRUE, %s, %s
                    )
                """,
                    (
                        id_nuevo,
                        correo_admin,
                        hash_admin,
                        nombre_admin,
                        rol_admin,
                        ahora,
                    ),
                )
                print("   Superusuario creado exitosamente.")

            # 3. Limpieza de usuarios nulos o corruptos si los hubiera
            cur.execute("""
                DELETE FROM "user" 
                WHERE email IS NULL OR email = '' OR hashed_password IS NULL;
            """)

            conn.commit()
            print("SANEAMIENTO DE BASE DE DATOS COMPLETADO CON EXITO.")


if __name__ == "__main__":
    sanear_base_datos_usuarios()
