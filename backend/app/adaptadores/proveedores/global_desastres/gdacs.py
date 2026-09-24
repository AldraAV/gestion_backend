"""
Proveedor de alertas globales multirriesgo via GDACS (Global Disaster Alert and Coordination System).

Fuente: GDACS RSS Feed (Naciones Unidas / Comision Europea)
Formato: RSS XML con etiquetas GeoRSS.
Auth: Ninguna (servicio publico internacional).
Frecuencia recomendada: cada 6 horas (servicio de cruce y respaldo).
"""

from datetime import UTC, datetime

import feedparser
import httpx

from app.adaptadores.proveedores.base import IncidenciaGeo
from app.adaptadores.proveedores.global_desastres.interfaz import (
    ProveedorDesastresGlobal,
)


class ProveedorDesastresGDACS(ProveedorDesastresGlobal):
    """Implementacion de consulta y normalizacion de feed GDACS."""

    def __init__(
        self,
        url_feed: str = "https://www.gdacs.org/xml/rss.xml",
    ) -> None:
        self._url_feed = url_feed

    @property
    def nombre_fuente(self) -> str:
        return "gdacs"

    async def obtener_incidencias(
        self, bbox: tuple[float, float, float, float] | None = None
    ) -> list[IncidenciaGeo]:
        """Consulta el feed RSS de GDACS y extrae incidentes relevantes para Mexico.

        Args:
            bbox: (lonMin, latMin, lonMax, latMax) para filtrado espacial.

        Returns:
            Lista de IncidenciaGeo extraidas de GDACS.
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as cliente:
                respuesta = await cliente.get(self._url_feed)
                respuesta.raise_for_status()
                contenido_xml = respuesta.text
        except (httpx.HTTPError, Exception):
            return []

        return self._normalizar_feed(contenido_xml, bbox)

    def _normalizar_feed(
        self, contenido_xml: str, bbox: tuple[float, float, float, float] | None
    ) -> list[IncidenciaGeo]:
        """Parsea las entradas del feed RSS utilizando feedparser."""
        incidencias: list[IncidenciaGeo] = []
        feed = feedparser.parse(contenido_xml)

        for entrada in feed.entries:
            titulo = entrada.get("title", "")
            resumen = entrada.get("summary", "")
            texto_completo = f"{titulo} {resumen}".lower()

            # Extraer coordenadas geograficas desde georss_point
            punto_geo = entrada.get("georss_point", "")
            lat = 0.0
            lon = 0.0
            if punto_geo:
                partes = punto_geo.strip().split()
                if len(partes) >= 2:
                    try:
                        lat = float(partes[0])
                        lon = float(partes[1])
                    except ValueError:
                        lat, lon = 0.0, 0.0

            # Filtrar si corresponde a Mexico o esta dentro del bbox
            coincide_mexico = "mexico" in texto_completo or "mex" in texto_completo
            coincide_bbox = False

            if bbox and (lat != 0.0 or lon != 0.0):
                lon_min, lat_min, lon_max, lat_max = bbox
                if lon_min <= lon <= lon_max and lat_min <= lat <= lat_max:
                    coincide_bbox = True

            if not (coincide_mexico or coincide_bbox):
                continue

            tipo_evento = self._mapear_tipo_evento(entrada.get("gdacs_eventtype", ""))
            nivel = self._mapear_nivel_alerta(entrada.get("gdacs_alertlevel", ""))
            fecha = entrada.get("published", datetime.now(UTC).isoformat())

            incidencias.append(
                IncidenciaGeo(
                    tipo=tipo_evento,
                    fuente="gdacs",
                    titulo=titulo or f"Incidencia Global {tipo_evento}",
                    descripcion=resumen or "Alerta detectada en sistema GDACS",
                    latitud=lat,
                    longitud=lon,
                    nivel_alerta=nivel,
                    fecha_evento=fecha,
                    datos_extra={
                        "pais": entrada.get("gdacs_country"),
                        "severidad": entrada.get("gdacs_severity"),
                        "enlace": entrada.get("link"),
                    },
                )
            )

        return incidencias

    @staticmethod
    def _mapear_tipo_evento(tipo_gdacs: str) -> str:
        """Traduce los codigos de evento GDACS a la nomenclatura del Aldraverso."""
        tipo_limpio = (tipo_gdacs or "").upper()
        mapa = {
            "EQ": "sismo",
            "TC": "ciclon",
            "FL": "inundacion",
            "WF": "incendio",
            "VO": "volcan",
            "DR": "sequia",
        }
        return mapa.get(tipo_limpio, "otro")

    @staticmethod
    def _mapear_nivel_alerta(nivel_gdacs: str) -> str:
        """Convierte los niveles de alerta de GDACS (Red, Orange, Green)."""
        nivel = (nivel_gdacs or "").lower()
        if "red" in nivel:
            return "roja"
        if "orange" in nivel:
            return "naranja"
        if "yellow" in nivel:
            return "amarillo"
        return "verde"
