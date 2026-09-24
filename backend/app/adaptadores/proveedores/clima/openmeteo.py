"""
Proveedor de datos climaticos via Open-Meteo API (fallback de desarrollo).

Fuente: https://api.open-meteo.com/v1/forecast
Formato: JSON.
Auth: Ninguna (servicio publico gratuito).
Uso: Solo para desarrollo. En produccion usar CONAGUA.
"""

import httpx

from app.adaptadores.proveedores.base import IncidenciaGeo
from app.adaptadores.proveedores.clima.interfaz import ProveedorClima


class ProveedorClimaOpenMeteo(ProveedorClima):
    """Implementacion del proveedor de clima usando Open-Meteo (fallback dev)."""

    def __init__(
        self,
        url_base: str = "https://api.open-meteo.com/v1",
    ) -> None:
        self._url_base = url_base

    @property
    def nombre_fuente(self) -> str:
        return "openmeteo"

    async def obtener_incidencias(
        self, bbox: tuple[float, float, float, float] | None = None
    ) -> list[IncidenciaGeo]:
        """Consulta Open-Meteo y genera alertas solo si hay condiciones extremas.

        Args:
            bbox: (lonMin, latMin, lonMax, latMax). Se usa el centro del bbox.

        Returns:
            Lista de IncidenciaGeo solo si hay condiciones meteorologicas
            extremas (lluvias >50mm/h, vientos >80km/h). Lista vacia si normal.
        """
        # Calcular centro del bbox o usar default (Veracruz centro-norte)
        if bbox:
            lon_centro = (bbox[0] + bbox[2]) / 2
            lat_centro = (bbox[1] + bbox[3]) / 2
        else:
            lat_centro = 20.5
            lon_centro = -97.5

        parametros = {
            "latitude": lat_centro,
            "longitude": lon_centro,
            "hourly": "temperature_2m,precipitation,windspeed_10m",
            "forecast_days": 1,
            "timezone": "America/Mexico_City",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as cliente:
                respuesta = await cliente.get(
                    f"{self._url_base}/forecast", params=parametros
                )
                respuesta.raise_for_status()
                datos = respuesta.json()
        except (httpx.HTTPError, Exception):
            return []

        return self._analizar_condiciones_extremas(datos, lat_centro, lon_centro)

    def _analizar_condiciones_extremas(
        self, datos: dict, latitud: float, longitud: float
    ) -> list[IncidenciaGeo]:
        """Analiza datos meteorologicos y genera alertas por condiciones extremas."""
        incidencias: list[IncidenciaGeo] = []
        horario = datos.get("hourly", {})

        precipitaciones = horario.get("precipitation", [])
        vientos = horario.get("windspeed_10m", [])
        tiempos = horario.get("time", [])

        for i, tiempo in enumerate(tiempos):
            precip = precipitaciones[i] if i < len(precipitaciones) else 0
            viento = vientos[i] if i < len(vientos) else 0

            # Alerta por precipitacion extrema
            if precip and precip > 50:
                nivel = "roja" if precip > 100 else "naranja"
                incidencias.append(
                    IncidenciaGeo(
                        tipo="inundacion",
                        fuente="openmeteo",
                        titulo=f"Lluvia intensa: {precip:.1f} mm/h",
                        descripcion=(
                            f"Precipitacion de {precip:.1f} mm/h detectada. "
                            f"Riesgo de inundacion en la zona."
                        ),
                        latitud=latitud,
                        longitud=longitud,
                        nivel_alerta=nivel,
                        fecha_evento=f"{tiempo}:00",
                        datos_extra={"precipitacion_mm": precip, "hora": tiempo},
                    )
                )

            # Alerta por viento extremo
            if viento and viento > 80:
                nivel = "roja" if viento > 120 else "naranja"
                incidencias.append(
                    IncidenciaGeo(
                        tipo="ciclon",
                        fuente="openmeteo",
                        titulo=f"Viento extremo: {viento:.1f} km/h",
                        descripcion=(
                            f"Rafagas de {viento:.1f} km/h detectadas. "
                            f"Posible actividad ciclonica."
                        ),
                        latitud=latitud,
                        longitud=longitud,
                        nivel_alerta=nivel,
                        fecha_evento=f"{tiempo}:00",
                        datos_extra={"viento_kmh": viento, "hora": tiempo},
                    )
                )

        return incidencias
