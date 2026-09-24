import json
import logging
from typing import Optional
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.reporte_ciudadano import TipoEmergenciaCiudadana, NivelPrioridadEmergencia

logger = logging.getLogger(__name__)


class ResultadoAnalisisReporte(BaseModel):
    tipo_emergencia: str = Field(
        default=TipoEmergenciaCiudadana.OTRO.value,
        description="Tipo de emergencia clasificada"
    )
    nivel_prioridad: str = Field(
        default=NivelPrioridadEmergencia.ALTA.value,
        description="Nivel de prioridad o triaje"
    )
    titulo_incidencia: str = Field(
        default="Incidencia Reportada por Ciudadano",
        description="Titulo sintetico para visualizacion en mapa"
    )
    resumen_analisis: str = Field(
        default="Reporte ciudadano recibido en centro de comando.",
        description="Sintesis analitica elaborada por la IA"
    )
    municipio_detectado: str = Field(
        default="Zona Conurbada",
        description="Municipio o demarcacion detectada"
    )
    es_bloqueo_o_riesgo_vial: bool = Field(
        default=True,
        description="Determina si debe proyectarse como punto de riesgo o bloqueo en el mapa"
    )
    radio_afectacion_km: float = Field(
        default=0.5,
        description="Radio estimado del perimetro de afectacion en kilometros"
    )
    latitud_estimada: Optional[float] = Field(
        default=None,
        description="Latitud estimada si no se proporciono GPS directo"
    )
    longitud_estimada: Optional[float] = Field(
        default=None,
        description="Longitud estimada si no se proporciono GPS directo"
    )


COORDENADAS_MUNICIPIOS_REFERENCIA = {
    "tampico": (22.2550, -97.8680),
    "madero": (22.2800, -97.8300),
    "ciudad madero": (22.2800, -97.8300),
    "altamira": (22.3900, -97.9300),
    "poza rica": (20.5333, -97.4500),
    "alamo": (20.9000, -97.6800),
    "alamo temapache": (20.9000, -97.6800),
    "panuco": (22.0500, -98.1800),
    "monterrey": (25.6866, -100.3161),
    "guadalupe": (25.6811, -100.2289),
    "huejutla": (21.1408, -98.4206),
    "tamazunchale": (21.2581, -98.7915),
    "victoria": (23.7509, -99.1506),
    "ciudad victoria": (23.7509, -99.1506),
    "reynosa": (26.0800, -98.2800),
    "rio bravo": (25.9822, -98.1105),
}


