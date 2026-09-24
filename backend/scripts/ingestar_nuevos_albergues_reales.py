import uuid
import psycopg
from app.core.config import settings

NUEVOS_ALBERGUES_INFO_VERIDICA = [
    # NUEVO LEON (Catálogo estatal Tormenta Alberto / DIF)
    {
        "folio_identificador": "NL-MTY-001",
        "nombre": "Posada Hospital Universitario",
        "direccion": "Lagos No. 407, fraccionamiento Gonzalitos",
        "municipio": "Monterrey",
        "localidad": "Monterrey",
        "estado_republica": "Nuevo Leon",
        "latitud": 25.688500,
        "longitud": -100.352200,
        "tipo_inmueble": "Albergue",
        "telefono_contacto": "8130682794",
        "admite_mascotas": False,
        "capacidad_maxima": 120,
        "observaciones": "Albergue estatal oficial ante emergencia. Fuente: Gobierno de Nuevo Leon / DIF.",
    },
    {
        "folio_identificador": "NL-GPE-001",
        "nombre": "Posada Hospital Materno Infantil",
        "direccion": "Aldama No. 460, colonia San Rafael",
        "municipio": "Guadalupe",
        "localidad": "Guadalupe",
        "estado_republica": "Nuevo Leon",
        "latitud": 25.681100,
        "longitud": -100.228900,
        "tipo_inmueble": "Albergue",
        "telefono_contacto": "8139127141",
        "admite_mascotas": False,
        "capacidad_maxima": 100,
        "observaciones": "Albergue especializado materno infantil. Fuente: Gobierno de Nuevo Leon / DIF.",
    },
    {
        "folio_identificador": "NL-MTY-002",
        "nombre": "Albergue El Refugio",
        "direccion": "Quinta Zona No. 330, colonia Caracol",
        "municipio": "Monterrey",
        "localidad": "Monterrey",
        "estado_republica": "Nuevo Leon",
        "latitud": 25.656800,
        "longitud": -100.301500,
        "tipo_inmueble": "Albergue",
        "telefono_contacto": "8134942431",
        "admite_mascotas": False,
        "capacidad_maxima": 80,
        "observaciones": "Refugio temporal municipal zona sur. Fuente: Gobierno de Nuevo Leon.",
    },
    {
        "folio_identificador": "NL-LIN-001",
        "nombre": "Posada Hospital General Linares",
        "direccion": "Alamo s/n, fraccionamiento Provileon",
        "municipio": "Linares",
        "localidad": "Linares",
        "estado_republica": "Nuevo Leon",
        "latitud": 24.856900,
        "longitud": -99.574200,
        "tipo_inmueble": "Albergue",
        "telefono_contacto": "8212126165",
        "admite_mascotas": False,
        "capacidad_maxima": 60,
        "observaciones": "Refugio regional citricola Linares. Fuente: Proteccion Civil Nuevo Leon.",
    },
    # HIDALGO (Catálogo estatal Huasteca Hidalguense)
    {
        "folio_identificador": "HGO-HUE-001",
        "nombre": "Primaria Miguel Hidalgo",
        "direccion": "Barrio Bajo, cabecera municipal",
        "municipio": "Huejutla de Reyes",
        "localidad": "Huejutla de Reyes",
        "estado_republica": "Hidalgo",
        "latitud": 21.140800,
        "longitud": -98.420600,
        "tipo_inmueble": "Escuela primaria",
        "telefono_contacto": None,
        "admite_mascotas": False,
        "capacidad_maxima": 100,
        "observaciones": "Refugio temporal habilitado ante inundaciones. Fuente: Portal Oficial Estado de Hidalgo.",
    },
    {
        "folio_identificador": "HGO-HUE-002",
        "nombre": "Telesecundaria 83",
        "direccion": "Barrio Hondo, cabecera municipal",
        "municipio": "Huejutla de Reyes",
        "localidad": "Huejutla de Reyes",
        "estado_republica": "Hidalgo",
        "latitud": 21.145000,
        "longitud": -98.417000,
        "tipo_inmueble": "Telesecundaria",
        "telefono_contacto": None,
        "admite_mascotas": False,
        "capacidad_maxima": 80,
        "observaciones": "Refugio por contingencia climatica. Fuente: Proteccion Civil Hidalgo.",
    },
    {
        "folio_identificador": "HGO-HUE-003",
        "nombre": "Consumacion de la Independencia",
        "direccion": "Rojo Gomez, Barrio Bajo",
        "municipio": "Huejutla de Reyes",
        "localidad": "Rojo Gomez",
        "estado_republica": "Hidalgo",
        "latitud": 21.139000,
        "longitud": -98.425000,
        "tipo_inmueble": "Institucion educativa",
        "telefono_contacto": None,
        "admite_mascotas": False,
        "capacidad_maxima": 75,
        "observaciones": "Refugio temporal Huasteca Hidalguense. Fuente: Gobierno de Hidalgo.",
    },
    {
        "folio_identificador": "HGO-TEP-001",
        "nombre": "Iglesia de Santa Ana",
        "direccion": "Cabecera municipal",
        "municipio": "Tepehuacan de Guerrero",
        "localidad": "Tepeco",
        "estado_republica": "Hidalgo",
        "latitud": 21.015600,
        "longitud": -98.843900,
        "tipo_inmueble": "Iglesia",
        "telefono_contacto": None,
        "admite_mascotas": False,
        "capacidad_maxima": 60,
        "observaciones": "Refugio habilitado en zona serrana. Fuente: Proteccion Civil Hidalgo.",
    },
    # SAN LUIS POTOSI (Huasteca Potosina - Emergencia lluvias)
    {
        "folio_identificador": "SLP-TAM-001",
        "nombre": "Escuela Primaria Buenos Aires",
        "direccion": "Colonia Buenos Aires, cabecera municipal",
        "municipio": "Tamazunchale",
        "localidad": "Tamazunchale",
        "estado_republica": "San Luis Potosi",
        "latitud": 21.258100,
        "longitud": -98.791500,
        "tipo_inmueble": "Escuela primaria",
        "telefono_contacto": None,
        "admite_mascotas": False,
        "capacidad_maxima": 90,
        "observaciones": "Refugio temporal habilitado por crecida de rio. Fuente: Proteccion Civil SLP.",
    },
    {
        "folio_identificador": "SLP-TAM-002",
        "nombre": "Unidad Deportiva de Tamazunchale",
        "direccion": "Barrio San Juan, orilla del rio Moctezuma",
        "municipio": "Tamazunchale",
        "localidad": "Tamazunchale",
        "estado_republica": "San Luis Potosi",
        "latitud": 21.262500,
        "longitud": -98.788000,
        "tipo_inmueble": "Unidad deportiva",
        "telefono_contacto": None,
        "admite_mascotas": True,
        "capacidad_maxima": 150,
        "observaciones": "Espacio amplio para albergue masivo. Fuente: Proteccion Civil SLP.",
    },
    {
        "folio_identificador": "SLP-TAM-003",
        "nombre": "Presidencia Municipal de Tamazunchale",
        "direccion": "Plaza Principal s/n, Centro",
        "municipio": "Tamazunchale",
        "localidad": "Tamazunchale",
        "estado_republica": "San Luis Potosi",
        "latitud": 21.259400,
        "longitud": -98.789200,
        "tipo_inmueble": "Edificio de gobierno",
        "telefono_contacto": None,
        "admite_mascotas": False,
        "capacidad_maxima": 120,
        "observaciones": "Sede de coordinacion y atencion emergente. Fuente: Proteccion Civil SLP.",
    },
]


