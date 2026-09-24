"""
Orquestador central de proveedores de desastres naturales en tiempo real.

Agrega fuentes heterogeneas (USGS, Clima, FIRMS, GDACS), orquesta consultas
asincronas, gestiona cache en memoria con TTL individual y genera GeoJSON
FeatureCollection listo para MapLibre o Mapbox.

REGLA SUPREMA: NUNCA PERSISTE DATOS EXTERNOS EN BASE DE DATOS.
"""

from typing import Any

from app.adaptadores.proveedores.base import IncidenciaGeo, ProveedorExterno
from app.adaptadores.proveedores.cache_memoria import CacheEnMemoria
from app.core.config import settings


class AgregadorIncidencias:
    """Orquestador y despachador de eventos meteorologicos y sismicos."""

    def __init__(
        self,
        proveedores: list[ProveedorExterno],
        cache: CacheEnMemoria,
        ttls_por_fuente: dict[str, int] | None = None,
    ) -> None:
        self._proveedores = proveedores
        self._cache = cache
        self._ttls = ttls_por_fuente or {
            "usgs": settings.CACHE_TTL_SISMOS,
            "openmeteo": settings.CACHE_TTL_CLIMA,
            "conagua": settings.CACHE_TTL_CLIMA,
            "firms": settings.CACHE_TTL_INCENDIOS,
            "gdacs": settings.CACHE_TTL_GLOBAL,
        }

    async def obtener_todas(
        self, bbox: tuple[float, float, float, float] | None = None
    ) -> dict[str, Any]:
        """Recopila incidencias de todos los proveedores activos aplicando cache.

        Args:
            bbox: (lonMin, latMin, lonMax, latMax) opcional.

        Returns:
            GeoJSON FeatureCollection serializable con metadata de control.
        """
        todas_las_incidencias: list[IncidenciaGeo] = []
        fuentes_consultadas: list[str] = []
        hubo_cache_miss = False

        for proveedor in self._proveedores:
            nombre = proveedor.nombre_fuente
            fuentes_consultadas.append(nombre)

            # Clave de cache considerando bbox si existe
            clave_cache = f"{nombre}_{bbox}" if bbox else nombre
            datos_cacheados = self._cache.obtener(clave_cache)

            if datos_cacheados is not None:
                todas_las_incidencias.extend(datos_cacheados)
            else:
                hubo_cache_miss = True
                try:
                    incidencias_frescas = await proveedor.obtener_incidencias(bbox=bbox)
                    ttl = self._ttls.get(nombre, 300)
                    self._cache.almacenar(
                        clave_cache, incidencias_frescas, ttl_segundos=ttl
                    )
                    todas_las_incidencias.extend(incidencias_frescas)
                except Exception:
                    continue

        features = [self._convertir_a_feature(inc) for inc in todas_las_incidencias]

        return {
            "type": "FeatureCollection",
            "total": len(features),
            "fuentes_consultadas": fuentes_consultadas,
            "cache_vigente": not hubo_cache_miss,
            "features": features,
        }

    @staticmethod
    def _convertir_a_feature(inc: IncidenciaGeo) -> dict[str, Any]:
        """Convierte una IncidenciaGeo a una Feature de GeoJSON estandar."""
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [inc.longitud, inc.latitud],
            },
            "properties": {
                "tipo": inc.tipo,
                "fuente": inc.fuente,
                "titulo": inc.titulo,
                "descripcion": inc.descripcion,
                "magnitud": inc.magnitud,
                "nivel_alerta": inc.nivel_alerta,
                "fecha_evento": inc.fecha_evento,
                "datos_extra": inc.datos_extra,
            },
        }


def crear_agregador_default() -> AgregadorIncidencias:
    """Factoria del agregador configurado con las variables activas del sistema."""
    from app.adaptadores.proveedores.clima.conagua import ProveedorClimaConagua
    from app.adaptadores.proveedores.clima.openmeteo import ProveedorClimaOpenMeteo
    from app.adaptadores.proveedores.global_desastres.gdacs import (
        ProveedorDesastresGDACS,
    )
    from app.adaptadores.proveedores.incendios.firms import ProveedorIncendiosFIRMS
    from app.adaptadores.proveedores.sismos.usgs import ProveedorSismosUSGS

    proveedores: list[ProveedorExterno] = []

    # 1. Sismos (USGS)
    proveedores.append(ProveedorSismosUSGS(url_base=settings.USGS_EARTHQUAKE_BASE_URL))

    # 2. Clima (Conagua o OpenMeteo)
    if settings.CLIMA_PROVIDER.lower() == "conagua":
        proveedores.append(
            ProveedorClimaConagua(url_base=settings.CONAGUA_SMN_BASE_URL)
        )
    else:
        proveedores.append(
            ProveedorClimaOpenMeteo(url_base=settings.OPEN_METEO_BASE_URL)
        )

    # 3. Incendios (NASA FIRMS)
    proveedores.append(
        ProveedorIncendiosFIRMS(
            api_key=settings.FIRMS_API_KEY,
            url_base=settings.FIRMS_BASE_URL,
        )
    )

    # 4. Multirriesgo global (GDACS)
    proveedores.append(ProveedorDesastresGDACS(url_feed=settings.GDACS_FEED_URL))

    cache = CacheEnMemoria()

    return AgregadorIncidencias(
        proveedores=proveedores,
        cache=cache,
        ttls_por_fuente={
            "usgs": settings.CACHE_TTL_SISMOS,
            "openmeteo": settings.CACHE_TTL_CLIMA,
            "conagua": settings.CACHE_TTL_CLIMA,
            "firms": settings.CACHE_TTL_INCENDIOS,
            "gdacs": settings.CACHE_TTL_GLOBAL,
        },
    )
