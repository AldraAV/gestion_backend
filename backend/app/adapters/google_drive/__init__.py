"""
Paquete adaptador para Google Drive API v3.
Incluye clientes duales (OAuth y Service Account), subida, descarga, busqueda y auditoria de seguridad.
"""

from .client import (
    obtener_servicio_drive_usuario,
    obtener_servicio_drive_sistema,
    resolver_servicio_drive,
    ErrorCredencialesGoogleDrive,
)
from .upload import (
    subir_archivo,
    crear_carpeta,
    ErrorSubidaGoogleDrive,
)
from .download import (
    descargar_archivo,
    ErrorDescargaGoogleDrive,
)
from .search import (
    buscar_archivos,
    ErrorBusquedaGoogleDrive,
)
from .audit import (
    auditar_archivo,
    auditar_carpeta,
    ErrorAuditoriaGoogleDrive,
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