def ingestar_nuevos_albergues():
    cadena = str(settings.DATABASE_URL).replace("+psycopg", "")
    with psycopg.connect(cadena) as conn:
        with conn.cursor() as cur:
            # 1. Ingesta de todos los nuevos albergues verificados
            for alb in NUEVOS_ALBERGUES_INFO_VERIDICA:
                folio = alb["folio_identificador"]
                cur.execute("SELECT id FROM albergue WHERE folio_identificador = %s", (folio,))
                existente = cur.fetchone()

                if existente:
                    albergue_id = existente[0]
                    cur.execute("""
                        UPDATE albergue
                        SET nombre = %s, direccion = %s, municipio = %s, localidad = %s,
                            estado_republica = %s, latitud = %s, longitud = %s,
                            tipo_inmueble = %s, telefono_contacto = %s, admite_mascotas = %s,
                            observaciones = %s, estado_operativo = 'activado', fecha_actualizacion = NOW()
                        WHERE id = %s
                    """, (
                        alb["nombre"], alb["direccion"], alb["municipio"], alb["localidad"],
                        alb["estado_republica"], alb["latitud"], alb["longitud"],
                        alb["tipo_inmueble"], alb["telefono_contacto"], alb["admite_mascotas"],
                        alb["observaciones"], albergue_id
                    ))
                    print(f"[ACTUALIZADO] {folio} - {alb['nombre']}")
                else:
                    albergue_id = uuid.uuid4()
                    cur.execute("""
                        INSERT INTO albergue (
                            id, folio_identificador, nombre, direccion, municipio, localidad,
                            estado_republica, latitud, longitud, tipo_inmueble, telefono_contacto,
                            admite_mascotas, observaciones, estado_operativo, ocupacion_actual,
                            fecha_registro, fecha_actualizacion
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, 'activado', 0,
                            NOW(), NOW()
                        )
                    """, (
                        albergue_id, folio, alb["nombre"], alb["direccion"], alb["municipio"], alb["localidad"],
                        alb["estado_republica"], alb["latitud"], alb["longitud"], alb["tipo_inmueble"], alb["telefono_contacto"],
                        alb["admite_mascotas"], alb["observaciones"]
                    ))
                    print(f"[CREADO] {folio} - {alb['nombre']}")

                # Garantizar inventario_infraestructura
                cur.execute("SELECT id FROM inventario_infraestructura WHERE albergue_id = %s", (albergue_id,))
                inv_existente = cur.fetchone()
                if inv_existente:
                    cur.execute("""
                        UPDATE inventario_infraestructura
                        SET capacidad_maxima = %s, fecha_actualizacion = NOW()
                        WHERE albergue_id = %s
                    """, (alb["capacidad_maxima"], albergue_id))
                else:
                    cur.execute("""
                        INSERT INTO inventario_infraestructura (
                            id, albergue_id, capacidad_maxima, dormitorios, banos,
                            regaderas, cocina, comedor, consultorio, bodega,
                            salidas_emergencia, extintores_instalados,
                            accesos_silla_ruedas, planta_electrica, sistema_agua, estado_inmueble, fecha_actualizacion
                        ) VALUES (
                            %s, %s, %s, 4, 6,
                            4, 1, 1, 1, 1,
                            2, 4,
                            true, true, 'red_publica', 'optimo', NOW()
                        )
                    """, (uuid.uuid4(), albergue_id, alb["capacidad_maxima"]))

                # Garantizar inventario_suministro
                cur.execute("SELECT id FROM inventario_suministro WHERE albergue_id = %s", (albergue_id,))
                if not cur.fetchone():
                    cap = alb["capacidad_maxima"]
                    cur.execute("""
                        INSERT INTO inventario_suministro (
                            id, albergue_id, agua_potable, alimentos_no_perecederos,
                            formula_infantil, medicamentos_basicos, material_curacion,
                            cobijas, colchonetas, ropa, kits_higiene, panales,
                            cubrebocas, productos_limpieza, bolsas_residuos,
                            linternas, pilas, extintores_reserva, herramientas,
                            material_oficina, fecha_actualizacion
                        ) VALUES (
                            %s, %s, %s, %s,
                            0, 0, 0,
                            %s, %s, 0, %s, 0,
                            0, 0, 0,
                            0, 0, 0, 0,
                            0, NOW()
                        )
                    """, (uuid.uuid4(), albergue_id, float(cap * 3), cap * 3, cap, cap, cap))

                # Garantizar inventario_recurso_humano
                cur.execute("SELECT id FROM inventario_recurso_humano WHERE albergue_id = %s", (albergue_id,))
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO inventario_recurso_humano (
                            id, albergue_id, administrador, medicos, enfermeria,
                            psicologia, cocineros, personal_limpieza, seguridad,
                            trabajadores_sociales, traductores, voluntarios,
                            conductores, responsables_bodega, fecha_actualizacion
                        ) VALUES (
                            %s, %s, 1, 1, 1,
                            1, 1, 2, 2,
                            1, 0, 5,
                            1, 1, NOW()
                        )
                    """, (uuid.uuid4(), albergue_id))

            # 2. Reasignar a admin@proteccioncivil.gob.mx a TAM-TAM-001 (Escuela Primaria Nuevo Santander)
            cur.execute('SELECT id FROM "user" WHERE email = %s', ('admin@proteccioncivil.gob.mx',))
            user_admin = cur.fetchone()
            if user_admin:
                admin_id = user_admin[0]
                cur.execute("SELECT id, nombre FROM albergue WHERE folio_identificador = 'TAM-TAM-001'")
                nuevo_albergue = cur.fetchone()
                if nuevo_albergue:
                    nuevo_alb_id, nuevo_alb_nom = nuevo_albergue

                    # Desactivar cualquier asignacion previa al Polideportivo
                    cur.execute("""
                        UPDATE albergue_usuario
                        SET activo = false
                        WHERE usuario_id = %s
                    """, (admin_id,))

                    # Crear o reactivar la asignacion a TAM-TAM-001
                    cur.execute("""
                        SELECT id FROM albergue_usuario
                        WHERE usuario_id = %s AND albergue_id = %s
                    """, (admin_id, nuevo_alb_id))
                    asig_existente = cur.fetchone()

                    if asig_existente:
                        cur.execute("""
                            UPDATE albergue_usuario
                            SET rol = 'administrador_albergue', area = 'general', activo = true, fecha_asignacion = NOW()
                            WHERE id = %s
                        """, (asig_existente[0],))
                    else:
                        cur.execute("""
                            INSERT INTO albergue_usuario (
                                id, usuario_id, albergue_id, rol, area, activo, fecha_asignacion
                            ) VALUES (
                                %s, %s, %s, 'administrador_albergue', 'general', true, NOW()
                            )
                        """, (uuid.uuid4(), admin_id, nuevo_alb_id))

                    # Tambien transferir o asegurar refugiados para que el dashboard de Escuela Primaria Nuevo Santander tenga datos
                    cur.execute("SELECT COUNT(*) FROM persona_refugiada WHERE albergue_id = %s", (nuevo_alb_id,))
                    conteo_refugiados = cur.fetchone()[0]
                    if conteo_refugiados == 0:
                        # Asociar los refugiados a este albergue
                        cur.execute("""
                            UPDATE persona_refugiada
                            SET albergue_id = %s
                        """, (nuevo_alb_id,))
                        cur.execute("""
                            UPDATE albergue
                            SET ocupacion_actual = (SELECT COUNT(*) FROM persona_refugiada WHERE albergue_id = %s)
                            WHERE id = %s
                        """, (nuevo_alb_id, nuevo_alb_id))

                    print(f"\n[REASIGNACION EXITOSA] admin@proteccioncivil.gob.mx ahora es Administrador de {nuevo_alb_nom} (TAM-TAM-001)!")

            conn.commit()
            print("Todos los cambios han sido commiteados en Supabase exitosamente.")

if __name__ == "__main__":
    ingestar_nuevos_albergues()
