"""
Clases base para el sistema de proveedores de datos de desastres.

Define la interfaz abstracta y el DTO comun que todos los proveedores
deben implementar. Los datos son efimeros: NUNCA se persisten en BD.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class IncidenciaGeo(BaseModel):
    """DTO efimero que representa un evento de desastre para el mapa.

    NO es una tabla de base de datos. Los datos viven en memoria
    y mueren con el proceso o al expirar el cache.
    """

    tipo: str
    fuente: str
    titulo: str
    descripcion: str
    latitud: float
    longitud: float
    magnitud: float | None = None
    nivel_alerta: str | None = None
    fecha_evento: str
    datos_extra: dict | None = None


class ProveedorExterno(ABC):
    """Interfaz abstracta para proveedores de datos de desastres.

    Cada proveedor concreto debe implementar:
    - obtener_incidencias: consulta la API externa y normaliza a IncidenciaGeo
    - nombre_fuente: identificador unico del proveedor
    """

    @abstractmethod
    async def obtener_incidencias(
        self, bbox: tuple[float, float, float, float] | None = None
    ) -> list[IncidenciaGeo]:
        """Consulta la API externa y retorna incidencias normalizadas.

        Args:
            bbox: Bounding box opcional (lonMin, latMin, lonMax, latMax).

        Returns:
            Lista de incidencias normalizadas. Lista vacia si no hay datos
            o si el proveedor falla (resiliencia).
        """
        ...

    @property
    @abstractmethod
    def nombre_fuente(self) -> str:
        """Identificador unico del proveedor (ej: 'usgs', 'openmeteo')."""
        ...
