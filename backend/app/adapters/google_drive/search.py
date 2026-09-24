"""
Modulo de busqueda avanzada de archivos en Google Drive.
Construye consultas estructuradas (Search Query Language de Drive API v3).
"""

from typing import Any

import structlog
from googleapiclient.discovery import Resource

registro = structlog.get_logger()


class ErrorBusquedaGoogleDrive(Exception):
    """Excepcion lanzada ante errores de busqueda en Drive."""

    pass


def buscar_archivos(
    servicio: Resource,
    texto_busqueda: str | None = None,
    carpeta_padre_id: str | None = None,
    tipo_mime: str | None = None,
    limite: int = 50,
    ordenar_por: str = "modifiedTime desc",
    incluir_papelera: bool = False,
) -> list[dict[str, Any]]:
    """
    Realiza busquedas avanzadas de archivos en Google Drive.
    Permite filtrar por nombre, carpeta contenedora, tipo MIME y estado.
    """
    try:
        condiciones = []

        if not incluir_papelera:
            condiciones.append("trashed = false")

        if texto_busqueda:
            texto_limpio = texto_busqueda.replace("'", "\\'")
            condiciones.append(f"name contains '{texto_limpio}'")

        if carpeta_padre_id:
            condiciones.append(f"'{carpeta_padre_id}' in parents")

        if tipo_mime:
            condiciones.append(f"mimeType = '{tipo_mime}'")

        consulta_final = " and ".join(condiciones) if condiciones else ""

        campos = "nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink, owners, shared)"

        respuesta = (
            servicio.files()
            .list(
                q=consulta_final,
                pageSize=min(limite, 100),
                fields=campos,
                orderBy=ordenar_por,
            )
            .execute()
        )

        archivos = respuesta.get("files", [])
        registro.info(
            "busqueda_drive_completada", total=len(archivos), consulta=consulta_final
        )
        return archivos

    except Exception as e:
        registro.error("error_buscar_archivos_drive", error=str(e))
        raise ErrorBusquedaGoogleDrive(
            f"Error al buscar archivos en Google Drive: {str(e)}"
        )
