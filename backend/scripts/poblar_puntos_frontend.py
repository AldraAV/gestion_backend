import datetime
import uuid

import psycopg

from app.core.config import settings

db_url = str(settings.DATABASE_URL).replace("+psycopg", "")

# 1. Albergues y Centros de Acopio
PUNTOS_APOYO = [
    {
        "folio": "sh-polideportivo",
        "nombre": "Polideportivo Oriente",
        "lat": 22.2412,
        "lon": -97.8215,
        "direccion": "Col. Oriente, Ciudad Madero",
        "municipio": "Ciudad Madero",
        "tipo": "shelter",
        "observaciones": "Capacidad: 250, Disponible: 90, Estado: Abierto",
        "estado_operativo": "activado",
    },
    {
        "folio": "sh-san-lucas",
        "nombre": "Col. San Lucas",
        "lat": 22.2684,
        "lon": -97.8703,
        "direccion": "Col. San Lucas, Tampico",
        "municipio": "Tampico",
        "tipo": "shelter",
        "observaciones": "Capacidad: 180, Disponible: 12, Estado: Casi lleno",
        "estado_operativo": "activado",
    },
    {
        "folio": "cc-centro",
        "nombre": "Acopio Plaza de Armas",
        "lat": 22.2156,
        "lon": -97.8579,
        "direccion": "Centro Histórico, Tampico",
        "municipio": "Tampico",
        "tipo": "collection_center",
        "observaciones": "Recibiendo víveres y agua",
        "estado_operativo": "activado",
    },
    {
        "folio": "hc-uat",
        "nombre": "Centro Universitario UAT Tampico-Madero",
        "lat": 22.2585,
        "lon": -97.8384,
        "direccion": "España 1101, Col. Vicente Guerrero, 89580 Ciudad Madero",
        "municipio": "Ciudad Madero",
        "tipo": "shelter",
        "observaciones": "Centro de apoyo general España 1101 / UAT",
        "estado_operativo": "activado",
    },
]

# 2. Bloqueos de Carretera / Zonas de Riesgo
BLOQUEOS = [
    {
        "codigo": "rb-moctezuma",
        "titulo": "Calle inundada (65 cm)",
        "lat": 22.2378,
        "lon": -97.8652,
        "direccion": "Av. Río Moctezuma esq. Calle 5",
        "radio_km": 0.18,
        "nivel": "roja",
        "descripcion": "Inundación - Calle cerrada",
    },
    {
        "codigo": "rb-puente",
        "titulo": "Árbol y poste derribado",
        "lat": 22.2295,
        "lon": -97.8437,
        "direccion": "Puente Norte Bicentenario",
        "radio_km": 0.12,
        "nivel": "amarillo",
        "descripcion": "Árbol y cables sobre el asfalto - Precaución",
    },
]


