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


# Catalogo base infalible en memoria
PUNTOS_PREDETERMINADOS: list[dict[str, Any]] = [
    {
        "id": "sh-polideportivo",
        "type": "shelter",
        "name": "Polideportivo Oriente",
        "latitude": 22.2412,
        "longitude": -97.8215,
        "address": "Col. Oriente, Ciudad Madero",
        "capacity": 250,
        "available": 90,
        "status": "Abierto",
    },
    {
        "id": "sh-san-lucas",
        "type": "shelter",
        "name": "Col. San Lucas",
        "latitude": 22.2684,
        "longitude": -97.8703,
        "address": "Col. San Lucas, Tampico",
        "capacity": 180,
        "available": 12,
        "status": "Casi lleno",
    },
    {
        "id": "hc-uat",
        "type": "shelter",
        "name": "Centro Universitario UAT Tampico-Madero",
        "latitude": 22.2585,
        "longitude": -97.8384,
        "address": "España 1101, Col. Vicente Guerrero, 89580 Ciudad Madero",
        "capacity": 300,
        "available": 150,
        "status": "Abierto",
    },
    {
        "id": "cc-centro",
        "type": "collection_center",
        "name": "Acopio Plaza de Armas",
        "latitude": 22.2156,
        "longitude": -97.8579,
        "address": "Centro Histórico, Tampico",
        "status": "Recibiendo víveres y agua",
    },
    {
        "id": "rb-moctezuma",
        "type": "road_block",
        "name": "Calle inundada (65 cm)",
        "latitude": 22.2378,
        "longitude": -97.8652,
        "address": "Av. Moctezuma esq. Ejército Mexicano",
        "severity": "high",
        "status": "Inundado - Tráfico cerrado",
    },
    {
        "id": "rb-puente",
        "type": "road_block",
        "name": "Árbol y poste derribado",
        "latitude": 22.2295,
        "longitude": -97.8437,
        "address": "Paso del Humo / Ribera",
        "severity": "medium",
        "status": "Parcialmente obstruido",
    },
]


def consultar_ubicaciones_base_datos() -> list[dict[str, Any]]:
    """
    Obtiene las ubicaciones activas desde Supabase PostgreSQL.
    Si la base de datos no esta disponible o vacia, retorna la salvaguarda predeterminada.
    """
    cadena_conexion = str(settings.DATABASE_URL).replace("+psycopg", "")
    puntos: list[dict[str, Any]] = []

    try:
        with psycopg.connect(cadena_conexion) as conexion:
            with conexion.cursor() as cursor:
                # 1. Albergues y Centros de Apoyo
                cursor.execute("""
                    SELECT folio_identificador, nombre, latitud, longitud, direccion, tipo_inmueble, observaciones
                    FROM albergue
                    WHERE latitud IS NOT NULL AND longitud IS NOT NULL
                """)
                for fila in cursor.fetchall():
                    folio, nombre, lat, lon, dir_texto, tipo_inm, obs = fila
                    tipo_valor = "shelter"
                    if tipo_inm and "collection" in str(tipo_inm).lower():
                        tipo_valor = "collection_center"

                    capacidad = None
                    disponible = None
                    estado_texto = "Abierto"

                    if obs:
                        for parte in str(obs).split(","):
                            parte_limpia = parte.strip()
                            if "Capacidad:" in parte_limpia:
                                try:
                                    capacidad = int(parte_limpia.split(":")[1].strip())
                                except (ValueError, IndexError):
                                    pass
                            elif "Disponible:" in parte_limpia:
                                try:
                                    disponible = int(parte_limpia.split(":")[1].strip())
                                except (ValueError, IndexError):
                                    pass
                            elif "Estado:" in parte_limpia:
                                estado_texto = parte_limpia.split(":")[1].strip()

                    puntos.append(
                        {
                            "id": folio or str(nombre).lower().replace(" ", "-"),
                            "type": tipo_valor,
                            "name": nombre,
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
