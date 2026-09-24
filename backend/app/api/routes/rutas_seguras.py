import uuid
from typing import Any

import psycopg
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from app.adapters.cliente_mapbox import ErrorCalculoRuta, obtener_ruta_mapbox
from app.core.config import settings

router = APIRouter(prefix="/publico/rutas", tags=["Rutas Seguras"])


class CoordenadasPunto(BaseModel):
    latitude: float
    longitude: float


class DestinoInfo(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float


class SegmentoRuta(BaseModel):
    distanceMeters: float
    durationSeconds: float
    instruction: str


class SolicitudRuta(BaseModel):
    """
    Soporta tanto la especificacion del frontend del pair programmer (camelCase):
      { siteId: string, latitude: number, longitude: number }
    como variantes en snake_case o en espanol.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    siteId: str = Field(default="", validation_alias="site_id")
    latitude: float = Field(..., validation_alias="latitud")
    longitude: float = Field(..., validation_alias="longitud")


class RespuestaRuta(BaseModel):
    """
    Contrato exacto requerido por el frontend del pair programmer:
    {
      routeId: string,
      origin: { latitude, longitude },
      destination: { id, name, latitude, longitude },
      distanceMeters: number,
      durationSeconds: number,
      geometry: [longitude, latitude][],   // LineString en orden Mapbox
      segments: { distanceMeters, durationSeconds, instruction }[],
    }
    """

    routeId: str
    origin: CoordenadasPunto
    destination: DestinoInfo
    distanceMeters: float
    durationSeconds: float
    geometry: list[list[float]]
    segments: list[SegmentoRuta]


# Mocks que nunca deben ser seleccionados como destino
MOCKS_DESTINO_EXCLUIDOS = {
    "hc-uat",
    "sh-polideportivo",
    "sh-san-lucas",
    "TAM-TAM-002",
    "REF-MAD-001",
}
NOMBRES_DESTINO_EXCLUIDOS = (
    "uat",
    "polideportivo oriente",
    "santo angel",
    "santo ángel",
    "san lucas",
    "españa 1101",
)


def obtener_puntos_incidencia_activos() -> list[tuple[float, float]]:
    """
    Obtiene las coordenadas (longitud, latitud) de bloqueos viales e incidencias
    activas en Supabase para alimentarlas al motor de evasion de Mapbox.
    """
    puntos: list[tuple[float, float]] = []
    db_url = str(settings.DATABASE_URL).replace("+psycopg", "")
    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT longitud_referencia, latitud_referencia
                    FROM alerta_zona_riesgo
                    WHERE activo = true
                      AND latitud_referencia IS NOT NULL
                      AND longitud_referencia IS NOT NULL
                """)
                for lon, lat in cur.fetchall():
                    puntos.append((float(lon), float(lat)))
    except Exception:
        # Puntos de bloqueo conocidos de salvaguarda (Moctezuma y Paso del Humo)
        puntos = [(-97.8652, 22.2378), (-97.8437, 22.2295)]
    return puntos


def buscar_albergue_destino(
    site_id: str, lat_origen: float = 22.2170, lon_origen: float = -97.8728
) -> dict[str, Any]:
    """
    Busca el albergue de destino en Supabase PostgreSQL.
    Si se proporciona un site_id valido, busca coincidencia exacta.
    Si site_id es vacio o no existe, calcula el albergue oficial real mas cercano
    a las coordenadas geograficas actuales del dispositivo (lat_origen, lon_origen).
    """
    db_url = str(settings.DATABASE_URL).replace("+psycopg", "")
    albergue = None

    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                # 1. Intentar por UUID si el site_id tiene formato UUID y no es mock
                if site_id:
                    try:
                        uuid_val = uuid.UUID(site_id)
                        cur.execute(
                            """
                            SELECT id, nombre, latitud, longitud
                            FROM albergue
                            WHERE id = %s
                              AND folio_identificador NOT IN ('hc-uat', 'sh-polideportivo', 'sh-san-lucas', 'TAM-TAM-002', 'REF-MAD-001')
                            """,
                            (uuid_val,),
                        )
                        albergue = cur.fetchone()
                    except (ValueError, AttributeError):
                        pass

                # 2. Intentar por folio_identificador o nombre si no es mock
                if not albergue and site_id:
                    cur.execute(
                        """
                        SELECT id, nombre, latitud, longitud
                        FROM albergue
                        WHERE (folio_identificador = %s OR nombre ILIKE %s)
                          AND folio_identificador NOT IN ('hc-uat', 'sh-polideportivo', 'sh-san-lucas', 'TAM-TAM-002', 'REF-MAD-001')
                          AND nombre NOT ILIKE '%uat%'
                          AND nombre NOT ILIKE '%polideportivo%'
                          AND nombre NOT ILIKE '%santo angel%'
                          AND nombre NOT ILIKE '%santo ángel%'
                          AND nombre NOT ILIKE '%san lucas%'
                        LIMIT 1
                        """,
                        (site_id, f"%{site_id}%"),
                    )
                    albergue = cur.fetchone()

                # 3. Si no se especifico site_id o no se encontro, buscar el albergue REAL
                # mas cercano geograficamente a la ubicacion del dispositivo del usuario
                if not albergue:
                    cur.execute(
                        """
                        SELECT id, nombre, latitud, longitud
                        FROM albergue
                        WHERE latitud IS NOT NULL AND longitud IS NOT NULL
                          AND folio_identificador NOT IN ('hc-uat', 'sh-polideportivo', 'sh-san-lucas', 'TAM-TAM-002', 'REF-MAD-001')
                          AND nombre NOT ILIKE '%uat%'
                          AND nombre NOT ILIKE '%polideportivo%'
                          AND nombre NOT ILIKE '%santo angel%'
                          AND nombre NOT ILIKE '%santo ángel%'
                          AND nombre NOT ILIKE '%san lucas%'
                          AND nombre NOT ILIKE '%españa 1101%'
                        ORDER BY ((latitud - %s)^2 + (longitud - %s)^2) ASC
                        LIMIT 1
                        """,
                        (lat_origen, lon_origen),
                    )
                    albergue = cur.fetchone()
    except Exception:
        pass

    # Salvaguarda oficial: Escuela Primaria Nuevo Santander (Altamira / Tampico conurbado)
    if not albergue:
        albergue = (
            "829e0565-15f6-444f-8d8e-d00d22aea44e",
            "Escuela Primaria Nuevo Santander",
            22.363848,
            -97.904238,
        )

    return {
        "id": str(albergue[0]),
        "name": albergue[1],
        "latitude": float(albergue[2]),
        "longitude": float(albergue[3]),
    }




