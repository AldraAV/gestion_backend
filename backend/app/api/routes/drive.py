"""
Rutas de API para la gestion integral de Google Drive.
Permite subir, descargar, buscar y auditar archivos y permisos de seguridad.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Header, Response
from fastapi.responses import StreamingResponse
import io
import structlog

from app.adapters.google_drive import (
    resolver_servicio_drive,
    subir_archivo,
    crear_carpeta,
    descargar_archivo,
    buscar_archivos,
    auditar_archivo,
    auditar_carpeta,
    ErrorCredencialesGoogleDrive,
    ErrorSubidaGoogleDrive,
    ErrorDescargaGoogleDrive,
    ErrorBusquedaGoogleDrive,
    ErrorAuditoriaGoogleDrive,
)

registro = structlog.get_logger()
router = APIRouter(prefix="/drive", tags=["Google Drive"])

def obtener_drive_servicio(x_provider_token: Optional[str] = Header(None, alias="X-Provider-Token")):
    """
    Inyeccion de dependencia para resolver el cliente de Google Drive.
    Si el frontend envia el token OAuth de Google en la cabecera 'X-Provider-Token', se usa ese.
    De lo contrario, recurre a la Cuenta de Servicio configurada en el backend.
    """
    try:
        return resolver_servicio_drive(x_provider_token)
    except ErrorCredencialesGoogleDrive as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al inicializar servicio de Drive: {str(e)}")

@router.post("/upload", summary="Subir archivo a Google Drive")
async def api_subir_archivo(
    archivo: UploadFile = File(..., description="Archivo binario a subir"),
    carpeta_id: Optional[str] = Form(None, description="ID de la carpeta contenedora en Drive"),
    descripcion: Optional[str] = Form(None, description="Descripcion opcional del archivo"),
    servicio = Depends(obtener_drive_servicio)
) -> Dict[str, Any]:
    """
    Sube un archivo directamente a Google Drive con soporte para metadatos y asignacion de carpeta.
    """
    try:
        contenido = await archivo.read()
        mime = archivo.content_type or "application/octet-stream"
        resultado = subir_archivo(
            servicio=servicio,
            contenido_bytes=contenido,
            nombre_archivo=archivo.filename,
            tipo_mime=mime,
            carpeta_padre_id=carpeta_id,
            descripcion=descripcion
        )
        return {
            "exito": True,
            "mensaje": "Archivo subido correctamente a Google Drive.",
            "archivo": resultado
        }
    except ErrorSubidaGoogleDrive as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        registro.error("error_endpoint_subir_drive", error=str(e))
        raise HTTPException(status_code=500, detail=f"Fallo interno en subida: {str(e)}")

@router.post("/folder", summary="Crear carpeta en Google Drive")
def api_crear_carpeta(
    nombre_carpeta: str = Form(..., description="Nombre de la nueva carpeta"),
    carpeta_padre_id: Optional[str] = Form(None, description="ID de la carpeta padre"),
    servicio = Depends(obtener_drive_servicio)
) -> Dict[str, Any]:
    """
    Crea una carpeta estructurada en Google Drive.
    """
    try:
        carpeta = crear_carpeta(servicio, nombre_carpeta, carpeta_padre_id)
        return {"exito": True, "carpeta": carpeta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{archivo_id}", summary="Descargar o exportar archivo de Google Drive")
def api_descargar_archivo(
    archivo_id: str,
    formato_exportacion: Optional[str] = None,
    servicio = Depends(obtener_drive_servicio)
):
    """
    Descarga el flujo de bytes de un archivo o exporta un Google Doc nativo a formato estandar.
    """
    try:
        contenido_bytes, metadatos = descargar_archivo(servicio, archivo_id, formato_exportacion)
        nombre = metadatos.get("name", "archivo_descargado")
        tipo_mime = metadatos.get("mimeTypeExportado") or metadatos.get("mimeType", "application/octet-stream")

        return StreamingResponse(
            io.BytesIO(contenido_bytes),
            media_type=tipo_mime,
            headers={"Content-Disposition": f'attachment; filename="{nombre}"'}
        )
    except ErrorDescargaGoogleDrive as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", summary="Buscar archivos en Google Drive")
def api_buscar_archivos(
    q: Optional[str] = None,
    carpeta_id: Optional[str] = None,
    tipo_mime: Optional[str] = None,
    limite: int = 50,
    incluir_papelera: bool = False,
    servicio = Depends(obtener_drive_servicio)
) -> Dict[str, Any]:
    """
    Realiza busquedas avanzadas en Google Drive filtrando por nombre, carpetas o tipo MIME.
    """
    try:
        archivos = buscar_archivos(
            servicio=servicio,
            texto_busqueda=q,
            carpeta_padre_id=carpeta_id,
            tipo_mime=tipo_mime,
            limite=limite,
            incluir_papelera=incluir_papelera
        )
        return {"exito": True, "total": len(archivos), "archivos": archivos}
    except ErrorBusquedaGoogleDrive as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit/{archivo_id}", summary="Auditar permisos y seguridad de un archivo en Drive")
def api_auditar_archivo(
    archivo_id: str,
    servicio = Depends(obtener_drive_servicio)
) -> Dict[str, Any]:
    """
    Inspecciona colaboradores, revisiones, enlaces publicos y determina el nivel de riesgo de seguridad.
    """
    try:
        reporte = auditar_archivo(servicio, archivo_id)
        return {"exito": True, "auditoria": reporte}
    except ErrorAuditoriaGoogleDrive as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit-folder/{carpeta_id}", summary="Auditar seguridad de todos los archivos de una carpeta")
def api_auditar_carpeta(
    carpeta_id: str,
    limite: int = 50,
    servicio = Depends(obtener_drive_servicio)
) -> Dict[str, Any]:
    """
    Audita en lote los archivos contenidos en una carpeta y retorna la matriz de riesgo consolidada.
    """
    try:
        reporte = auditar_carpeta(servicio, carpeta_id, limite_archivos=limite)
        return {"exito": True, "auditoria_carpeta": reporte}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
