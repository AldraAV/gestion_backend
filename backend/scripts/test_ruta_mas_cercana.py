import asyncio
from app.api.routes.rutas_seguras import SolicitudRuta, calcular_ruta_segura

async def probar_calculo_ruta():
    # Coordenadas actuales del dispositivo del usuario (ejemplo Tampico Centro)
    solicitud = SolicitudRuta(
        siteId="", # Sin especificar albergue: el sistema debe buscar el real mas cercano
        latitude=22.2170,
        longitude=-97.8728
    )
    
    respuesta = await calcular_ruta_segura(solicitud)
    print("\n--- RUTA MAS CERCANA Y SEGURA CALCULADA ---")
    print(f"Ruta ID: {respuesta.routeId}")
    print(f"Origen: Lat {respuesta.origin.latitude}, Lon {respuesta.origin.longitude}")
    print(f"Destino Seleccionado: {respuesta.destination.name} (ID: {respuesta.destination.id})")
    print(f"Coordenadas Destino: Lat {respuesta.destination.latitude}, Lon {respuesta.destination.longitude}")
    print(f"Distancia Total: {respuesta.distanceMeters / 1000:.2f} km")
    print(f"Duracion Estimada: {respuesta.durationSeconds / 60:.1f} minutos")
    print(f"Puntos de Geometria: {len(respuesta.geometry)} coordenadas")
    print(f"Total Instrucciones de Navegacion: {len(respuesta.segments)}")
    print(f"Primera instruccion: {respuesta.segments[0].instruction if respuesta.segments else 'N/A'}")

asyncio.run(probar_calculo_ruta())