def analizar_reporte_con_heuristica(
    descripcion: str,
    direccion_referencia: Optional[str] = None,
    municipio_usuario: Optional[str] = None,
    latitud_usuario: Optional[float] = None,
    longitud_usuario: Optional[float] = None,
) -> ResultadoAnalisisReporte:
    """Metodo determinista de respaldo sin dependencias externas en caso de falla de API."""
    texto_combinado = f"{descripcion} {direccion_referencia or ''} {municipio_usuario or ''}".lower()

    # Clasificacion de tipo de emergencia
    if any(k in texto_combinado for k in ["atrapad", "rescate", "ahog", "techo"]):
        tipo = TipoEmergenciaCiudadana.PERSONA_ATRAPADA.value
        prioridad = NivelPrioridadEmergencia.CRITICA_VIDA_EN_RIESGO.value
        titulo = "Personas Atrapadas / Requiere Rescate Inmediato"
    elif any(k in texto_combinado for k in ["inund", "agua", "desborde", "rio", "laguna", "creciente"]):
        tipo = TipoEmergenciaCiudadana.INUNDACION_SEVERA.value
        prioridad = NivelPrioridadEmergencia.ALTA.value
        titulo = "Inundacion Severa y Encharcamiento Critico"
    elif any(k in texto_combinado for k in ["deslave", "derrumbe", "bloqueo", "camino", "carretera", "puente", "cerrado", "socavon"]):
        tipo = TipoEmergenciaCiudadana.DESLAVE_BLOQUEO_CAMINO.value
        prioridad = NivelPrioridadEmergencia.ALTA.value
        titulo = "Bloqueo Vial o Deslave en Camino"
    elif any(k in texto_combinado for k in ["herid", "medico", "ambulancia", "infarto", "sangr"]):
        tipo = TipoEmergenciaCiudadana.ATENCION_MEDICA_URGENTE.value
        prioridad = NivelPrioridadEmergencia.CRITICA_VIDA_EN_RIESGO.value
        titulo = "Emergencia Medica Urgente"
    elif any(k in texto_combinado for k in ["evacua", "salir", "refugio"]):
        tipo = TipoEmergenciaCiudadana.REQUIERE_EVACUACION.value
        prioridad = NivelPrioridadEmergencia.ALTA.value
        titulo = "Zona con Solicitud de Evacuacion"
    elif any(k in texto_combinado for k in ["comida", "agua potable", "desabasto", "hambre", "viveres"]):
        tipo = TipoEmergenciaCiudadana.DESABASTO_SUMINISTROS.value
        prioridad = NivelPrioridadEmergencia.MEDIA.value
        titulo = "Reporte de Desabasto de Insumos Basicos"
    else:
        tipo = TipoEmergenciaCiudadana.OTRO.value
        prioridad = NivelPrioridadEmergencia.MEDIA.value
        titulo = "Incidencia Ciudadana en Verificacion"

    # Deteccion de municipio
    municipio_det = "Zona Conurbada"
    for mun, (lat_ref, lon_ref) in COORDENADAS_MUNICIPIOS_REFERENCIA.items():
        if mun in texto_combinado:
            municipio_det = mun.title()
            break

    lat_est = latitud_usuario
    lon_est = longitud_usuario
    if lat_est is None or lon_est is None:
        mun_clave = municipio_det.lower()
        if mun_clave in COORDENADAS_MUNICIPIOS_REFERENCIA:
            lat_est, lon_est = COORDENADAS_MUNICIPIOS_REFERENCIA[mun_clave]
        else:
            # Coordenadas predeterminadas en zona conurbada Tampico-Madero
            lat_est, lon_est = (22.2550, -97.8680)

    return ResultadoAnalisisReporte(
        tipo_emergencia=tipo,
        nivel_prioridad=prioridad,
        titulo_incidencia=titulo,
        resumen_analisis=f"Evaluacion inicial de triaje: {tipo.replace('_', ' ').capitalize()}. Municipio detectado: {municipio_det}.",
        municipio_detectado=municipio_det,
        es_bloqueo_o_riesgo_vial=True,
        radio_afectacion_km=0.8,
        latitud_estimada=lat_est,
        longitud_estimada=lon_est,
    )


