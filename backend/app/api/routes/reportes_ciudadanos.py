import datetime
import logging
import uuid
from typing import Optional

import psycopg
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.adapters.analizador_reportes_ia import (
    ResultadoAnalisisReporte,
    clasificar_reporte_ciudadano_con_ia,
)
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/publico/reportes", tags=["Reportes Ciudadanos e IA"])


class CoordenadasRegistradas(BaseModel):
    latitud: float
    longitud: float
    es_estimada_por_ia: bool


class RespuestaReporteCiudadano(BaseModel):
    folio_reporte: str
    mensaje: str
    tipo_emergencia: str
    nivel_prioridad: str
    resumen_analisis_ia: str
    coordenadas: CoordenadasRegistradas
    incidencia_mapa_generada: bool
    codigo_alerta_mapa: Optional[str] = None
    radio_afectacion_km: float
    url_evidencia: Optional[str] = None


MAPEO_TIPO_FENOMENO = {
    "inundacion_severa": "Inundacion",
    "persona_atrapada": "Rescate y Evacuacion",
    "deslave_bloqueo_camino": "Deslave / Bloqueo Vial",
    "requiere_evacuacion": "Zona de Evacuacion",
    "desabasto_suministros": "Desabasto Critico",
    "atencion_medica_urgente": "Emergencia Medica",
    "otro": "Riesgo Hidrometeorologico",
}

MAPEO_NIVEL_ALERTA = {
    "critica_vida_en_riesgo": "roja",
    "alta": "naranja",
    "media": "amarillo",
    "baja": "verde",
}


def guardar_reporte_e_incidencia(
    descripcion: str,
    analisis: ResultadoAnalisisReporte,
    folio_reporte: str,
    latitud_final: float,
    longitud_final: float,
    url_evidencia: Optional[str] = None,
) -> tuple[uuid.UUID, Optional[str]]:
    """Persiste atomica y deterministamente el reporte y genera la alerta vial en Supabase."""
    cadena_conexion = str(settings.DATABASE_URL).replace("+psycopg", "")
    id_reporte = uuid.uuid4()
    codigo_alerta = f"INC-{folio_reporte}"

    tipo_fenomeno = MAPEO_TIPO_FENOMENO.get(
        analisis.tipo_emergencia, "Incidencia de Proteccion Civil"
    )
    nivel_alerta = MAPEO_NIVEL_ALERTA.get(analisis.nivel_prioridad, "amarillo")

    with psycopg.connect(cadena_conexion) as conexion:
        with conexion.cursor() as cursor:
            # 1. Insercion en reporte_ciudadano
            cursor.execute(
                """
                INSERT INTO reporte_ciudadano (
                    id, folio_reporte, tipo_emergencia, descripcion,
                    latitud, longitud, direccion_referencia, municipio,
                    nivel_prioridad, estado_reporte, personas_afectadas,
                    personas_vulnerables, telefono_contacto, url_evidencia_multimedia,
                    fecha_reporte
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, 'recibido', 1,
                    0, NULL, %s,
                    NOW()
                )
                """,
                (
                    id_reporte,
                    folio_reporte,
                    analisis.tipo_emergencia,
                    descripcion,
                    latitud_final,
                    longitud_final,
                    analisis.resumen_analisis,
                    analisis.municipio_detectado or "Sin especificar",
                    analisis.nivel_prioridad,
                    url_evidencia,
                ),
            )

            # 2. Generacion de la incidencia en alerta_zona_riesgo para proyeccion inmediata en el mapa
            cursor.execute(
                """
                INSERT INTO alerta_zona_riesgo (
                    id, codigo_alerta, titulo, tipo_fenomeno,
                    nivel_alerta, descripcion, municipios_afectados,
                    latitud_referencia, longitud_referencia, radio_afectacion_km,
                    activo, fecha_emision
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    true, NOW()
                )
                """,
                (
                    uuid.uuid4(),
                    codigo_alerta,
                    analisis.titulo_incidencia,
                    tipo_fenomeno,
                    nivel_alerta,
                    f"{analisis.resumen_analisis} | Ciudadano: {descripcion}",
                    analisis.municipio_detectado,
                    latitud_final,
                    longitud_final,
                    analisis.radio_afectacion_km,
                ),
            )

            conexion.commit()

    return id_reporte, codigo_alerta


