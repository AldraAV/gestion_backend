"""
Modulo de descarga y exportacion de archivos desde Google Drive.
"""

import io
from typing import Any

import structlog
from googleapiclient.discovery import Resource
from googleapiclient.http import MediaIoBaseDownload

registro = structlog.get_logger()

# Mapeo de tipos de Google Workspace a formatos de exportacion estandar
MAPA_EXPORTACION_GOOGLE = {
    "application/vnd.google-apps.document": "application/pdf",
    "application/vnd.google-apps.spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.google-apps.presentation": "application/pdf",
}


class ErrorDescargaGoogleDrive(Exception):
    """Excepcion lanzada ante fallos en la descarga de archivos."""

    pass


def descargar_archivo(
    servicio: Resource, archivo_id: str, mime_exportacion: str | None = None
) -> tuple[bytes, dict[str, Any]]:
    """
    Descarga el contenido de un archivo de Google Drive.
    Si el archivo es un documento nativo de Google (Docs, Sheets, Slides), ejecuta files().export_media().
    Si es un binario estandar, ejecuta files().get_media().

    Retorna una tupla: (contenido_en_bytes, metadatos_del_archivo).
    """
    try:
        # 1. Obtener metadatos para conocer el MIME type real
        metadatos = (
            servicio.files()
            .get(fileId=archivo_id, fields="id, name, mimeType, size, modifiedTime")
            .execute()
        )

        tipo_mime = metadatos.get("mimeType", "")
        flujo_destino = io.BytesIO()

        # 2. Verificar si es documento nativo de Google
        if (
            tipo_mime.startswith("application/vnd.google-apps.")
            and tipo_mime in MAPA_EXPORTACION_GOOGLE
        ):
            mime_final = mime_exportacion or MAPA_EXPORTACION_GOOGLE[tipo_mime]
            peticion = servicio.files().export_media(
                fileId=archivo_id, mimeType=mime_final
            )
            descargador = MediaIoBaseDownload(flujo_destino, peticion)
            completado = False
            while not completado:
                _, completado = descargador.next_chunk()
            metadatos["mimeTypeExportado"] = mime_final
        else:
            peticion = servicio.files().get_media(fileId=archivo_id)
            descargador = MediaIoBaseDownload(flujo_destino, peticion)
            completado = False
            while not completado:
                _, completado = descargador.next_chunk()

        registro.info(
            "archivo_descargado_de_drive",
            id=archivo_id,
            bytes_totales=flujo_destino.tell(),
        )
        return flujo_destino.getvalue(), metadatos

    except Exception as e:
        registro.error("error_descargar_archivo_drive", id=archivo_id, error=str(e))
        raise ErrorDescargaGoogleDrive(
            f"Error al descargar archivo de Google Drive: {str(e)}"
        )
