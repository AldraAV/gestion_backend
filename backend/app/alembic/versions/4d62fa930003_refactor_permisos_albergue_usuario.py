"""refactor permisos albergue usuario

Revision ID: 4d62fa930003
Revises: 3c51ef829002
Create Date: 2026-09-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4d62fa930003'
down_revision = '3c51ef829002'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Asegurar enum roloperativo con coordinador_emergencias
    op.execute("ALTER TYPE roloperativo ADD VALUE IF NOT EXISTS 'coordinador_emergencias';")

    # 2. Crear enum turnooperativo si no existe
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'turnooperativo') THEN
                CREATE TYPE turnooperativo AS ENUM ('matutino', 'vespertino', 'nocturno', 'completo');
            END IF;
        END$$;
    """)

    # 3. Agregar columna turno a albergue_usuario con valor por defecto
    op.execute("""
        ALTER TABLE albergue_usuario 
        ADD COLUMN IF NOT EXISTS turno turnooperativo NOT NULL DEFAULT 'completo';
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_albergue_usuario_turno ON albergue_usuario (turno);
    """)

    # 4. Migrar asignaciones operativas existentes desde user.alcance_id hacia albergue_usuario
    op.execute("""
        INSERT INTO albergue_usuario (id, albergue_id, usuario_id, rol, area, turno, activo, fecha_asignacion)
        SELECT 
            gen_random_uuid(),
            u.alcance_id,
            u.id,
            CASE 
                WHEN u.rol IN ('administrador_albergue', 'responsable_area', 'personal_operativo', 'coordinador_emergencias') 
                    THEN u.rol::roloperativo
                ELSE 'personal_operativo'::roloperativo
            END,
            CASE 
                WHEN u.email LIKE '%logistica%' THEN 'bodega_suministros'::areafuncional
                ELSE 'general'::areafuncional
            END,
            'completo'::turnooperativo,
            true,
            now()
        FROM "user" u
        WHERE u.alcance_id IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM albergue_usuario au 
              WHERE au.usuario_id = u.id AND au.albergue_id = u.alcance_id
          );
    """)

    # 5. Agregar restriccion CHECK a columna rol de la tabla user (4 valores exactos)
    op.execute("""
        ALTER TABLE "user" DROP CONSTRAINT IF EXISTS ck_user_rol;
        ALTER TABLE "user" ADD CONSTRAINT ck_user_rol 
            CHECK (rol IN ('coordinador_emergencias', 'administrador_albergue', 'responsable_area', 'personal_operativo'));
    """)

    # 6. Eliminar la columna redundante alcance_id de la tabla user
    op.execute("""
        ALTER TABLE "user" DROP COLUMN IF EXISTS alcance_id;
    """)


def downgrade():
    # 1. Recrear columna alcance_id en tabla user
    op.execute("""
        ALTER TABLE "user" ADD COLUMN IF NOT EXISTS alcance_id UUID;
    """)

    # 2. Restaurar alcance_id desde la asignacion activa mas reciente en albergue_usuario
    op.execute("""
        UPDATE "user" u
        SET alcance_id = au.albergue_id
        FROM albergue_usuario au
        WHERE au.usuario_id = u.id AND au.activo = true;
    """)

    # 3. Remover restriccion CHECK sobre rol
    op.execute("""
        ALTER TABLE "user" DROP CONSTRAINT IF EXISTS ck_user_rol;
    """)

    # 4. Remover columna e indice turno de albergue_usuario
    op.execute("""
        DROP INDEX IF EXISTS ix_albergue_usuario_turno;
        ALTER TABLE albergue_usuario DROP COLUMN IF EXISTS turno;
    """)
