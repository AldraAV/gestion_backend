"""
Cache en memoria con TTL configurable para datos efimeros de proveedores.

Los datos de APIs externas viven aqui temporalmente y expiran
automaticamente. Thread-safe mediante threading.Lock.
"""

import threading
import time

from app.adaptadores.proveedores.base import IncidenciaGeo


class _EntradaCache:
    """Entrada interna del cache con timestamp de expiracion."""

    __slots__ = ("datos", "expira_en")

    def __init__(self, datos: list[IncidenciaGeo], ttl_segundos: int) -> None:
        self.datos = datos
        self.expira_en = time.monotonic() + ttl_segundos

    def esta_vigente(self) -> bool:
        """Retorna True si la entrada aun no ha expirado."""
        return time.monotonic() < self.expira_en


class CacheEnMemoria:
    """Cache en memoria con expiracion por TTL.

    Almacena listas de IncidenciaGeo indexadas por clave (nombre_fuente).
    Thread-safe para uso concurrente en FastAPI.
    """

    def __init__(self) -> None:
        self._almacen: dict[str, _EntradaCache] = {}
        self._candado = threading.Lock()

    def obtener(self, clave: str) -> list[IncidenciaGeo] | None:
        """Obtiene datos del cache si estan vigentes.

        Args:
            clave: Identificador del proveedor (ej: 'usgs').

        Returns:
            Lista de incidencias si el cache esta vigente, None si expiro
            o no existe.
        """
        with self._candado:
            entrada = self._almacen.get(clave)
            if entrada is None or not entrada.esta_vigente():
                # Limpiar entrada expirada
                self._almacen.pop(clave, None)
                return None
            return entrada.datos

    def almacenar(
        self, clave: str, datos: list[IncidenciaGeo], ttl_segundos: int
    ) -> None:
        """Almacena datos en cache con TTL especificado.

        Args:
            clave: Identificador del proveedor.
            datos: Lista de incidencias a cachear.
            ttl_segundos: Tiempo de vida en segundos.
        """
        with self._candado:
            self._almacen[clave] = _EntradaCache(datos, ttl_segundos)

    def invalidar(self, clave: str) -> None:
        """Elimina una entrada del cache explicitamente.

        Args:
            clave: Identificador del proveedor a invalidar.
        """
        with self._candado:
            self._almacen.pop(clave, None)

    def limpiar_expirados(self) -> int:
        """Elimina todas las entradas expiradas del cache.

        Returns:
            Cantidad de entradas eliminadas.
        """
        with self._candado:
            claves_expiradas = [
                clave
                for clave, entrada in self._almacen.items()
                if not entrada.esta_vigente()
            ]
            for clave in claves_expiradas:
                del self._almacen[clave]
            return len(claves_expiradas)
