"""Interfaz abstracta para proveedores de datos sismicos."""

from app.adaptadores.proveedores.base import ProveedorExterno


class ProveedorSismos(ProveedorExterno):
    """Interfaz semantica para proveedores de sismos."""

    pass
