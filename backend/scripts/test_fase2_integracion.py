"""
Suite de pruebas para la Fase 2: APIs de desastres + contratos frontend.

Ejecutar con: uv run python scripts/test_fase2_integracion.py
"""

import asyncio
import sys
import time
from pathlib import Path

# Agregar el directorio raiz del backend al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


async def test_cache_memoria():
    """Prueba unitaria del cache en memoria con TTL."""
    print("\n--- Test: CacheEnMemoria ---")
    from app.adaptadores.proveedores.base import IncidenciaGeo
    from app.adaptadores.proveedores.cache_memoria import CacheEnMemoria

    cache = CacheEnMemoria()

    # Crear datos de prueba
    datos_prueba = [
        IncidenciaGeo(
            tipo="sismo",
            fuente="usgs",
            titulo="Sismo de prueba M4.5",
            descripcion="Sismo de prueba cerca de Poza Rica",
            latitud=20.53,
            longitud=-97.45,
            magnitud=4.5,
            nivel_alerta="amarillo",
            fecha_evento="2026-09-24T06:00:00Z",
        )
    ]

    # Almacenar con TTL de 2 segundos
    cache.almacenar("test_sismos", datos_prueba, ttl_segundos=2)

    # Verificar que se puede obtener
    resultado = cache.obtener("test_sismos")
    assert resultado is not None, "FALLO: Cache deberia tener datos"
    assert len(resultado) == 1, "FALLO: Cache deberia tener 1 elemento"
    assert resultado[0].tipo == "sismo", "FALLO: Tipo deberia ser 'sismo'"
    print("  [OK] Almacenar y obtener funciona")

    # Esperar a que expire
    time.sleep(2.5)
    resultado_expirado = cache.obtener("test_sismos")
    assert resultado_expirado is None, "FALLO: Cache deberia haber expirado"
    print("  [OK] Expiracion por TTL funciona")

    # Invalidar explicitamente
    cache.almacenar("test_invalidar", datos_prueba, ttl_segundos=60)
    cache.invalidar("test_invalidar")
    assert cache.obtener("test_invalidar") is None, "FALLO: Invalidacion no funciono"
    print("  [OK] Invalidacion explicita funciona")

    # Limpiar expirados
    cache.almacenar("test_exp1", datos_prueba, ttl_segundos=1)
    time.sleep(1.5)
    limpiados = cache.limpiar_expirados()
    assert limpiados >= 1, "FALLO: Deberia haber limpiado al menos 1"
    print(f"  [OK] Limpieza de expirados funciona ({limpiados} limpiados)")

    print("  [RESULTADO] CacheEnMemoria: TODOS LOS TESTS PASARON")
    return True


async def test_proveedor_usgs():
    """Prueba de integracion con la API real de USGS."""
    print("\n--- Test: ProveedorSismosUSGS (API real) ---")
    from app.adaptadores.proveedores.sismos.usgs import ProveedorSismosUSGS

    proveedor = ProveedorSismosUSGS(
        url_base="https://earthquake.usgs.gov/fdsnws/event/1/query"
    )

    assert proveedor.nombre_fuente == "usgs", "FALLO: nombre_fuente deberia ser 'usgs'"

    # Consultar sismos reales (bbox de Mexico)
    bbox_mexico = (-118.0, 14.0, -86.0, 33.0)
    incidencias = await proveedor.obtener_incidencias(bbox=bbox_mexico)

    print(f"  Sismos encontrados: {len(incidencias)}")
    if incidencias:
        primer_sismo = incidencias[0]
        print(f"  Primer sismo: {primer_sismo.titulo}")
        print(f"  Magnitud: {primer_sismo.magnitud}")
        print(f"  Coordenadas: ({primer_sismo.latitud}, {primer_sismo.longitud})")
        print(f"  Alerta: {primer_sismo.nivel_alerta}")
        assert primer_sismo.tipo == "sismo", "FALLO: tipo deberia ser 'sismo'"
        assert primer_sismo.fuente == "usgs", "FALLO: fuente deberia ser 'usgs'"
        assert primer_sismo.latitud is not None, "FALLO: latitud no puede ser None"
        print("  [OK] Estructura de datos correcta")
    else:
        print("  [INFO] No hay sismos recientes en la zona (normal)")

    print("  [RESULTADO] ProveedorSismosUSGS: PASO")
    return True


