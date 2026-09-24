"""
Endpoint publico para consulta de incidencias de desastres en tiempo real.

GET /api/v1/publico/mapa/incidencias
- Consulta 4 proveedores externos (USGS, Clima, FIRMS, GDACS)
- Devuelve GeoJSON normalizado para MapLibre/Mapbox
- Cache en memoria con TTL configurable por proveedor
- CERO persistencia: los datos son efimeros
"""

from fastapi import APIRouter, Query

router = APIRouter(prefix="/publico/mapa", tags=["Mapa Incidencias"])

# Instancia global del agregador (lazy init)
_agregador = None


def _obtener_agregador():
    """Inicializa el agregador de incidencias de forma perezosa."""
    global _agregador
    if _agregador is None:
        from app.adaptadores.proveedores.agregador import crear_agregador_default

        _agregador = crear_agregador_default()
    return _agregador


@router.get("/incidencias")
@router.get("/incidencias/")
async def obtener_incidencias_mapa(
    tipos: str | None = Query(
        default=None,
        description="Tipos de incidencia separados por coma: sismo,inundacion,incendio,ciclon,otro",
    ),
    mag_min: float | None = Query(
        default=None,
        description="Magnitud minima para filtrar sismos",
    ),
    bbox: str | None = Query(
        default=None,
        description="Bounding box: lonMin,latMin,lonMax,latMax",
    ),
) -> dict:
    """
    Consulta incidencias de desastres en tiempo real desde multiples fuentes.

    Devuelve un GeoJSON FeatureCollection normalizado para consumo
    directo por MapLibre GL JS o Mapbox GL JS.

    Los datos NO se persisten en base de datos. Son efimeros con cache TTL.

    Args:
        tipos: Filtro opcional por tipo de incidencia (separados por coma).
        mag_min: Magnitud minima para filtrar sismos.
        bbox: Bounding box en formato lonMin,latMin,lonMax,latMax.

    Returns:
        dict con estructura GeoJSON FeatureCollection.
    """
    agregador = _obtener_agregador()

    # Parsear bbox si viene
    bbox_tupla = None
    if bbox:
        try:
            partes = [float(p.strip()) for p in bbox.split(",")]
            if len(partes) == 4:
                bbox_tupla = (partes[0], partes[1], partes[2], partes[3])
        except (ValueError, IndexError):
            pass  # Si el bbox es invalido, ignorar y consultar sin filtro

    # Obtener todas las incidencias del agregador
    resultado = await agregador.obtener_todas(bbox=bbox_tupla)

    # Filtrar por tipos si se especifican
    if tipos:
        tipos_permitidos = {t.strip().lower() for t in tipos.split(",")}
        resultado["features"] = [
            f
            for f in resultado["features"]
            if f.get("properties", {}).get("tipo", "") in tipos_permitidos
        ]
        resultado["total"] = len(resultado["features"])

    # Filtrar por magnitud minima si se especifica
    if mag_min is not None:
        resultado["features"] = [
            f
            for f in resultado["features"]
            if (
                f.get("properties", {}).get("tipo") != "sismo"
                or (f.get("properties", {}).get("magnitud") or 0) >= mag_min
            )
        ]
        resultado["total"] = len(resultado["features"])

    return resultado
