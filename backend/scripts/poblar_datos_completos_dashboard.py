from sqlalchemy import text

from app.core.db import engine
from app.core.security import get_password_hash

POLIDEPORTIVO_ID = "e552f605-7202-44ac-9e73-8bcbc607be50"
SAN_LUCAS_ID = "b6d10286-864c-4b48-9e1d-b80a72950ff6"


def poblar():
    with engine.begin() as conn:
        print("Poblando infraestructura, suministros y recursos humanos...")

        # 1. Infraestructura Polideportivo Oriente
        conn.execute(
            text("""
            INSERT INTO inventario_infraestructura (
                id, albergue_id, capacidad_maxima, dormitorios, banos, regaderas,
                cocina, comedor, consultorio, bodega, salidas_emergencia, extintores_instalados,
                accesos_silla_ruedas, planta_electrica, sistema_agua, estado_inmueble, fecha_actualizacion
            ) VALUES (
                gen_random_uuid(), :albergue_id, 250, 4, 12, 8,
                2, 1, 1, 1, 4, 6,
                true, true, 'cisterna_red', 'optimo', now()
            )
            ON CONFLICT (albergue_id) DO UPDATE SET
                capacidad_maxima = 250,
                dormitorios = 4,
                banos = 12,
                regaderas = 8,
                extintores_instalados = 6,
                accesos_silla_ruedas = true,
                planta_electrica = true,
                fecha_actualizacion = now();
        """),
            {"albergue_id": POLIDEPORTIVO_ID},
        )

        # 2. Recursos Humanos Polideportivo Oriente
        conn.execute(
            text("""
            INSERT INTO inventario_recurso_humano (
                id, albergue_id, administrador, medicos, enfermeria, psicologia,
                cocineros, personal_limpieza, seguridad, trabajadores_sociales,
                traductores, voluntarios, conductores, responsables_bodega, fecha_actualizacion
            ) VALUES (
                gen_random_uuid(), :albergue_id, 1, 2, 4, 1,
                4, 3, 2, 2,
                0, 8, 2, 1, now()
            )
            ON CONFLICT (albergue_id) DO UPDATE SET
                administrador = 1,
                medicos = 2,
                enfermeria = 4,
                psicologia = 1,
                cocineros = 4,
                personal_limpieza = 3,
                voluntarios = 8,
                fecha_actualizacion = now();
        """),
            {"albergue_id": POLIDEPORTIVO_ID},
        )

        # 3. Suministros Polideportivo Oriente
        conn.execute(
            text("""
            INSERT INTO inventario_suministro (
                id, albergue_id, agua_potable, alimentos_no_perecederos, formula_infantil,
                medicamentos_basicos, material_curacion, cobijas, colchonetas, ropa,
                kits_higiene, panales, cubrebocas, productos_limpieza, bolsas_residuos,
                linternas, pilas, extintores_reserva, herramientas, material_oficina, fecha_actualizacion
            ) VALUES (
                gen_random_uuid(), :albergue_id, 1200.0, 650, 30,
                120, 45, 200, 180, 150,
                170, 50, 300, 80, 50,
                15, 60, 2, 10, 20, now()
            )
            ON CONFLICT (albergue_id) DO UPDATE SET
                agua_potable = 1200.0,
                alimentos_no_perecederos = 650,
                colchonetas = 180,
                cobijas = 200,
                extintores_reserva = 2,
                fecha_actualizacion = now();
        """),
            {"albergue_id": POLIDEPORTIVO_ID},
        )

        # 4. Infraestructura Col. San Lucas (180 capacidad, ocupacion alta)
        conn.execute(
            text("""
            INSERT INTO inventario_infraestructura (
                id, albergue_id, capacidad_maxima, dormitorios, banos, regaderas,
                cocina, comedor, consultorio, bodega, salidas_emergencia, extintores_instalados,
                accesos_silla_ruedas, planta_electrica, sistema_agua, estado_inmueble, fecha_actualizacion
            ) VALUES (
                gen_random_uuid(), :albergue_id, 180, 3, 8, 6,
                1, 1, 1, 1, 2, 4,
                true, false, 'pozo_cisterna', 'bueno', now()
            )
            ON CONFLICT (albergue_id) DO UPDATE SET
                capacidad_maxima = 180,
                extintores_instalados = 4,
                fecha_actualizacion = now();
        """),
            {"albergue_id": SAN_LUCAS_ID},
        )

        # 5. Suministros Col. San Lucas
        conn.execute(
            text("""
            INSERT INTO inventario_suministro (
                id, albergue_id, agua_potable, alimentos_no_perecederos, formula_infantil,
                medicamentos_basicos, material_curacion, cobijas, colchonetas, ropa,
                kits_higiene, panales, cubrebocas, productos_limpieza, bolsas_residuos,
                linternas, pilas, extintores_reserva, herramientas, material_oficina, fecha_actualizacion
            ) VALUES (
                gen_random_uuid(), :albergue_id, 400.0, 150, 10,
                40, 20, 100, 120, 80,
                90, 20, 150, 40, 30,
                8, 30, 1, 5, 10, now()
            )
            ON CONFLICT (albergue_id) DO UPDATE SET
                agua_potable = 400.0,
                alimentos_no_perecederos = 150,
                extintores_reserva = 1,
                fecha_actualizacion = now();
        """),
            {"albergue_id": SAN_LUCAS_ID},
        )

        # 6. Insertar personas albergadas en Polideportivo Oriente
        conn.execute(
            text("""
            DELETE FROM persona_refugiada WHERE albergue_id = :albergue_id;
        """),
            {"albergue_id": POLIDEPORTIVO_ID},
        )

        conn.execute(
            text("""
            INSERT INTO persona_refugiada (
                id, albergue_id, folio_identificacion, nombre, apellido_paterno, apellido_materno,
                curp, genero, condicion_medica, discapacidad, embarazo, adulto_mayor, menor_de_edad,
                necesidad_especial, dormitorio_asignado, numero_cama_colchoneta, estado_estancia, fecha_ingreso
            ) VALUES
            (
                gen_random_uuid(), :albergue_id, 'REF-TAM-001', 'Maria Elena', 'Hernandez', 'Lopez',
                'HELM750412MTCLPR01', 'femenino', 'Hipertension arterial y asma moderada', false, false, false, false,
                'Dieta baja en sodio y control termico', 'Nave A - Familiar', 'C-12', 'albergado', now() - interval '2 days'
            ),
            (
                gen_random_uuid(), :albergue_id, 'REF-TAM-002', 'Roberto', 'Gomez', 'Ruiz',
                'GORR580918HTCLRN02', 'masculino', 'Diabetes mellitus tipo 2 insulinodependiente', true, false, true, false,
                'Requiere refrigeracion constante para insulina y rampa', 'Nave A - Familiar', 'C-13', 'albergado', now() - interval '1 day'
            ),
            (
                gen_random_uuid(), :albergue_id, 'REF-TAM-003', 'Carlos Eduardo', 'Perez', 'Castillo',
                'PECC920315HTCLSN03', 'masculino', NULL, false, false, false, false,
                NULL, 'Nave B - General', 'C-45', 'albergado', now() - interval '5 hours'
            );
        """),
            {"albergue_id": POLIDEPORTIVO_ID},
        )

        # 7. Actualizar ocupacion_actual en albergue Polideportivo Oriente
        conn.execute(
            text("""
            UPDATE albergue
            SET ocupacion_actual = (
                SELECT COUNT(*) FROM persona_refugiada
                WHERE albergue_id = :albergue_id AND estado_estancia IN ('albergado', 'salida_temporal')
            ),
            fecha_actualizacion = now()
            WHERE id = :albergue_id;
        """),
            {"albergue_id": POLIDEPORTIVO_ID},
        )

        # 8. Crear usuarios de prueba para Javier (Admin Albergue) y personal operativo
        password_hash = get_password_hash("Javier1234!")
        javier_id = conn.execute(
            text("""
            INSERT INTO "user" (
                id, email, hashed_password, full_name, is_active, is_superuser, rol, created_at
            ) VALUES (
                gen_random_uuid(), 'javier@proteccioncivil.gob.mx', :hash, 'Javier Administrador de Albergue',
                true, false, 'administrador_albergue', now()
            )
            ON CONFLICT (email) DO UPDATE SET
                hashed_password = :hash,
                rol = 'administrador_albergue',
                is_active = true
            RETURNING id;
        """),
            {"hash": password_hash},
        ).scalar()

        # Asignar a Javier en albergue_usuario
        conn.execute(
            text("""
            INSERT INTO albergue_usuario (
                id, albergue_id, usuario_id, rol, area, turno, activo, fecha_asignacion
            ) VALUES (
                gen_random_uuid(), :albergue_id, :usuario_id, 'administrador_albergue', 'general', 'completo', true, now()
            )
            ON CONFLICT DO NOTHING;
        """),
            {"albergue_id": POLIDEPORTIVO_ID, "usuario_id": javier_id},
        )

        hash_logistica = get_password_hash("Logistica1234!")
        logistica_id = conn.execute(
            text("""
            INSERT INTO "user" (
                id, email, hashed_password, full_name, is_active, is_superuser, rol, created_at
            ) VALUES (
                gen_random_uuid(), 'logistica@proteccioncivil.gob.mx', :hash, 'Operador de Logistica',
                true, false, 'personal_operativo', now()
            )
            ON CONFLICT (email) DO UPDATE SET
                hashed_password = :hash,
                rol = 'personal_operativo',
                is_active = true
            RETURNING id;
        """),
            {"hash": hash_logistica},
        ).scalar()

        # Asignar a Logistica en albergue_usuario (bodega_suministros, matutino)
        conn.execute(
            text("""
            INSERT INTO albergue_usuario (
                id, albergue_id, usuario_id, rol, area, turno, activo, fecha_asignacion
            ) VALUES (
                gen_random_uuid(), :albergue_id, :usuario_id, 'personal_operativo', 'bodega_suministros', 'matutino', true, now()
            )
            ON CONFLICT DO NOTHING;
        """),
            {"albergue_id": POLIDEPORTIVO_ID, "usuario_id": logistica_id},
        )

        print("Poblacion de datos de prueba completada exitosamente.")


if __name__ == "__main__":
    poblar()