async def test_proveedor_openmeteo():
    """Prueba de integracion con la API real de Open-Meteo."""
    print("\n--- Test: ProveedorClimaOpenMeteo (API real) ---")
    from app.adaptadores.proveedores.clima.openmeteo import ProveedorClimaOpenMeteo

    proveedor = ProveedorClimaOpenMeteo(url_base="https://api.open-meteo.com/v1")

    assert proveedor.nombre_fuente == "openmeteo", "FALLO: nombre_fuente"

    # Consultar clima para zona de Veracruz
    bbox_veracruz = (-97.5, 20.0, -96.5, 21.0)
    incidencias = await proveedor.obtener_incidencias(bbox=bbox_veracruz)

    print(f"  Alertas climaticas: {len(incidencias)}")
    if incidencias:
        for alerta in incidencias[:3]:
            print(f"  - {alerta.titulo} ({alerta.nivel_alerta})")
    else:
        print("  [INFO] Sin condiciones extremas ahora (esperado en clima normal)")

    print("  [RESULTADO] ProveedorClimaOpenMeteo: PASO")
    return True


async def test_agregador_completo():
    """Prueba de integracion del agregador con todos los proveedores."""
    print("\n--- Test: AgregadorIncidencias (todos los proveedores) ---")
    from app.adaptadores.proveedores.agregador import crear_agregador_default

    agregador = crear_agregador_default()

    # Consultar todas las incidencias
    bbox_mexico = (-100.0, 18.0, -96.0, 23.0)
    resultado = await agregador.obtener_todas(bbox=bbox_mexico)

    assert resultado["type"] == "FeatureCollection", (
        "FALLO: type debe ser FeatureCollection"
    )
    assert isinstance(resultado["total"], int), "FALLO: total debe ser int"
    assert isinstance(resultado["fuentes_consultadas"], list), (
        "FALLO: fuentes debe ser lista"
    )
    assert isinstance(resultado["features"], list), "FALLO: features debe ser lista"

    print(f"  Total incidencias: {resultado['total']}")
    print(f"  Fuentes consultadas: {resultado['fuentes_consultadas']}")
    print(f"  Cache vigente: {resultado['cache_vigente']}")

    # Verificar estructura de cada feature
    for feature in resultado["features"][:3]:
        assert feature["type"] == "Feature", "FALLO: cada feature debe ser tipo Feature"
        assert "geometry" in feature, "FALLO: feature debe tener geometry"
        assert "properties" in feature, "FALLO: feature debe tener properties"
        assert feature["geometry"]["type"] == "Point", "FALLO: geometry debe ser Point"
        coords = feature["geometry"]["coordinates"]
        assert len(coords) == 2, "FALLO: coordenadas deben ser [lon, lat]"
        print(
            f"  Feature: {feature['properties'].get('titulo', 'N/A')} ({feature['properties'].get('tipo', 'N/A')})"
        )

    # Segunda consulta: debe venir del cache
    resultado_cache = await agregador.obtener_todas(bbox=bbox_mexico)
    assert resultado_cache["cache_vigente"] is True, (
        "FALLO: segunda consulta deberia ser cache"
    )
    print("  [OK] Segunda consulta usa cache correctamente")

    print("  [RESULTADO] AgregadorIncidencias: PASO")
    return True


async def test_endpoint_incidencias():
    """Prueba del endpoint HTTP via TestClient."""
    print("\n--- Test: GET /api/v1/publico/mapa/incidencias ---")
    import httpx

    base_url = "http://localhost:8000/api/v1"

    async with httpx.AsyncClient(timeout=30.0) as cliente:
        # Test basico sin filtros
        respuesta = await cliente.get(f"{base_url}/publico/mapa/incidencias")
        print(f"  Status: {respuesta.status_code}")

        if respuesta.status_code == 200:
            datos = respuesta.json()
            assert datos["type"] == "FeatureCollection", "FALLO: type incorrecto"
            assert "total" in datos, "FALLO: falta total"
            assert "fuentes_consultadas" in datos, "FALLO: falta fuentes_consultadas"
            assert "features" in datos, "FALLO: falta features"
            print(f"  Total: {datos['total']}")
            print(f"  Fuentes: {datos['fuentes_consultadas']}")
            print("  [OK] Estructura de respuesta correcta")

            # Test con filtro de tipo
            respuesta_filtrada = await cliente.get(
                f"{base_url}/publico/mapa/incidencias?tipos=sismo"
            )
            datos_filtrados = respuesta_filtrada.json()
            for f in datos_filtrados["features"]:
                assert f["properties"]["tipo"] == "sismo", (
                    "FALLO: filtro de tipo no funciona"
                )
            print(f"  [OK] Filtro por tipo: {datos_filtrados['total']} sismos")

            # Test con bbox
            respuesta_bbox = await cliente.get(
                f"{base_url}/publico/mapa/incidencias?bbox=-98,19,-96,23"
            )
            assert respuesta_bbox.status_code == 200, "FALLO: bbox deberia funcionar"
            print("  [OK] Filtro por bbox funciona")

        else:
            print(f"  [ERROR] Status inesperado: {respuesta.status_code}")
            print(f"  Respuesta: {respuesta.text[:500]}")
            return False

    print("  [RESULTADO] Endpoint incidencias: PASO")
    return True


