"""
Proveedor de datos de anomalias termicas e incendios via NASA FIRMS.

Fuente: NASA FIRMS (Fire Information for Resource Management System)
Formato: CSV de anomalias termicas satelitales (VIIRS / MODIS).
Auth: Requiere FIRMS_API_KEY (gratuita con registro previo).
Frecuencia: cada 3 a 6 horas.
"""

import csv
import io
from datetime import UTC, datetime

import httpx

from app.adaptadores.proveedores.base import IncidenciaGeo
from app.adaptadores.proveedores.incendios.interfaz import ProveedorIncendios


class ProveedorIncendiosFIRMS(ProveedorIncendios):
    """Implementacion del proveedor de incendios usando NASA FIRMS."""

    def __init__(
        self,
        api_key: str = "",
        url_base: str = "https://firms.modaps.eosdis.nasa.gov/api",
    ) -> None:
        self._api_key = api_key
        self._url_base = url_base

    @property
    def nombre_fuente(self) -> str:
        return "firms"

    async def obtener_incidencias(
        self, bbox: tuple[float, float, float, float] | None = None
    ) -> list[IncidenciaGeo]:
        """Consulta anomalias termicas de satelite para Mexico.

        Args:
            bbox: (lonMin, latMin, lonMax, latMax) para filtrado espacial.

        Returns:
            Lista de IncidenciaGeo de tipo 'incendio'. Vacio si no hay key
            o falla la peticion.
        """
        if not self._api_key:
            return []

        # Endpoint CSV para Mexico en tiempo cuasi-real (1 dia)
        url = f"{self._url_base}/country/csv/{self._api_key}/VIIRS_SNPP_NRT/MEX/1"

        try:
            async with httpx.AsyncClient(timeout=20.0) as cliente:
                respuesta = await cliente.get(url)
                respuesta.raise_for_status()
                texto_csv = respuesta.text
        except (httpx.HTTPError, Exception):
            return []

        return self._normalizar_csv(texto_csv, bbox)

    def _normalizar_csv(
        self, texto_csv: str, bbox: tuple[float, float, float, float] | None
    ) -> list[IncidenciaGeo]:
        """Parsea las lineas CSV de FIRMS y genera IncidenciaGeo."""
        incidencias: list[IncidenciaGeo] = []
        lector = csv.DictReader(io.StringIO(texto_csv))

        for fila in lector:
            try:
                lat = float(fila.get("latitude", 0))
                lon = float(fila.get("longitude", 0))
            except (ValueError, TypeError):
                continue

            # Filtrar por bounding box si se solicita
            if bbox:
                lon_min, lat_min, lon_max, lat_max = bbox
                if not (lon_min <= lon <= lon_max and lat_min <= lat <= lat_max):
                    continue

            confianza = str(fila.get("confidence", "")).lower()
            if confianza not in ("nominal", "high", "h", "n"):
                continue

            try:
                frp = float(fila.get("frp", 0.0) or 0.0)
            except ValueError:
                frp = 0.0

            nivel = self._calcular_nivel_alerta(frp)
            fecha_acq = fila.get("acq_date", datetime.now(UTC).strftime("%Y-%m-%d"))
            hora_acq = fila.get("acq_time", "0000")
            hora_formateada = (
                f"{hora_acq[:2]}:{hora_acq[2:]}:00"
                if len(hora_acq) == 4
                else "00:00:00"
            )

            incidencias.append(
                IncidenciaGeo(
                    tipo="incendio",
                    fuente="firms",
                    titulo=f"Foco termico activo (FRP: {frp:.1f} MW)",
                    descripcion=(
                        f"Anomalia termica detectada por satelite VIIRS. "
                        f"Potencia radiativa: {frp:.1f} MW. Confianza: {confianza}."
                    ),
                    latitud=lat,
                    longitud=lon,
                    nivel_alerta=nivel,
                    fecha_evento=f"{fecha_acq}T{hora_formateada}Z",
                    datos_extra={
                        "potencia_frp": frp,
                        "brillo_kelvin": fila.get("bright_ti4"),
                        "satelite": fila.get("satellite", "SNPP"),
                        "dia_noche": fila.get("daynight"),
                    },
                )
            )

        return incidencias

    @staticmethod
    def _calcular_nivel_alerta(frp: float) -> str:
        """Determina la criticidad del incendio segun potencia de fuego (FRP)."""
        if frp >= 100.0:
            return "roja"
        if frp >= 50.0:
            return "naranja"
        if frp >= 20.0:
            return "amarillo"
        return "verde"
