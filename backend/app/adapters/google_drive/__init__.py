"""
Paquete adaptador para Google Drive API v3.
Incluye clientes duales (OAuth y Service Account), subida, descarga, busqueda y auditoria de seguridad.
"""

from .audit import (
    ErrorAuditoriaGoogleDrive,
    auditar_archivo,
    auditar_carpeta,
)
from .client import (
    ErrorCredencialesGoogleDrive,
    obtener_servicio_drive_sistema,
    obtener_servicio_drive_usuario,
    resolver_servicio_drive,
)
from .download import (
    ErrorDescargaGoogleDrive,
    descargar_archivo,
)
from .search import (
    ErrorBusquedaGoogleDrive,
    buscar_archivos,
)
from .upload import (
    ErrorSubidaGoogleDrive,
    crear_carpeta,
    subir_archivo,
)

__all__ = [
    "obtener_servicio_drive_usuario",
    "obtener_servicio_drive_sistema",
    "resolver_servicio_drive",
    "ErrorCredencialesGoogleDrive",
    "subir_archivo",
    "crear_carpeta",
    "ErrorSubidaGoogleDrive",
    "descargar_archivo",
    "ErrorDescargaGoogleDrive",
    "buscar_archivos",
    "ErrorBusquedaGoogleDrive",
    "auditar_archivo",
    "auditar_carpeta",
    "ErrorAuditoriaGoogleDrive",
]
