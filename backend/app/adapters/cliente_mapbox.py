import os
from typing import Any

import httpx

MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN", "")
MAPBOX_DIRECTIONS_API = "https://api.mapbox.com/directions/v5/mapbox/driving"


class ErrorCalculoRuta(Exception):
    """Excepcion lanzada cuando MapBox o el calculo de ruta falla."""

    pass


async def obtener_ruta_mapbox(
    origen_lon: float, origen_lat: float, destino_lon: float, destino_lat: float
) -> dict[str, Any]:
    """
    Consulta la API oficial de Mapbox Directions y extrae la geometria y segmentos detallados.
    """
    coordenadas = f"{origen_lon},{origen_lat};{destino_lon},{destino_lat}"
    parametros = {
        "geometries": "geojson",
        "steps": "true",
        "overview": "full",
        "language": "es",
        "access_token": MAPBOX_ACCESS_TOKEN,
    }
    url = f"{MAPBOX_DIRECTIONS_API}/{coordenadas}"

    async with httpx.AsyncClient(timeout=15.0) as cliente:
        try:
            respuesta = await cliente.get(url, params=parametros)
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
