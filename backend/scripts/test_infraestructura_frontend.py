"""
Pruebas exhaustivas para el contrato Frontend de Infraestructura:
1. GET /api/v1/albergues/{id}/infraestructura -> lista de 9 areas con fechaActualizacion.
2. POST /api/v1/albergues/{id}/infraestructura/{areaId}/ajuste (+1) -> atomicamente suma.
3. POST /api/v1/albergues/{id}/infraestructura/{areaId}/ajuste (-1) -> atomicamente resta.
4. Validacion cota minima: intento de restar cuando cantidad es 0 -> HTTP 422 CANTIDAD_INVALIDA.
5. Validacion lista blanca: area inexistente -> HTTP 404 AREA_NO_ENCONTRADA.
6. Validacion delta = 0 -> HTTP 422 CANTIDAD_INVALIDA.
7. Concurrencia: multiples peticiones atomicas concurrentes.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


async def main():
    import httpx

    base_url = "http://127.0.0.1:8000/api/v1"
    albergue_id = "e552f605-7202-44ac-9e73-8bcbc607be50"  # Polideportivo Oriente

    async with httpx.AsyncClient(timeout=30.0) as cliente:
        print("=" * 70)
        print("TEST: CONTRATO FRONTEND DE INFRAESTRUCTURA (SIGRAS)")
        print("=" * 70)

        # 0. Autenticacion
        print("\n0. Autenticando como Javier (admin Polideportivo)...")
        login_resp = await cliente.post(
            f"{base_url}/login/access-token",
            data={
                "username": "javier@proteccioncivil.gob.mx",
                "password": "Javier1234!",
            },
        )
        assert login_resp.status_code == 200, f"Login fallo: {login_resp.status_code}"
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("   [OK] Token obtenido.")

        # 1. GET Infraestructura
        print("\n1. GET /albergues/{id}/infraestructura...")
        resp_get = await cliente.get(
            f"{base_url}/albergues/{albergue_id}/infraestructura",
            headers=headers,
        )
        assert resp_get.status_code == 200, f"GET fallo: {resp_get.status_code}"
        datos_get = resp_get.json()
        assert "areas" in datos_get, "Falta 'areas' en respuesta"
        assert len(datos_get["areas"]) == 9, (
            f"Se esperaban 9 areas, llegaron {len(datos_get['areas'])}"
        )
        print(
            f"   [OK] 9 areas recibidas correctamente. Ultima actualizacion: {datos_get.get('fechaActualizacion')}"
        )
        for a in datos_get["areas"]:
            print(f"        - {a['id']}: '{a['nombre']}' = {a['cantidad']}")

        # Encontrar cantidad inicial de dormitorios
        dormitorios_inicial = next(
            a["cantidad"] for a in datos_get["areas"] if a["id"] == "dormitorios"
        )

        # 2. POST Ajuste +1
        print(
            f"\n2. POST ajuste (+1) a 'dormitorios' (inicial: {dormitorios_inicial})..."
        )
        resp_mas_uno = await cliente.post(
            f"{base_url}/albergues/{albergue_id}/infraestructura/dormitorios/ajuste",
            json={"delta": 1},
            headers=headers,
        )
        assert resp_mas_uno.status_code == 200, (
            f"Ajuste +1 fallo: {resp_mas_uno.status_code}"
        )
        datos_mas_uno = resp_mas_uno.json()
        assert datos_mas_uno["success"] is True
        assert datos_mas_uno["area"]["cantidad"] == dormitorios_inicial + 1
        print(
            f"   [OK] Incremento exitoso: {datos_mas_uno['area']['nombre']} -> {datos_mas_uno['area']['cantidad']}"
        )

        # 3. POST Ajuste -1
        print("\n3. POST ajuste (-1) a 'dormitorios'...")
        resp_menos_uno = await cliente.post(
            f"{base_url}/albergues/{albergue_id}/infraestructura/dormitorios/ajuste",
            json={"delta": -1},
            headers=headers,
        )
        assert resp_menos_uno.status_code == 200, (
            f"Ajuste -1 fallo: {resp_menos_uno.status_code}"
        )
        datos_menos_uno = resp_menos_uno.json()
        assert datos_menos_uno["area"]["cantidad"] == dormitorios_inicial
        print(
            f"   [OK] Decremento exitoso: {datos_menos_uno['area']['nombre']} -> {datos_menos_uno['area']['cantidad']}"
        )

        # 4. Validacion Cota Minima (< 0)
        # Vamos a intentar decrementar con un delta muy negativo que sobrepase la cantidad
        cantidad_actual = datos_menos_uno["area"]["cantidad"]
        delta_invalido = -(cantidad_actual + 10)
        print(
            f"\n4. Probando cota minima (cantidad actual: {cantidad_actual}, delta: {delta_invalido})..."
        )
        resp_cota = await cliente.post(
            f"{base_url}/albergues/{albergue_id}/infraestructura/dormitorios/ajuste",
            json={"delta": delta_invalido},
            headers=headers,
        )
        assert resp_cota.status_code == 422, (
            f"Se esperaba 422, se recibio {resp_cota.status_code}"
        )
        datos_cota = resp_cota.json()
        assert datos_cota.get("code") == "CANTIDAD_INVALIDA", (
            f"Codigo erroneo: {datos_cota}"
        )
        assert "area" in datos_cota, "Falta 'area' en body de error 422"
        assert datos_cota["area"]["cantidad"] == cantidad_actual
        print(
            f"   [OK] Rechazo correcto (HTTP 422 CANTIDAD_INVALIDA). Area actual devuelta: {datos_cota['area']}"
        )

        # 5. Validacion Lista Blanca (Area Inexistente)
        print("\n5. Probando inyeccion / area inexistente ('alberca_olimpica')...")
        resp_404 = await cliente.post(
            f"{base_url}/albergues/{albergue_id}/infraestructura/alberca_olimpica/ajuste",
            json={"delta": 1},
            headers=headers,
        )
        assert resp_404.status_code == 404, (
            f"Se esperaba 404, llego {resp_404.status_code}"
        )
        datos_404 = resp_404.json()
        assert datos_404.get("code") == "AREA_NO_ENCONTRADA"
        print(f"   [OK] Rechazo correcto (HTTP 404 AREA_NO_ENCONTRADA): {datos_404}")

        # 6. Validacion delta = 0
        print("\n6. Probando delta = 0...")
        resp_delta_cero = await cliente.post(
            f"{base_url}/albergues/{albergue_id}/infraestructura/dormitorios/ajuste",
            json={"delta": 0},
            headers=headers,
        )
        assert resp_delta_cero.status_code == 422, (
            f"Se esperaba 422, llego {resp_delta_cero.status_code}"
        )
        datos_cero = resp_delta_cero.json()
        assert datos_cero.get("code") == "CANTIDAD_INVALIDA"
        print(f"   [OK] Rechazo correcto para delta=0 (HTTP 422): {datos_cero}")

        # 7. Concurrencia de 5 peticiones simultaneas (+1 cada una)
        print("\n7. Probando 5 ajustes concurrentes (+1 cada una) a 'regaderas'...")
        regaderas_inicial = next(
            a["cantidad"] for a in datos_get["areas"] if a["id"] == "regaderas"
        )

        tareas = [
            cliente.post(
                f"{base_url}/albergues/{albergue_id}/infraestructura/regaderas/ajuste",
                json={"delta": 1},
                headers=headers,
            )
            for _ in range(5)
        ]
        respuestas_concurrencia = await asyncio.gather(*tareas)
        for r in respuestas_concurrencia:
            assert r.status_code == 200, (
                f"Peticion concurrente fallo con {r.status_code}"
            )

        # Comprobar valor final
        resp_final = await cliente.get(
            f"{base_url}/albergues/{albergue_id}/infraestructura",
            headers=headers,
        )
        regaderas_final = next(
            a["cantidad"] for a in resp_final.json()["areas"] if a["id"] == "regaderas"
        )
        assert regaderas_final == regaderas_inicial + 5, (
            f"Esperado {regaderas_inicial + 5}, obtenido {regaderas_final}"
        )
        print(
            f"   [OK] Concurrencia atomica perfecta: {regaderas_inicial} + 5 = {regaderas_final}"
        )

        # Revertir
        await cliente.post(
            f"{base_url}/albergues/{albergue_id}/infraestructura/regaderas/ajuste",
            json={"delta": -5},
            headers=headers,
        )

        print("\n" + "=" * 70)
        print("CONTRATO FRONTEND DE INFRAESTRUCTURA VALIDADO AL 100%")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