@router.post(
    "",
    response_model=RespuestaReporteCiudadano,
    status_code=status.HTTP_201_CREATED,
    summary="Recepcion de reportes ciudadanos (FormData / JSON) con analisis de IA y proyeccion en mapa",
)
@router.post(
    "/",
    response_model=RespuestaReporteCiudadano,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def recibir_reporte_ciudadano(peticion: Request) -> RespuestaReporteCiudadano:
    """
    Cacha el formulario del frontend (descripcion, latitud, longitud, nivel_prioridad, archivo).
    La IA (Gemini 2.5 Flash) realiza el triaje semantico y visual, infiere coordenadas
    si no estan presentes o son nulas, y proyecta la incidencia en el mapa publico.
    """
    try:
        tipo_contenido = peticion.headers.get("content-type", "")
        descripcion = ""
        latitud_ingresada: Optional[float] = None
        longitud_ingresada: Optional[float] = None
        nivel_prioridad_ingresado: Optional[str] = None
        bytes_archivo: Optional[bytes] = None
        tipo_mime_archivo: Optional[str] = None
        url_evidencia: Optional[str] = None

        if "multipart/form-data" in tipo_contenido or "application/x-www-form-urlencoded" in tipo_contenido:
            formulario = await peticion.form()
            descripcion = str(formulario.get("descripcion") or "").strip()

            # Extraer latitud y longitud tolerando Number(null) => 0 en JS
            raw_lat = formulario.get("latitud")
            raw_lon = formulario.get("longitud")
            try:
                if raw_lat is not None and str(raw_lat).strip() not in ("", "null", "undefined", "NaN"):
                    val_lat = float(raw_lat)
                    if abs(val_lat) > 0.001:  # Ignorar Null Island (0,0)
                        latitud_ingresada = val_lat
            except (ValueError, TypeError):
                latitud_ingresada = None

            try:
                if raw_lon is not None and str(raw_lon).strip() not in ("", "null", "undefined", "NaN"):
                    val_lon = float(raw_lon)
                    if abs(val_lon) > 0.001:  # Ignorar Null Island (0,0)
                        longitud_ingresada = val_lon
            except (ValueError, TypeError):
                longitud_ingresada = None

            raw_nivel = formulario.get("nivel_prioridad")
            if raw_nivel and str(raw_nivel).strip() not in ("", "null", "undefined"):
                nivel_prioridad_ingresado = str(raw_nivel).strip()

            archivo_subido = formulario.get("archivo")
            if archivo_subido and hasattr(archivo_subido, "read") and hasattr(archivo_subido, "filename") and archivo_subido.filename:
                bytes_archivo = await archivo_subido.read()
                tipo_mime_archivo = getattr(archivo_subido, "content_type", "image/jpeg")
                nombre_limpio = f"{uuid.uuid4().hex[:8]}_{archivo_subido.filename}"
                url_evidencia = f"/evidencias/{nombre_limpio}"

        else:
            # Soporte complementario para llamadas JSON directas
            cuerpo_json = await peticion.json()
            descripcion = str(cuerpo_json.get("descripcion") or "").strip()
            raw_lat = cuerpo_json.get("latitud")
            raw_lon = cuerpo_json.get("longitud")
            if raw_lat is not None and abs(float(raw_lat)) > 0.001:
                latitud_ingresada = float(raw_lat)
            if raw_lon is not None and abs(float(raw_lon)) > 0.001:
                longitud_ingresada = float(raw_lon)
            nivel_prioridad_ingresado = cuerpo_json.get("nivel_prioridad")
            url_evidencia = cuerpo_json.get("url_evidencia_multimedia")

        if not descripcion:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El campo 'descripcion' es obligatorio para procesar el reporte ciudadano.",
            )

        # 1. Triaje inteligente con IA (Gemini 2.5 Flash con soporte multimodal)
        analisis: ResultadoAnalisisReporte = await clasificar_reporte_ciudadano_con_ia(
            descripcion=descripcion,
            direccion_referencia=None,
            municipio_usuario=None,
            latitud_usuario=latitud_ingresada,
            longitud_usuario=longitud_ingresada,
            nivel_prioridad_sugerido=nivel_prioridad_ingresado,
            bytes_imagen=bytes_archivo,
            mime_imagen=tipo_mime_archivo,
        )

        # 2. Resolucion de coordenadas efectivas
        es_estimada = False
        if latitud_ingresada is not None and longitud_ingresada is not None:
            latitud_final = latitud_ingresada
            longitud_final = longitud_ingresada
        else:
            latitud_final = float(analisis.latitud_estimada if analisis.latitud_estimada is not None else 22.2550)
            longitud_final = float(analisis.longitud_estimada if analisis.longitud_estimada is not None else -97.8680)
            es_estimada = True

        # 3. Folio unico de atencion
        fecha_prefijo = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
        folio = f"REP-{fecha_prefijo}-{uuid.uuid4().hex[:6].upper()}"

        # 4. Guardar en base de datos y proyectar alerta vial activa en el mapa
        _, codigo_alerta = guardar_reporte_e_incidencia(
            descripcion=descripcion,
            analisis=analisis,
            folio_reporte=folio,
            latitud_final=latitud_final,
            longitud_final=longitud_final,
            url_evidencia=url_evidencia,
        )

        # 5. Enrutar respuesta estructurada al frontend
        return RespuestaReporteCiudadano(
            folio_reporte=folio,
            mensaje="Reporte ciudadano procesado y verificado con exito. Incidencia proyectada en el mapa en tiempo real.",
            tipo_emergencia=analisis.tipo_emergencia,
            nivel_prioridad=analisis.nivel_prioridad,
            resumen_analisis_ia=analisis.resumen_analisis,
            coordenadas=CoordenadasRegistradas(
                latitud=latitud_final,
                longitud=longitud_final,
                es_estimada_por_ia=es_estimada,
            ),
            incidencia_mapa_generada=True,
            codigo_alerta_mapa=codigo_alerta,
            radio_afectacion_km=analisis.radio_afectacion_km,
            url_evidencia=url_evidencia,
        )

    except HTTPException:
        raise
    except Exception as error_inesperado:
        logger.error(f"Error critico al enrutar reporte ciudadano: {error_inesperado}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fallo del servidor al procesar el reporte: {str(error_inesperado)}",
        )
