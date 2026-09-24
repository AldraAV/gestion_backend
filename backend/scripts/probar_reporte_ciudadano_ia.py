import asyncio
import json
import httpx

from app.api.routes.reportes_ciudadanos import (
    SolicitudReporteCiudadano,
    recibir_reporte_ciudadano,
)
from app.api.routes.ubicaciones import consultar_ubicaciones_base_datos
from app.api.routes.rutas_seguras import SolicitudRuta, calcular_ruta_segura


async def probar_sistema_reportes_ia():
    print("=" * 70)
    print("TEST 1: REPORTE CIUDADANO CON GPS DIRECTO Y ATENCION CRITICA")
    print("=" * 70)

    reporte_1 = SolicitudReporteCiudadano(
        descripcion="Se desbordo la laguna del Carpintero y el nivel del agua sobrepasa un metro. Hay una familia atrapada en la azotea con una persona de la tercera edad y un bebe.",
        latitud=22.2350,
        longitud=-97.8590,
        direccion_referencia="Calle Morelos esquina con Boulevard Fidel Velazquez, frente a la laguna",
        municipio="Tampico",
        personas_afectadas=4,
        personas_vulnerables=2,
        telefono_contacto="8331234567"
    )

    respuesta_1 = await recibir_reporte_ciudadano(reporte_1)
    print(f"Folio Generado: {respuesta_1.folio_reporte}")
    print(f"Tipo Emergencia (IA): {respuesta_1.tipo_emergencia}")
    print(f"Prioridad (IA): {respuesta_1.nivel_prioridad}")
    print(f"Resumen Analisis IA: {respuesta_1.resumen_analisis_ia}")
    print(f"Coordenadas: Lat {respuesta_1.coordenadas.latitud}, Lon {respuesta_1.coordenadas.longitud} (Estimada: {respuesta_1.coordenadas.es_estimada_por_ia})")
    print(f"Incidencia Generada en Mapa: {respuesta_1.incidencia_mapa_generada} - Codigo: {respuesta_1.codigo_alerta_mapa}")
    print(f"Radio de Afectacion: {respuesta_1.radio_afectacion_km} km")

    print("\n" + "=" * 70)
    print("TEST 2: REPORTE CIUDADANO SIN GPS (ESTIMACION DE COORDENADAS POR IA)")
    print("=" * 70)

    reporte_2 = SolicitudReporteCiudadano(
        descripcion="Deslave masivo de tierra y rocas que bloqueo por completo la carretera en la sierra de Tepehuacan de Guerrero, camino a Huejutla. Ningun carro puede pasar.",
        direccion_referencia="Carretera estatal tramo Tepeco a Santa Ana",
        municipio="Tepehuacan de Guerrero",
        personas_afectadas=20,
        personas_vulnerables=0
    )

    respuesta_2 = await recibir_reporte_ciudadano(reporte_2)
    print(f"Folio Generado: {respuesta_2.folio_reporte}")
    print(f"Tipo Emergencia (IA): {respuesta_2.tipo_emergencia}")
    print(f"Prioridad (IA): {respuesta_2.nivel_prioridad}")
    print(f"Resumen Analisis IA: {respuesta_2.resumen_analisis_ia}")
    print(f"Coordenadas: Lat {respuesta_2.coordenadas.latitud}, Lon {respuesta_2.coordenadas.longitud} (Estimada: {respuesta_2.coordenadas.es_estimada_por_ia})")
    print(f"Incidencia Generada en Mapa: {respuesta_2.incidencia_mapa_generada} - Codigo: {respuesta_2.codigo_alerta_mapa}")

    print("\n" + "=" * 70)
    print("TEST 3: VERIFICACION DE INCIDENCIAS EN EL MAPA PUBLICO (/publico/ubicaciones)")
    print("=" * 70)

    ubicaciones = consultar_ubicaciones_base_datos()
    bloqueos = [u for u in ubicaciones if u.get("type") == "road_block"]
    print(f"Total bloqueos viales e incidencias en el mapa: {len(bloqueos)}")
    
    codigos_creados = [respuesta_1.codigo_alerta_mapa, respuesta_2.codigo_alerta_mapa]
    encontrados = 0
    for b in bloqueos:
        print(f" - [{b['id']}] {b['name']} | Severidad: {b.get('severity')} | Lat: {b['latitude']}, Lon: {b['longitude']}")
        if b['id'] in codigos_creados:
            encontrados += 1

    print(f"\nIncidencias creadas por los reportes encontradas en el mapa: {encontrados}/{len(codigos_creados)}")
    assert encontrados >= 2, "ERROR: Las incidencias no se reflejaron en el mapa publico"

    print("\n" + "=" * 70)
    print("TEST 4: CALCULO DE RUTA SEGURA EVADIENDO LAS NUEVAS INCIDENCIAS")
    print("=" * 70)

    solicitud_ruta = SolicitudRuta(
        siteId="",
        latitude=22.2200,
        longitude=-97.8600
    )
    ruta = await calcular_ruta_segura(solicitud_ruta)
    print(f"Ruta hacia: {ruta.destination.name}")
    print(f"Distancia Total: {ruta.distanceMeters / 1000:.2f} km")
    print(f"Puntos de Geometria calculados: {len(ruta.geometry)}")
    print(f"Paso 1: {ruta.segments[0].instruction if ruta.segments else 'N/A'}")

    print("\nTODOS LOS TESTS DE REPORTES CON IA E INCIDENCIAS EN MAPA PASARON EXITOSAMENTE!")


if __name__ == "__main__":
    asyncio.run(probar_sistema_reportes_ia())
