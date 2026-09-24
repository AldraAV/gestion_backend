"""
Proveedor de datos sismicos via USGS Earthquake API.

Fuente: https://earthquake.usgs.gov/fdsnws/event/1/
Formato: GeoJSON nativo.
Auth: Ninguna (servicio publico gratuito).
Frecuencia recomendada: cada 1-5 minutos.
"""

from datetime import UTC, datetime, timedelta

import httpx

from app.adaptadores.proveedores.base import IncidenciaGeo
from app.adaptadores.proveedores.sismos.interfaz import ProveedorSismos


class ProveedorSismosUSGS(ProveedorSismos):
    """Implementacion del proveedor de sismos usando USGS Earthquake API."""

    def __init__(
        self,
        url_base: str = "https://earthquake.usgs.gov/fdsnws/event/1/query",
        magnitud_minima: float = 3.0,
        limite: int = 50,
    ) -> None:
        self._url_base = url_base
        self._magnitud_minima = magnitud_minima
        self._limite = limite

    @property
    def nombre_fuente(self) -> str:
        return "usgs"

    async def obtener_incidencias(
        self, bbox: tuple[float, float, float, float] | None = None
    ) -> list[IncidenciaGeo]:
        """Consulta la API de USGS y retorna sismos normalizados.

        Args:
            bbox: (lonMin, latMin, lonMax, latMax) para filtrar por zona.

        Returns:
            Lista de IncidenciaGeo con sismos recientes. Lista vacia si falla.
        """
        parametros: dict = {
            "format": "geojson",
            "minmagnitude": self._magnitud_minima,
            "orderby": "time",
            "limit": self._limite,
            "starttime": (datetime.now(UTC) - timedelta(hours=24)).strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
        }

        if bbox:
            lon_min, lat_min, lon_max, lat_max = bbox
            parametros["minlongitude"] = lon_min
            parametros["minlatitude"] = lat_min
            parametros["maxlongitude"] = lon_max
            parametros["maxlatitude"] = lat_max

        try:
            async with httpx.AsyncClient(timeout=15.0) as cliente:
                respuesta = await cliente.get(self._url_base, params=parametros)
                respuesta.raise_for_status()
                datos = respuesta.json()
        except (httpx.HTTPError, Exception):
            return []

        return self._normalizar(datos)

    def _normalizar(self, datos_geojson: dict) -> list[IncidenciaGeo]:
        """Convierte el GeoJSON de USGS a lista de IncidenciaGeo."""
        incidencias: list[IncidenciaGeo] = []

        for feature in datos_geojson.get("features", []):
            propiedades = feature.get("properties", {})
            geometria = feature.get("geometry", {})
            coordenadas = geometria.get("coordinates", [0, 0, 0])

            magnitud = propiedades.get("mag", 0) or 0
            nivel = self._calcular_nivel_alerta(magnitud)

            # Timestamp de USGS viene en milisegundos epoch
            timestamp_ms = propiedades.get("time", 0)
            fecha = datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC).isoformat()

            incidencias.append(
                IncidenciaGeo(
                    tipo="sismo",
                    fuente="usgs",
                    titulo=propiedades.get("title", f"Sismo M{magnitud}"),
                    descripcion=propiedades.get("place", "Ubicacion desconocida"),
                    latitud=coordenadas[1],
                    longitud=coordenadas[0],
                    magnitud=magnitud,
                    nivel_alerta=nivel,
                    fecha_evento=fecha,
                    datos_extra={
                        "profundidad_km": coordenadas[2]
                        if len(coordenadas) > 2
                        else None,
                        "tsunami": propiedades.get("tsunami", 0),
                        "sentido": propiedades.get("felt"),
                        "url_detalle": propiedades.get("url"),
                    },
                )
            )

        return incidencias

    @staticmethod
    def _calcular_nivel_alerta(magnitud: float) -> str:
        """Calcula el nivel de alerta segun la magnitud del sismo."""
        if magnitud >= 7.0:
            return "roja"
        if magnitud >= 5.0:
            return "naranja"
        if magnitud >= 4.0:
            return "amarillo"
        return "verde"