@router.get("/segura", response_model=RespuestaRuta)
@router.get("/segura/", response_model=RespuestaRuta)
@router.get("/segura'", response_model=RespuestaRuta)
@router.get("", response_model=RespuestaRuta)
@router.get("/", response_model=RespuestaRuta)
async def calcular_ruta_segura_get(
    siteId: str = Query(default="", alias="site_id"),
    latitude: float = Query(default=22.2170, alias="latitud"),
    longitude: float = Query(default=-97.8728, alias="longitud"),
) -> RespuestaRuta:
    """
    Permite invocar la ruta tanto por GET (query parameters) como por POST (body JSON).
    """
    solicitud = SolicitudRuta(siteId=siteId, latitude=latitude, longitude=longitude)
    return await calcular_ruta_segura(solicitud)


@router.post("/segura", response_model=RespuestaRuta)
@router.post("/segura/", response_model=RespuestaRuta)
@router.post("/segura'", response_model=RespuestaRuta)
@router.post("", response_model=RespuestaRuta)
@router.post("/", response_model=RespuestaRuta)
async def calcular_ruta_segura(solicitud: SolicitudRuta) -> RespuestaRuta:
    """
    METODO: POST

    Calcula la ruta vehicular mas cercana y segura hacia el centro de apoyo o albergue especificado.

    Request Body:
      {
        "siteId": "string",
        "latitude": 22.2170,
        "longitude": -97.8728
      }

    Response Body:
      {
        "routeId": "ruta_123456",
        "origin": { "latitude": 22.2170, "longitude": -97.8728 },
        "destination": { "id": "...", "name": "...", "latitude": 22.2585, "longitude": -97.8384 },
        "distanceMeters": 8505.6,
        "durationSeconds": 1318.2,
        "geometry": [[-97.8728, 22.2170], ...],
        "segments": [...]
      }
    """
    # 1. Obtener coordenadas de incidencias y bloqueos activos para su evasion
    puntos_exclusion = obtener_puntos_incidencia_activos()

    # 2. Resolver el albergue destino oficial mas cercano a la ubicacion del dispositivo
    destino = buscar_albergue_destino(
        site_id=solicitud.siteId,
        lat_origen=solicitud.latitude,
        lon_origen=solicitud.longitude,
    )

    # 3. Calcular la ruta usando la API de Mapbox Directions con evasion activa
    try:
        resultado_mapbox = await obtener_ruta_mapbox(
            origen_lon=solicitud.longitude,
            origen_lat=solicitud.latitude,
            destino_lon=destino["longitude"],
            destino_lat=destino["latitude"],
            puntos_exclusion=puntos_exclusion,
        )
    except ErrorCalculoRuta as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 3. Estructurar la respuesta
    id_ruta = f"ruta_{uuid.uuid4().hex[:12]}"

    return RespuestaRuta(
        routeId=id_ruta,
        origin=CoordenadasPunto(
            latitude=solicitud.latitude, longitude=solicitud.longitude
        ),
        destination=DestinoInfo(
            id=solicitud.siteId if solicitud.siteId else destino["id"],
            name=destino["name"],
            latitude=destino["latitude"],
            longitude=destino["longitude"],
        ),
        distanceMeters=resultado_mapbox["distanceMeters"],
        durationSeconds=resultado_mapbox["durationSeconds"],
        geometry=resultado_mapbox["geometry"],
        segments=[
            SegmentoRuta(
                distanceMeters=seg["distanceMeters"],
                durationSeconds=seg["durationSeconds"],
                instruction=seg["instruction"],
            )
            for seg in resultado_mapbox["segments"]
        ],
    )