def poblar():
    ahora = datetime.datetime.now(datetime.UTC)
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            # 1. Asegurar tabla alerta_zona_riesgo si no existe
            cur.execute("""
                DO $$ BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'nivelalertariesgo') THEN
                        CREATE TYPE nivelalertariesgo AS ENUM ('verde', 'amarillo', 'naranja', 'roja');
                    END IF;
                END $$;

                CREATE TABLE IF NOT EXISTS alerta_zona_riesgo (
                    id UUID PRIMARY KEY,
                    codigo_alerta VARCHAR(50) UNIQUE NOT NULL,
                    titulo VARCHAR(255) NOT NULL,
                    tipo_fenomeno VARCHAR(100) DEFAULT 'Hidrometeorologico',
                    nivel_alerta nivelalertariesgo DEFAULT 'amarillo',
                    descripcion VARCHAR(2000) NOT NULL,
                    cuenca_rio VARCHAR(150),
                    nivel_actual_metros FLOAT,
                    nivel_critico_desbordamiento FLOAT,
                    municipios_afectados VARCHAR(1000),
                    latitud_referencia FLOAT,
                    longitud_referencia FLOAT,
                    radio_afectacion_km FLOAT,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_emision TIMESTAMP WITH TIME ZONE NOT NULL,
                    fecha_vigencia TIMESTAMP WITH TIME ZONE
                );
            """)

            # 2. Insertar o actualizar Puntos de Apoyo / Albergues
            for p in PUNTOS_APOYO:
                cur.execute(
                    "SELECT id FROM albergue WHERE folio_identificador = %s",
                    (p["folio"],),
                )
                existente = cur.fetchone()
                if existente:
                    cur.execute(
                        """
                        UPDATE albergue SET
                            nombre = %s, latitud = %s, longitud = %s, direccion = %s,
                            municipio = %s, tipo_inmueble = %s, observaciones = %s,
                            fecha_actualizacion = %s
                        WHERE id = %s
                    """,
                        (
                            p["nombre"],
                            p["lat"],
                            p["lon"],
                            p["direccion"],
                            p["municipio"],
                            p["tipo"],
                            p["observaciones"],
                            ahora,
                            existente[0],
                        ),
                    )
                    print(f"[ALBERGUE ACTUALIZADO] {p['folio']} -> {p['nombre']}")
                else:
                    nuevo_id = uuid.uuid4()
                    cur.execute(
                        """
                        INSERT INTO albergue (
                            id, folio_identificador, nombre, direccion, municipio,
                            estado_republica, latitud, longitud, tipo_inmueble,
                            observaciones, admite_mascotas, estado_operativo,
                            fecha_registro, fecha_actualizacion
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """,
                        (
                            nuevo_id,
                            p["folio"],
                            p["nombre"],
                            p["direccion"],
                            p["municipio"],
                            "Tamaulipas",
                            p["lat"],
                            p["lon"],
                            p["tipo"],
                            p["observaciones"],
                            True,
                            p["estado_operativo"],
                            ahora,
                            ahora,
                        ),
                    )
                    print(
                        f"[ALBERGUE INSERTADO] {p['folio']} -> {p['nombre']} (ID: {nuevo_id})"
                    )

            # 3. Insertar o actualizar Bloqueos / Zonas de Riesgo
            for b in BLOQUEOS:
                cur.execute(
                    "SELECT id FROM alerta_zona_riesgo WHERE codigo_alerta = %s",
                    (b["codigo"],),
                )
                existente = cur.fetchone()
                if existente:
                    cur.execute(
                        """
                        UPDATE alerta_zona_riesgo SET
                            titulo = %s, latitud_referencia = %s, longitud_referencia = %s,
                            radio_afectacion_km = %s, nivel_alerta = %s, descripcion = %s
                        WHERE id = %s
                    """,
                        (
                            b["titulo"],
                            b["lat"],
                            b["lon"],
                            b["radio_km"],
                            b["nivel"],
                            b["descripcion"],
                            existente[0],
                        ),
                    )
                    print(f"[BLOQUEO ACTUALIZADO] {b['codigo']} -> {b['titulo']}")
                else:
                    nuevo_id = uuid.uuid4()
                    cur.execute(
                        """
                        INSERT INTO alerta_zona_riesgo (
                            id, codigo_alerta, titulo, latitud_referencia,
                            longitud_referencia, radio_afectacion_km, nivel_alerta,
                            descripcion, fecha_emision, activo
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """,
                        (
                            nuevo_id,
                            b["codigo"],
                            b["titulo"],
                            b["lat"],
                            b["lon"],
                            b["radio_km"],
                            b["nivel"],
                            b["descripcion"],
                            ahora,
                            True,
                        ),
                    )
                    print(
                        f"[BLOQUEO INSERTADO] {b['codigo']} -> {b['titulo']} (ID: {nuevo_id})"
                    )

            conn.commit()
            print("TODOS LOS PUNTOS FUERON REGISTRADOS EXITOSAMENTE EN SUPABASE")


if __name__ == "__main__":
    poblar()
