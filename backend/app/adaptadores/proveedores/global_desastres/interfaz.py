"""Interfaz abstracta para proveedores globales de desastres multirriesgo."""

from app.adaptadores.proveedores.base import ProveedorExterno


class ProveedorDesastresGlobal(ProveedorExterno):
    """Interfaz semantica para agregadores globales como GDACS."""

    pass
