"""
Proveedor de datos climaticos via CONAGUA/SMN (produccion).

STUB: El endpoint real de CONAGUA aun no esta disponible para
consumo programatico completo. Esta clase se completara cuando
el equipo obtenga acceso al web service de smn.conagua.gob.mx.
"""

from app.adaptadores.proveedores.base import IncidenciaGeo
from app.adaptadores.proveedores.clima.interfaz import ProveedorClima


class ProveedorClimaConagua(ProveedorClima):
    """Stub del proveedor CONAGUA/SMN para produccion.

    Cumple con el Reglamento Art. 22-III como fuente oficial del
    Estado mexicano. La implementacion se completara con acceso
    al web service real.
    """

    def __init__(self, url_base: str = "") -> None:
        self._url_base = url_base

    @property
    def nombre_fuente(self) -> str:
        return "conagua"

    async def obtener_incidencias(
        self, bbox: tuple[float, float, float, float] | None = None
    ) -> list[IncidenciaGeo]:
        """Stub: retorna lista vacia hasta que se integre CONAGUA real."""
        return []