async def clasificar_reporte_ciudadano_con_ia(
    descripcion: str,
    direccion_referencia: Optional[str] = None,
    municipio_usuario: Optional[str] = None,
    latitud_usuario: Optional[float] = None,
    longitud_usuario: Optional[float] = None,
    nivel_prioridad_sugerido: Optional[str] = None,
    bytes_imagen: Optional[bytes] = None,
    mime_imagen: Optional[str] = None,
) -> ResultadoAnalisisReporte:
    """
    Analiza y estructura el reporte ciudadano utilizando la API de Google Gemini (Multimodal).
    Si la clave no esta configurada o el servicio no responde, aplica heuristica soberana.
    """
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY no configurada. Usando analizador heuristico.")
        return analizar_reporte_con_heuristica(
            descripcion, direccion_referencia, municipio_usuario, latitud_usuario, longitud_usuario
        )

    try:
        from google import genai
        from google.genai import types

        cliente = genai.Client(api_key=settings.GEMINI_API_KEY)

        prompt_sistema = """
Eres el sistema oficial de triaje, clasificacion y respuesta rapida de Proteccion Civil (SIGRAS).
Tu mision es analizar reportes de emergencia ciudadanos enviados por la poblacion civil durante contingencias climaticas y desastres naturales.
Si se adjunta una imagen o fotografia, debes analizarla visualmente para calibrar el dano, nivel de agua, obstruccion y gravedad real.

Debes extraer y clasificar de forma estructurada en formato JSON:
1. tipo_emergencia: Uno de ['inundacion_severa', 'persona_atrapada', 'deslave_bloqueo_camino', 'requiere_evacuacion', 'desabasto_suministros', 'atencion_medica_urgente', 'otro'].
2. nivel_prioridad: Uno de ['baja', 'media', 'alta', 'critica_vida_en_riesgo']. Si hay personas en peligro inminente de muerte o atrapadas por agua/derrumbe, es 'critica_vida_en_riesgo'.
3. titulo_incidencia: Un titulo sintetico, profesional y claro para el mapa de emergencias (maximo 70 caracteres).
4. resumen_analisis: Breve sintesis operativa para brigadistas y autoridades (1 o 2 oraciones).
5. municipio_detectado: Nombre del municipio inferido de la direccion, texto o contexto.
6. es_bloqueo_o_riesgo_vial: Booleano. True si la situacion bloquea o pone en peligro la circulacion vehicular o peatonal (para que las rutas de evacuacion la evadan).
7. radio_afectacion_km: Numero flotante estimando el radio de la zona de riesgo en kilometros (entre 0.2 y 5.0).
8. latitud_estimada: Si el usuario NO aporto coordenadas exactas, estima latitud aproximada del lugar si reconoces el punto en Mexico (especialmente Tamaulipas, Veracruz, Hidalgo, SLP, Nuevo Leon). Si no es posible, deja null.
9. longitud_estimada: Si el usuario NO aporto coordenadas exactas, estima longitud aproximada. Si no es posible, deja null.
"""

        cuerpo_reporte = f"""
DESCRIPCION DEL CIUDADANO: {descripcion}
DIRECCION O REFERENCIA INDICADA: {direccion_referencia or 'No especificada'}
MUNICIPIO INGRESADO: {municipio_usuario or 'No especificado'}
COORDENADAS GPS DISPOSITIVO: Lat={latitud_usuario}, Lon={longitud_usuario}
NIVEL DE PRIORIDAD SUGERIDO POR CIUDADANO: {nivel_prioridad_sugerido or 'No especificado'}
"""
        contenido_partes: list[types.Part | str] = [cuerpo_reporte]
        es_imagen_valida = (
            bytes_imagen is not None
            and len(bytes_imagen) > 32
            and (
                bytes_imagen.startswith(b"\xff\xd8\xff")  # JPEG
                or bytes_imagen.startswith(b"\x89PNG")    # PNG
                or bytes_imagen.startswith(b"RIFF")       # WEBP
                or bytes_imagen.startswith(b"GIF8")       # GIF
            )
        )
        if es_imagen_valida and mime_imagen and mime_imagen.startswith("image/"):
            contenido_partes.append(
                types.Part.from_bytes(data=bytes_imagen, mime_type=mime_imagen)
            )

        respuesta = cliente.models.generate_content(
            model="gemini-2.5-flash",
            contents=contenido_partes,
            config=types.GenerateContentConfig(
                system_instruction=prompt_sistema,
                response_mime_type="application/json",
                response_schema=ResultadoAnalisisReporte,
                temperature=0.2,
            ),
        )

        if respuesta.text:
            datos_json = json.loads(respuesta.text)
            resultado = ResultadoAnalisisReporte(**datos_json)

            # Si el usuario ya dio GPS exacto, respetarlo como verdad absoluta
            if latitud_usuario is not None and longitud_usuario is not None:
                resultado.latitud_estimada = latitud_usuario
                resultado.longitud_estimada = longitud_usuario
            elif resultado.latitud_estimada is None or resultado.longitud_estimada is None:
                # Si Gemini no pudo estimar coords, usar respaldo municipal
                mun = (resultado.municipio_detectado or municipio_usuario or "").lower()
                for k, coords in COORDENADAS_MUNICIPIOS_REFERENCIA.items():
                    if k in mun:
                        resultado.latitud_estimada, resultado.longitud_estimada = coords
                        break
                if resultado.latitud_estimada is None:
                    resultado.latitud_estimada, resultado.longitud_estimada = (22.2550, -97.8680)

            return resultado

    except Exception as exc:
        logger.error(f"Error al invocar Gemini API para analisis de reporte: {exc}", exc_info=True)

    # Fallback seguro
    return analizar_reporte_con_heuristica(
        descripcion, direccion_referencia, municipio_usuario, latitud_usuario, longitud_usuario
    )
