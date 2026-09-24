import os
from typing import Any

import httpx

from app.core.config import settings

MAPBOX_DIRECTIONS_API = "https://api.mapbox.com/directions/v5/mapbox/driving"


class ErrorCalculoRuta(Exception):
    """Excepcion lanzada cuando MapBox o el calculo de ruta falla."""

    pass


def obtener_token_mapbox() -> str:
    return settings.MAPBOX_ACCESS_TOKEN or os.getenv("MAPBOX_ACCESS_TOKEN", "")


async def obtener_ruta_mapbox(
    origen_lon: float,
    origen_lat: float,
    destino_lon: float,
    destino_lat: float,
    puntos_exclusion: list[tuple[float, float]] | None = None,
) -> dict[str, Any]:
    """
    Consulta la API oficial de Mapbox Directions y extrae la geometria y segmentos detallados.
    Soporta la evasion activa de incidencias mediante el parametro exclude de Mapbox.
    """
    token = obtener_token_mapbox()
    coordenadas = f"{origen_lon},{origen_lat};{destino_lon},{destino_lat}"
    parametros: dict[str, Any] = {
        "geometries": "geojson",
        "steps": "true",
        "overview": "full",
        "language": "es",
        "access_token": token,
    }

    if puntos_exclusion:
        # Formato Mapbox v5: point(lon lat),point(lon lat)
        puntos_validos = [
            f"point({lon:.5f} {lat:.5f})"
            for lon, lat in puntos_exclusion[:10]
            if abs(lon) <= 180 and abs(lat) <= 90
        ]
        if puntos_validos:
            parametros["exclude"] = ",".join(puntos_validos)

    url = f"{MAPBOX_DIRECTIONS_API}/{coordenadas}"

    async with httpx.AsyncClient(timeout=15.0) as cliente:
        try:
            respuesta = await cliente.get(url, params=parametros)
            # Salvaguarda: Si con exclusion estricta Mapbox no halla paso, reintentar sin exclusion
            if respuesta.status_code != 200 and "exclude" in parametros:
                parametros_rescate = dict(parametros)
                del parametros_rescate["exclude"]
                respuesta = await cliente.get(url, params=parametros_rescate)
        except Exception as error_red:
            raise ErrorCalculoRuta(f"Error de conexion con Mapbox: {str(error_red)}")

    if respuesta.status_code != 200:
        raise ErrorCalculoRuta(
            f"Mapbox respondio con codigo {respuesta.status_code}: {respuesta.text}"
        )

    datos = respuesta.json()
    rutas = datos.get("routes", [])
    if not rutas:
        raise ErrorCalculoRuta(
            "Mapbox no encontro ninguna ruta valida entre los puntos especificados."
        )

    ruta_principal = rutas[0]
    geometria_coordenadas = ruta_principal.get("geometry", {}).get("coordinates", [])
    distancia = ruta_principal.get("distance", 0.0)
    duracion = ruta_principal.get("duration", 0.0)

    # Extraer segmentos paso a paso (steps)
    segmentos = []
    legs = ruta_principal.get("legs", [])
    for leg in legs:
        for step in leg.get("steps", []):
            instruccion = step.get("maneuver", {}).get("instruction", "")
            segmentos.append(
                {
                    "distanceMeters": step.get("distance", 0.0),
                    "durationSeconds": step.get("duration", 0.0),
                    "instruction": instruccion,
                }
            )

    return {
        "distanceMeters": distancia,
        "durationSeconds": duracion,
        "geometry": geometria_coordenadas,
        "segments": segmentos,
    }
