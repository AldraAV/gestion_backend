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


def buscar_albergue_destino(site_id: str) -> dict[str, Any]:
    """
    Busca el centro de apoyo o albergue en la base de datos Supabase PostgreSQL.
    Si no se encuentra un match exacto por UUID, folio o nombre, usa como salvaguarda
    el centro de apoyo 'Espana 1101' (lat: 22.2585, lon: -97.8384).
    """
    db_url = str(settings.DATABASE_URL).replace("+psycopg", "")
    albergue = None

    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                # 1. Intentar por UUID si el site_id tiene formato UUID
                try:
                    uuid_val = uuid.UUID(site_id)
                    cur.execute(
                        "SELECT id, nombre, latitud, longitud FROM albergue WHERE id = %s",
                        (uuid_val,),
                    )
                    albergue = cur.fetchone()
                except (ValueError, AttributeError):
                    pass

                # 2. Intentar por folio_identificador o nombre
                if not albergue and site_id:
                    cur.execute(
                        """
                        SELECT id, nombre, latitud, longitud
                        FROM albergue
                        WHERE folio_identificador = %s OR nombre ILIKE %s
                        LIMIT 1
                        """,
                        (site_id, f"%{site_id}%"),
                    )
                    albergue = cur.fetchone()

                # 3. Si no encontro o site_id es vacio, buscar el centro de Espana 1101 (22.2585, -97.8384)
                if not albergue:
                    cur.execute(
                        """
                        SELECT id, nombre, latitud, longitud
                        FROM albergue
                        WHERE latitud IS NOT NULL AND longitud IS NOT NULL
                        ORDER BY (abs(latitud - 22.2585) + abs(longitud - (-97.8384))) ASC
                        LIMIT 1
                        """
                    )
                    albergue = cur.fetchone()
    except Exception:
        # Si la conexion a la BD fallara temporalmente, proveemos el albergue Espana 1101 en memoria
        albergue = (
            "8d6db559-93ea-4184-8c67-30d376b511e0",
            "España 1101 (Centro de Apoyo)",
            22.2585,
            -97.8384,
        )

    if not albergue:
        return {
            "id": "8d6db559-93ea-4184-8c67-30d376b511e0",
            "name": "España 1101 (Centro de Apoyo)",
            "latitude": 22.2585,
            "longitude": -97.8384,
        }

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
    # 1. Resolver el destino (Centro de Apoyo en base de datos)
    destino = buscar_albergue_destino(solicitud.siteId)

    # 2. Calcular la ruta usando la API de Mapbox Directions
    try:
        resultado_mapbox = await obtener_ruta_mapbox(
            origen_lon=solicitud.longitude,
            origen_lat=solicitud.latitude,
            destino_lon=destino["longitude"],
            destino_lat=destino["latitude"],
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
