import asyncio
import httpx
from starlette.requests import Request
from starlette.datastructures import Headers

from app.api.routes.reportes_ciudadanos import recibir_reporte_ciudadano


async def simular_peticion_frontend():
    print("=" * 70)
    print("SIMULACION 1: FORM-DATA CON COORDENADAS GPS VALIDAS")
    print("=" * 70)

    # Simular una llamada HTTP directa con cliente httpx
    transporte = httpx.ASGITransport(app=None)
    
    # Importar app de FastAPI
    from app.main import app

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as cliente:
        # Peticion 1: con coordenadas
        datos_formulario = {
            "descripcion": "Fuerte corriente arrastro escombros y bloqueo la avenida Cuauhtemoc, el agua subio a mas de medio metro y entro a varias casas.",
            "latitud": "22.2560",
            "longitud": "-97.8640",
            "nivel_prioridad": "alta",
        }
        archivos = {
            "archivo": ("evidencia_inundacion.jpg", b"BYTES_IMAGEN_TEST_SIMULADO", "image/jpeg")
        }

        resp1 = await cliente.post("/api/v1/publico/reportes", data=datos_formulario, files=archivos)
        print("Status Code 1:", resp1.status_code)
        json1 = resp1.json()
        print(f"Folio: {json1.get('folio_reporte')}")
        print(f"Tipo Emergencia (IA): {json1.get('tipo_emergencia')}")
        print(f"Prioridad (IA): {json1.get('nivel_prioridad')}")
        print(f"Resumen Analisis IA: {json1.get('resumen_analisis_ia')}")
        print(f"Coordenadas: {json1.get('coordenadas')}")
        print(f"Alerta Mapa: {json1.get('codigo_alerta_mapa')}")
        print(f"Evidencia URL: {json1.get('url_evidencia')}")

        print("\n" + "=" * 70)
        print("SIMULACION 2: FORM-DATA CON LAT=0, LON=0 (NULL ISLAND POR NUMBER(NULL))")
        print("=" * 70)

        # Peticion 2: con latitud=0 y longitud=0 (cuando JS hace Number(null))
        datos_sin_gps = {
            "descripcion": "Colapso de barda y socavon en carretera de acceso a Huejutla de Reyes, no hay paso para ningun vehiculo.",
            "latitud": "0",
            "longitud": "0",
            "nivel_prioridad": "alta",
        }

        resp2 = await cliente.post("/api/v1/publico/reportes", data=datos_sin_gps)
        print("Status Code 2:", resp2.status_code)
        json2 = resp2.json()
        print(f"Folio: {json2.get('folio_reporte')}")
        print(f"Tipo Emergencia (IA): {json2.get('tipo_emergencia')}")
        print(f"Prioridad (IA): {json2.get('nivel_prioridad')}")
        print(f"Resumen Analisis IA: {json2.get('resumen_analisis_ia')}")
        print(f"Coordenadas Inferidas por IA: {json2.get('coordenadas')}")
        print(f"Alerta Mapa: {json2.get('codigo_alerta_mapa')}")

        assert json2["coordenadas"]["es_estimada_por_ia"] is True, "ERROR: Debio detectar que 0,0 no es GPS real y estimar coordenadas con IA"
        assert abs(json2["coordenadas"]["latitud"]) > 1.0, "ERROR: La latitud no debe ser 0"

        print("\n" + "=" * 70)
        print("SIMULACION 3: COMPROBACION EN /publico/ubicaciones")
        print("=" * 70)
        resp_mapa = await cliente.get("/api/v1/publico/ubicaciones")
        bloqueos = [u for u in resp_mapa.json() if u.get("type") == "road_block"]
        print(f"Total bloqueos viales proyectados en el mapa: {len(bloqueos)}")
        print(f"Ultimos 2 bloqueos en el mapa:")
        for b in bloqueos[-2:]:
            print(f" - [{b['id']}] {b['name']} | Lat: {b['latitude']}, Lon: {b['longitude']}")

        print("\nTODAS LAS SIMULACIONES DE FORM-DATA DEL FRONTEND PASARON CON EXITO!")


if __name__ == "__main__":
    asyncio.run(simular_peticion_frontend())
