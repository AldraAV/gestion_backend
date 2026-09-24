"""Interfaz abstracta para proveedores de datos climaticos."""

from app.adaptadores.proveedores.base import ProveedorExterno


class ProveedorClima(ProveedorExterno):
    """Interfaz semantica para proveedores de clima."""

    pass
