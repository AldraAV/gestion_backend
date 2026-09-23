"""
Modulo de subida de archivos y creacion de carpetas en Google Drive.
"""

import io
from typing import Dict, Any, Optional, List
import structlog
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import Resource

registro = structlog.get_logger()

class ErrorSubidaGoogleDrive(Exception):
    """Excepcion lanzada ante errores durante la carga de archivos."""
    pass

def crear_carpeta(
    servicio: Resource,
    nombre_carpeta: str,
    carpeta_padre_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Crea una nueva carpeta en Google Drive y retorna su identificador y metadata.
    """
    try:
        metadatos = {
            "name": nombre_carpeta,
            "mimeType": "application/vnd.google-apps.folder"
        }
        if carpeta_padre_id:
            metadatos["parents"] = [carpeta_padre_id]
        
        carpeta = servicio.files().create(
            body=metadatos,
            fields="id, name, mimeType, webViewLink"
        ).execute()
        
        registro.info("carpeta_creada_en_drive", id=carpeta.get("id"), nombre=nombre_carpeta)
        return carpeta
    except Exception as e:
        registro.error("error_crear_carpeta_drive", nombre=nombre_carpeta, error=str(e))
        raise ErrorSubidaGoogleDrive(f"Error al crear carpeta en Google Drive: {str(e)}")

def subir_archivo(
    servicio: Resource,
    contenido_bytes: bytes,
    nombre_archivo: str,
    tipo_mime: str = "application/octet-stream",
    carpeta_padre_id: Optional[str] = None,
    descripcion: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sube un archivo en memoria (bytes) hacia Google Drive.
    Retorna la metadata del archivo creado (id, name, size, webViewLink, webContentLink).
    """
    try:
        metadatos_cuerpo: Dict[str, Any] = {
            "name": nombre_archivo,
            "mimeType": tipo_mime
        }
        
        if carpeta_padre_id:
            metadatos_cuerpo["parents"] = [carpeta_padre_id]
            
        if descripcion:
            metadatos_cuerpo["description"] = descripcion

        flujo_memoria = io.BytesIO(contenido_bytes)
        medio = MediaIoBaseUpload(
            flujo_memoria,
            mimetype=tipo_mime,
            resumable=True
        )

        campos_solicitados = "id, name, mimeType, size, createdTime, modifiedTime, webViewLink, webContentLink, owners"
        
        archivo_creado = servicio.files().create(
            body=metadatos_cuerpo,
            media_body=medio,
            fields=campos_solicitados
        ).execute()

        registro.info("archivo_subido_a_drive", id=archivo_creado.get("id"), nombre=nombre_archivo)
        return archivo_creado

    except Exception as e:
        registro.error("error_subir_archivo_drive", nombre=nombre_archivo, error=str(e))
        raise ErrorSubidaGoogleDrive(f"Fallo al subir archivo a Google Drive: {str(e)}")
