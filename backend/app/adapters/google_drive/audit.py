"""
Modulo de auditoria de seguridad y gobernanza de archivos en Google Drive.
Evalua permisos de acceso, exposicion publica, historial de revisiones y nivel de riesgo.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
from googleapiclient.discovery import Resource

registro = structlog.get_logger()

class ErrorAuditoriaGoogleDrive(Exception):
    """Excepcion lanzada ante errores durante la auditoria de archivos."""
    pass

def auditar_archivo(servicio: Resource, archivo_id: str) -> Dict[str, Any]:
    """
    Realiza una auditoria completa de seguridad sobre un archivo especifico en Google Drive.
    Analiza:
    1. Metadatos generales (propietario, tamaño, fechas).
    2. Lista de permisos y colaboradores.
    3. Deteccion de acceso publico o abierto al mundo.
    4. Historial de revisiones.
    5. Nivel de riesgo ('BAJO', 'MEDIO', 'ALTO', 'CRITICO').
    """
    try:
        # 1. Metadatos detallados
        metadatos = servicio.files().get(
            fileId=archivo_id,
            fields="id, name, mimeType, size, createdTime, modifiedTime, shared, owners, capabilities, permissions"
        ).execute()

        # 2. Lista de permisos completa
        permisos_resp = servicio.permissions().list(
            fileId=archivo_id,
            fields="permissions(id, type, role, emailAddress, displayName, allowFileDiscovery, domain)"
        ).execute()
        permisos = permisos_resp.get("permissions", [])

        # 3. Historial de revisiones (si esta disponible)
        try:
            revisiones_resp = servicio.revisions().list(
                fileId=archivo_id,
                fields="revisions(id, modifiedTime, lastModifyingUser)"
            ).execute()
            revisiones = revisiones_resp.get("revisions", [])
        except Exception:
            revisiones = []

        # 4. Evaluacion de Riesgo
        es_publico = False
        es_dominio_abierto = False
        total_editores = 0
        total_lectores = 0
        hallazgos: List[str] = []

        for perm in permisos:
            tipo_perm = perm.get("type")
            rol_perm = perm.get("role")

            if tipo_perm == "anyone":
                es_publico = True
                if rol_perm in ["writer", "editor"]:
                    hallazgos.append("CRITICO: El archivo es de acceso publico editable por cualquier persona con el enlace.")
                else:
                    hallazgos.append("ALTO: El archivo es de acceso publico de lectura para cualquier persona con el enlace.")
            
            if tipo_perm == "domain":
                es_dominio_abierto = True
                hallazgos.append(f"MEDIO: El archivo es accesible por todo el dominio corporativo ({perm.get('domain', 'global')}).")

            if rol_perm in ["writer", "editor", "owner"]:
                total_editores += 1
            elif rol_perm in ["reader", "commenter"]:
                total_lectores += 1

        # Calculo ponderado de nivel de riesgo
        if es_publico and any("CRITICO" in h for h in hallazgos):
            nivel_riesgo = "CRITICO"
        elif es_publico:
            nivel_riesgo = "ALTO"
        elif es_dominio_abierto or total_editores > 5:
            nivel_riesgo = "MEDIO"
        else:
            nivel_riesgo = "BAJO"

        recomendaciones: List[str] = []
        if es_publico:
            recomendaciones.append("Restringir el permiso publico ('anyone') a correos corporativos o usuarios especificos.")
        if total_editores > 3:
            recomendaciones.append("Revisar la lista de editores para aplicar el principio de minimo privilegio.")
        if not hallazgos:
            hallazgos.append("Acceso controlado adecuadamente. Sin riesgos aparentes de exposicion publica.")

        reporte = {
            "archivo_id": archivo_id,
            "nombre": metadatos.get("name"),
            "tipo_mime": metadatos.get("mimeType"),
            "tamano_bytes": metadatos.get("size"),
            "fecha_creacion": metadatos.get("createdTime"),
            "ultima_modificacion": metadatos.get("modifiedTime"),
            "propietarios": [p.get("emailAddress") for p in metadatos.get("owners", [])],
            "compartido": metadatos.get("shared", False),
            "nivel_riesgo": nivel_riesgo,
            "es_publico": es_publico,
            "total_editores": total_editores,
            "total_lectores": total_lectores,
            "total_revisiones": len(revisiones),
            "hallazgos": hallazgos,
            "recomendaciones": recomendaciones,
            "permisos_detallados": permisos
        }

        registro.info("auditoria_archivo_completada", id=archivo_id, riesgo=nivel_riesgo)
        return reporte

    except Exception as e:
        registro.error("error_auditar_archivo_drive", id=archivo_id, error=str(e))
        raise ErrorAuditoriaGoogleDrive(f"Error durante la auditoria del archivo: {str(e)}")

def auditar_carpeta(servicio: Resource, carpeta_id: str, limite_archivos: int = 50) -> Dict[str, Any]:
    """
    Audita los archivos contenidos en una carpeta de Google Drive y entrega una matriz consolidada de riesgo.
    """
    from .search import buscar_archivos
    try:
        archivos = buscar_archivos(servicio, carpeta_padre_id=carpeta_id, limite=limite_archivos)
        reportes_archivos = []
        resumen_riesgo = {"CRITICO": 0, "ALTO": 0, "MEDIO": 0, "BAJO": 0}

        for arch in archivos:
            rep = auditar_archivo(servicio, arch["id"])
            reportes_archivos.append(rep)
            resumen_riesgo[rep["nivel_riesgo"]] += 1

        return {
            "carpeta_id": carpeta_id,
            "total_archivos_auditados": len(reportes_archivos),
            "resumen_riesgo": resumen_riesgo,
            "archivos": reportes_archivos
        }
    except Exception as e:
        registro.error("error_auditar_carpeta_drive", carpeta=carpeta_id, error=str(e))
        raise ErrorAuditoriaGoogleDrive(f"Error al auditar carpeta: {str(e)}")