async def test_contratos_frontend_intactos():
    """Verifica que los contratos existentes NO se han roto."""
    print("\n--- Test: Contratos Frontend INTACTOS ---")
    import httpx

    base_url = "http://localhost:8000/api/v1"

    async with httpx.AsyncClient(timeout=30.0) as cliente:
        # 1. GET /publico/ubicaciones
        r_ubicaciones = await cliente.get(f"{base_url}/publico/ubicaciones")
        assert r_ubicaciones.status_code == 200, (
            f"FALLO: ubicaciones retorno {r_ubicaciones.status_code}"
        )
        datos_ub = r_ubicaciones.json()
        claves_esperadas = {
            "id",
            "type",
            "name",
            "latitude",
            "longitude",
            "address",
            "status",
            "capacity",
            "available",
            "severity",
        }
        if isinstance(datos_ub, list) and len(datos_ub) > 0:
            claves_reales = set(datos_ub[0].keys())
            assert claves_esperadas <= claves_reales, (
                f"FALLO: claves faltantes: {claves_esperadas - claves_reales}"
            )
            print(f"  [OK] /publico/ubicaciones: {len(datos_ub)} POIs, claves intactas")
        else:
            print("  [WARN] /publico/ubicaciones: respuesta vacia o formato inesperado")

        # 2. POST /publico/rutas/segura
        payload_ruta = {"siteId": "", "latitude": 22.2170, "longitude": -97.8728}
        r_ruta = await cliente.post(
            f"{base_url}/publico/rutas/segura", json=payload_ruta
        )
        assert r_ruta.status_code == 200, (
            f"FALLO: rutas/segura retorno {r_ruta.status_code}"
        )
        datos_ruta = r_ruta.json()
        claves_ruta = {
            "routeId",
            "origin",
            "destination",
            "distanceMeters",
            "durationSeconds",
            "geometry",
            "segments",
        }
        claves_reales_ruta = set(datos_ruta.keys())
        assert claves_ruta <= claves_reales_ruta, (
            f"FALLO: claves faltantes: {claves_ruta - claves_reales_ruta}"
        )
        print(
            f"  [OK] /publico/rutas/segura: {len(datos_ruta['geometry'])} puntos, {len(datos_ruta['segments'])} segmentos"
        )

        # 3. POST /login/access-token
        login_data = {
            "username": "admin@proteccioncivil.gob.mx",
            "password": "Admin1234!",
        }
        r_login = await cliente.post(f"{base_url}/login/access-token", data=login_data)
        assert r_login.status_code == 200, f"FALLO: login retorno {r_login.status_code}"
        datos_login = r_login.json()
        assert "access_token" in datos_login, "FALLO: falta access_token"
        assert datos_login["token_type"] == "bearer", "FALLO: token_type incorrecto"
        print("  [OK] /login/access-token: autenticacion funcional")

    print("  [RESULTADO] Contratos Frontend: TODOS INTACTOS")
    return True


async def main():
    """Ejecuta toda la suite de pruebas Fase 2."""
    print("=" * 65)
    print("SUITE DE PRUEBAS FASE 2 - SIGRAS")
    print("APIs de Desastres + Contratos Frontend")
    print("=" * 65)

    resultados = {}
    tests = [
        ("CacheEnMemoria", test_cache_memoria),
        ("ProveedorSismosUSGS", test_proveedor_usgs),
        ("ProveedorClimaOpenMeteo", test_proveedor_openmeteo),
        ("AgregadorIncidencias", test_agregador_completo),
        ("Endpoint /mapa/incidencias", test_endpoint_incidencias),
        ("Contratos Frontend", test_contratos_frontend_intactos),
    ]

    for nombre, test_fn in tests:
        try:
            resultado = await test_fn()
            resultados[nombre] = "PASO" if resultado else "FALLO"
        except Exception as error:
            import traceback

            print(f"\n  [EXCEPCION] {nombre}: {error}")
            traceback.print_exc()
            resultados[nombre] = f"EXCEPCION: {error}"

    # Resumen final
    print("\n" + "=" * 65)
    print("RESUMEN DE RESULTADOS")
    print("=" * 65)
    for nombre, estado in resultados.items():
        indicador = "[OK]" if estado == "PASO" else "[XX]"
        print(f"  {indicador} {nombre}: {estado}")

    total = len(resultados)
    pasaron = sum(1 for v in resultados.values() if v == "PASO")
    print(f"\n  Total: {pasaron}/{total} tests pasaron")
    print("=" * 65)

    return pasaron == total


if __name__ == "__main__":
    exito = asyncio.run(main())
    sys.exit(0 if exito else 1)
