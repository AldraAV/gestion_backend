"""
Modulo de almacenamiento en Supabase Storage.
Maneja operaciones de carga, descarga, listado y generacion de URLs firmadas para buckets.
"""

from typing import List, Dict, Any, Optional
import structlog
from .client import obtener_cliente_supabase_admin

registro = structlog.get_logger()

class ErrorStorageSupabase(Exception):
    """Excepcion para fallos en operaciones de almacenamiento en Supabase."""
    pass

class AlmacenamientoSupabase:
    def __init__(self, bucket_predeterminado: str = "archivos"):
        self.bucket = bucket_predeterminado
        self._cliente = obtener_cliente_supabase_admin()

    def subir_archivo(self, ruta_en_bucket: str, contenido_bytes: bytes, tipo_mime: str = "application/octet-stream") -> Dict[str, Any]:
        """
        Sube un archivo al bucket de Supabase Storage especificado.
        """
        try:
            opciones = {"content-type": tipo_mime, "upsert": "true"}
            respuesta = self._cliente.storage.from_(self.bucket).upload(
                path=ruta_en_bucket,
                file=contenido_bytes,
                file_options=opciones
            )
            return {
                "exito": True,
                "ruta": ruta_en_bucket,
                "bucket": self.bucket,
                "respuesta": respuesta
            }
        except Exception as e:
            registro.error("error_subir_storage_supabase", bucket=self.bucket, ruta=ruta_en_bucket, error=str(e))
            raise ErrorStorageSupabase(f"Error al subir archivo a Supabase Storage: {str(e)}")

    def descargar_archivo(self, ruta_en_bucket: str) -> bytes:
        """
        Descarga los bytes crudos de un archivo almacenado en Supabase Storage.
        """
        try:
            datos = self._cliente.storage.from_(self.bucket).download(ruta_en_bucket)
            return datos
        except Exception as e:
            registro.error("error_descargar_storage_supabase", bucket=self.bucket, ruta=ruta_en_bucket, error=str(e))
            raise ErrorStorageSupabase(f"Error al descargar archivo de Supabase Storage: {str(e)}")

    def obtener_url_publica(self, ruta_en_bucket: str) -> str:
        """
        Genera la URL publica directa para acceder a un recurso si el bucket es publico.
        """
        return self._cliente.storage.from_(self.bucket).get_public_url(ruta_en_bucket)

    def obtener_url_firmada(self, ruta_en_bucket: str, expiracion_segundos: int = 3600) -> str:
        """
        Genera una URL temporal firmada para acceder a un recurso privado.
        """
        try:
            respuesta = self._cliente.storage.from_(self.bucket).create_signed_url(ruta_en_bucket, expiracion_segundos)
            return respuesta.get("signedURL", "")
        except Exception as e:
            registro.error("error_generar_url_firmada", ruta=ruta_en_bucket, error=str(e))
            raise ErrorStorageSupabase(f"Error al generar URL firmada: {str(e)}")

    def listar_archivos(self, prefijo_carpeta: str = "", limite: int = 100) -> List[Dict[str, Any]]:
        """
        Lista los archivos contenidos en una carpeta o prefijo del bucket.
        """
        try:
            archivos = self._cliente.storage.from_(self.bucket).list(path=prefijo_carpeta, options={"limit": limite})
            return archivos
        except Exception as e:
            registro.error("error_listar_storage_supabase", error=str(e))
            raise ErrorStorageSupabase(f"Error al listar archivos: {str(e)}")
