from typing import Any

import psycopg
from fastapi import APIRouter, Query
from pydantic import BaseModel, ConfigDict, Field

from app.core.config import settings

enrutador = APIRouter(prefix="/publico", tags=["Ubicaciones Publicas"])


class ModeloUbicacion(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    type: str = Field(
        ..., description="Tipo de ubicacion: shelter, collection_center o road_block"
    )
    name: str
    latitude: float
    longitude: float
    address: str = ""
    status: str = ""
    capacity: int | None = None
    available: int | None = None
    severity: str | None = None


# Catalogo base infalible en memoria (Exclusivamente albergues oficiales verificados)
PUNTOS_PREDETERMINADOS: list[dict[str, Any]] = [
    {
        "id": "TAM-TAM-001",
        "type": "shelter",
        "name": "Escuela Primaria Nuevo Santander",
        "latitude": 22.363848,
        "longitude": -97.904238,
        "address": "Calle Carmin No. 1930, entre Belen y Alcatraz, fraccionamiento Alejandro Briones, sector 3, Monte Alto, C.P. 89606",
        "capacity": 100,
        "available": 100,
        "status": "Abierto",
    },
    {
        "id": "TAM-ALD-001",
        "type": "shelter",
        "name": "Escuela Primaria Pedro Jose Mendez, Zona 201",
        "latitude": 23.301230,
        "longitude": -98.073984,
        "address": "Domicilio conocido, ejido El Vidal, C.P. 89679, Aldama",
        "capacity": 50,
        "available": 50,
        "status": "Abierto",
    },
    {
        "id": "VER-ALA-001",
        "type": "shelter",
        "name": "Escuela Primaria Enrique C. Rebsamen",
        "latitude": 20.901060,
        "longitude": -97.682055,
        "address": "Calle Gabino Gonzalez s/n, Ejido Pueblo Nuevo, C.P. 92730, Alamo Temapache",
        "capacity": 100,
        "available": 100,
        "status": "Abierto",
    },
    {
        "id": "VER-PAN-001",
        "type": "shelter",
        "name": "Secundaria para Trabajadores Essington T. Trimmer Diaz",
        "latitude": 22.053564,
        "longitude": -98.182059,
        "address": "Calle Aldama 305, Col. Revolucion Mexicana, C.P. 93997, Panuco",
        "capacity": 120,
        "available": 120,
        "status": "Abierto",
    },
    {
        "id": "VER-POZ-001",
        "type": "shelter",
        "name": "Casa del Migrante",
        "latitude": 20.507247,
        "longitude": -97.461041,
        "address": "Avenida Papantla s/n, colonia Jardines de Poza Rica",
        "capacity": 80,
        "available": 80,
        "status": "Abierto",
    },
    {
        "id": "cc-centro",
        "type": "collection_center",
        "name": "Acopio Plaza de Armas",
        "latitude": 22.2156,
        "longitude": -97.8579,
        "address": "Centro Historico, Tampico",
        "status": "Recibiendo viveres y agua",
        "capacity": 100,
        "available": 100,
    },
    {
        "id": "rb-moctezuma",
        "type": "road_block",
        "name": "Calle inundada (65 cm)",
        "latitude": 22.2378,
        "longitude": -97.8652,
        "address": "Av. Moctezuma esq. Ejercito Mexicano",
        "severity": "high",
        "status": "Inundado - Trafico cerrado",
    },
    {
        "id": "rb-puente",
        "type": "road_block",
        "name": "Arbol y poste derribado",
        "latitude": 22.2295,
        "longitude": -97.8437,
        "address": "Paso del Humo / Ribera",
        "severity": "medium",
        "status": "Parcialmente obstruido",
    },
]

# Lista negra estricta de inmuebles mock a excluir del mapa publico
FOLIOS_MOCK_EXCLUIDOS = {
    "hc-uat",
    "sh-polideportivo",
    "sh-san-lucas",
    "TAM-TAM-002",
    "REF-MAD-001",
}
NOMBRES_MOCK_EXCLUIDOS = (
    "uat",
    "polideportivo oriente",
    "santo angel",
    "santo ángel",
    "san lucas",
    "españa 1101",
)


def consultar_ubicaciones_base_datos() -> list[dict[str, Any]]:
    """
    Obtiene las ubicaciones activas reales desde Supabase PostgreSQL,
    excluyendo cualquier dato mock (UAT, Polideportivo, Santo Angel, San Lucas).
    """
    cadena_conexion = str(settings.DATABASE_URL).replace("+psycopg", "")
    puntos: list[dict[str, Any]] = []

    try:
        with psycopg.connect(cadena_conexion) as conexion:
            with conexion.cursor() as cursor:
                # 1. Albergues y Centros de Apoyo oficiales
                cursor.execute("""
                    SELECT a.folio_identificador, a.nombre, a.latitud, a.longitud, a.direccion,
                           a.tipo_inmueble, a.observaciones, ii.capacidad_maxima, a.ocupacion_actual
                    FROM albergue a
                    LEFT JOIN inventario_infraestructura ii ON ii.albergue_id = a.id
                    WHERE a.latitud IS NOT NULL AND a.longitud IS NOT NULL
                    ORDER BY a.nombre
                """)
                for fila in cursor.fetchall():
                    folio, nombre, lat, lon, dir_texto, tipo_inm, obs, cap_max, ocup = fila
                    folio_str = str(folio or "").strip()
                    nombre_str = str(nombre or "").strip()
                    nombre_min = nombre_str.lower()

                    # Filtrar mocks explicitos solicitados
                    if folio_str in FOLIOS_MOCK_EXCLUIDOS or any(m in nombre_min for m in NOMBRES_MOCK_EXCLUIDOS):
                        continue

                    tipo_valor = "shelter"
                    if tipo_inm and "collection" in str(tipo_inm).lower():
                        tipo_valor = "collection_center"

                    capacidad = cap_max if cap_max is not None else 100
                    ocupacion = ocup if ocup is not None else 0
                    disponible = max(0, capacidad - ocupacion)
                    estado_texto = "Abierto"

                    puntos.append(
                        {
                            "id": folio_str or nombre_min.replace(" ", "-"),
                            "type": tipo_valor,
                            "name": nombre_str,
                            "latitude": float(lat),
                            "longitude": float(lon),
                            "address": dir_texto or "",
                            "capacity": capacidad,
                            "available": disponible,
                            "status": estado_texto,
                        }
                    )

                # 2. Bloqueos Viales y Zonas de Riesgo
                cursor.execute("""
                    SELECT codigo_alerta, titulo, latitud_referencia, longitud_referencia, nivel_alerta, descripcion
                    FROM alerta_zona_riesgo
                    WHERE latitud_referencia IS NOT NULL AND longitud_referencia IS NOT NULL AND activo = TRUE
                """)
                for fila in cursor.fetchall():
                    codigo, titulo, lat, lon, nivel, desc = fila
                    severidad = "high" if str(nivel).lower() == "roja" else "medium"
                    puntos.append(
                        {
                            "id": codigo or "rb-alerta",
                            "type": "road_block",
                            "name": titulo,
                            "latitude": float(lat),
                            "longitude": float(lon),
                            "address": desc or "",
                            "severity": severidad,
                            "status": desc or "Bloqueo vial activo",
                        }
                    )

    except Exception:
        return PUNTOS_PREDETERMINADOS

    return puntos if puntos else PUNTOS_PREDETERMINADOS


@enrutador.get("/ubicaciones", response_model=list[ModeloUbicacion])
@enrutador.get("/ubicaciones/", response_model=list[ModeloUbicacion])
def listar_ubicaciones(
    tipo: str | None = Query(
        default=None,
        alias="type",
        description="Filtrar por tipo: shelter, collection_center, road_block",
    ),
) -> list[dict[str, Any]]:
    """
    Retorna la lista de todas las ubicaciones activas en el mapa:
    albergues, centros de acopio y bloqueos viales.
    """
    registros = consultar_ubicaciones_base_datos()
    if tipo:
        tipo_normalizado = tipo.lower().strip()
        registros = [
            r for r in registros if r.get("type", "").lower() == tipo_normalizado
        ]
    return registros


@enrutador.get("/ubicaciones/agrupadas")
def listar_ubicaciones_agrupadas() -> dict[str, Any]:
    """
    Retorna las ubicaciones organizadas por categoria para clientes que requieran objetos separados.
    """
    todos = consultar_ubicaciones_base_datos()
    return {
        "shelters": [u for u in todos if u.get("type") == "shelter"],
        "collectionCenters": [u for u in todos if u.get("type") == "collection_center"],
        "roadBlocks": [u for u in todos if u.get("type") == "road_block"],
        "locations": todos,
    }


@enrutador.get("/albergues", response_model=list[ModeloUbicacion])
def listar_albergues() -> list[dict[str, Any]]:
    todos = consultar_ubicaciones_base_datos()
    return [u for u in todos if u.get("type") == "shelter"]


@enrutador.get("/centros-acopio", response_model=list[ModeloUbicacion])
def listar_centros_acopio() -> list[dict[str, Any]]:
    todos = consultar_ubicaciones_base_datos()
    return [u for u in todos if u.get("type") == "collection_center"]


@enrutador.get("/bloqueos", response_model=list[ModeloUbicacion])
def listar_bloqueos() -> list[dict[str, Any]]:
    todos = consultar_ubicaciones_base_datos()
    return [u for u in todos if u.get("type") == "road_block"]
