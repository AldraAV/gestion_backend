"""
Rutas de API para la gestion de almacenamiento en Supabase Storage.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
import io
import structlog

from app.adapters.supabase import (
    AlmacenamientoSupabase,
    ErrorStorageSupabase,
    ErrorConfiguracionSupabase,
)

registro = structlog.get_logger()
router = APIRouter(prefix="/supabase/storage", tags=["Supabase Storage"])

@router.post("/upload", summary="Subir archivo a Supabase Storage")
async def api_subir_storage(
    archivo: UploadFile = File(..., description="Archivo a almacenar"),
    bucket: str = Form("archivos", description="Nombre del bucket en Supabase"),
    ruta_destino: Optional[str] = Form(None, description="Ruta o nombre personalizado en el bucket")
) -> Dict[str, Any]:
    """
    Sube un archivo directamente a un bucket de Supabase Storage.
    """
    try:
        gestor = AlmacenamientoSupabase(bucket_predeterminado=bucket)
        contenido = await archivo.read()
        ruta_final = ruta_destino or archivo.filename
        mime = archivo.content_type or "application/octet-stream"

        resultado = gestor.subir_archivo(
            ruta_en_bucket=ruta_final,
            contenido_bytes=contenido,
            tipo_mime=mime
        )
        url_publica = gestor.obtener_url_publica(ruta_final)
        resultado["url_publica"] = url_publica
        return {"exito": True, "datos": resultado}

    except ErrorConfiguracionSupabase as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ErrorStorageSupabase as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        registro.error("error_subida_supabase_storage", error=str(e))
        raise HTTPException(status_code=500, detail=f"Fallo interno en Supabase Storage: {str(e)}")

@router.get("/download", summary="Descargar archivo de Supabase Storage")
def api_descargar_storage(
    ruta: str = Query(..., description="Ruta del archivo en el bucket"),
    bucket: str = Query("archivos", description="Nombre del bucket")
):
    """
    Descarga el flujo de bytes de un archivo almacenado en Supabase Storage.
    """
    try:
        gestor = AlmacenamientoSupabase(bucket_predeterminado=bucket)
        contenido_bytes = gestor.descargar_archivo(ruta)
        nombre_archivo = ruta.split("/")[-1]

        return StreamingResponse(
            io.BytesIO(contenido_bytes),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'}
        )
    except ErrorStorageSupabase as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", summary="Listar archivos en Supabase Storage")
def api_listar_storage(
    prefijo: str = Query("", description="Prefijo o subcarpeta dentro del bucket"),
    bucket: str = Query("archivos", description="Nombre del bucket"),
    limite: int = Query(100, ge=1, le=500)
) -> Dict[str, Any]:
    """
    Lista los archivos contenidos en el bucket de Supabase.
    """
    try:
        gestor = AlmacenamientoSupabase(bucket_predeterminado=bucket)
        archivos = gestor.listar_archivos(prefijo_carpeta=prefijo, limite=limite)
        return {"exito": True, "total": len(archivos), "archivos": archivos}
    except ErrorStorageSupabase as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signed-url", summary="Generar URL temporal firmada")
def api_url_firmada(
    ruta: str = Query(..., description="Ruta del archivo en el bucket"),
    bucket: str = Query("archivos", description="Nombre del bucket"),
    expiracion_segundos: int = Query(3600, description="Segundos de validez")
) -> Dict[str, Any]:
    """
    Genera un enlace firmado temporal para descargar archivos privados de Supabase.
    """
    try:
        gestor = AlmacenamientoSupabase(bucket_predeterminado=bucket)
        url_firmada = gestor.obtener_url_firmada(ruta, expiracion_segundos)
        return {"exito": True, "url_firmada": url_firmada, "expira_en_segundos": expiracion_segundos}
    except ErrorStorageSupabase as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
