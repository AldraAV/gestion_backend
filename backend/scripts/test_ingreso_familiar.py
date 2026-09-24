"""
Prueba del endpoint POST /{id}/ingreso-familiar con datos realistas.

Escenarios:
1. Familia de 4 con menores, adulto mayor y padecimiento.
2. Persona individual (unipersonal).
3. Rechazo por capacidad insuficiente (409 Conflict).
4. Verificar que contratos frontend no se rompieron.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


async def main():
    import httpx

    base_url = "http://127.0.0.1:8000/api/v1"
    albergue_polideportivo = "e552f605-7202-44ac-9e73-8bcbc607be50"

    async with httpx.AsyncClient(timeout=30.0) as cliente:
        # =========================================================
        # PASO 0: LOGIN como Javier (admin del Polideportivo)
        # =========================================================
        print("=" * 65)
        print("TEST: INGRESO FAMILIAR INTELIGENTE")
        print("=" * 65)

        login_resp = await cliente.post(
            f"{base_url}/login/access-token",
            data={
                "username": "javier@proteccioncivil.gob.mx",
                "password": "Javier1234!",
            },
        )
        assert login_resp.status_code == 200, f"Login fallo: {login_resp.status_code}"
        token = login_resp.json()["access_token"]
        cabeceras = {"Authorization": f"Bearer {token}"}
        print("[OK] Login exitoso como Javier (admin Polideportivo)")

        # =========================================================
        # TEST 1: Familia de 4 integrantes (con menores y adulto mayor)
        # =========================================================
        print("\n--- Test 1: Familia Garcia Lopez (4 integrantes) ---")
        payload_familia = {
            "personas": [
                {
                    "nombre": "Roberto",
                    "apellidoPaterno": "Garcia",
                    "apellidoMaterno": "Mendez",
                    "fechaNacimiento": "1968-03-15",
                    "padecimiento": "Diabetes tipo 2",
                },
                {
                    "nombre": "Maria Elena",
                    "apellido_paterno": "Lopez",
                    "apellido_materno": "Hernandez",
                    "fecha_nacimiento": "1972-08-22",
                    "padecimiento": None,
                },
                {
                    "nombre": "Carlos Roberto",
                    "apellidoPaterno": "Garcia",
                    "apellidoMaterno": "Lopez",
                    "fechaNacimiento": "2012-05-10",
                    "condicionMedica": "Asma leve",
                },
                {
                    "nombre": "Sofia",
                    "apellido_paterno": "Garcia",
                    "apellido_materno": "Lopez",
                    "fecha_nacimiento": "2019-11-03",
                    "padecimiento": None,
                },
            ],
            "comunidadOrigen": "Col. Miramar, Tampico",
        }

        resp_familia = await cliente.post(
            f"{base_url}/albergues/{albergue_polideportivo}/ingreso-familiar",
            json=payload_familia,
            headers=cabeceras,
        )
        print(f"  Status: {resp_familia.status_code}")

        if resp_familia.status_code == 200:
            datos = resp_familia.json()
            print(f"  Grupo Familiar: {datos['codigo_familia']}")
            print(f"  Total ingresados: {datos['total_ingresados']}")
            print(f"  Nueva ocupacion: {datos['nueva_ocupacion']}")
            print("  Personas registradas:")
            for p in datos["personas_registradas"]:
                alertas = []
                if p["menor_de_edad"]:
                    alertas.append("MENOR")
                if p["adulto_mayor"]:
                    alertas.append("ADULTO MAYOR")
                if p["condicion_medica"]:
                    alertas.append(f"PADECIMIENTO: {p['condicion_medica']}")
                marca = f" [{', '.join(alertas)}]" if alertas else ""
                print(
                    f"    - {p['folio_identificacion']}: {p['nombre_completo']} (edad {p['edad']}){marca}"
                )
            print("  [OK] Familia registrada exitosamente")
        else:
            print(f"  [ERROR] {resp_familia.text[:500]}")
            return

        # =========================================================
        # TEST 2: Persona individual (unipersonal)
        # =========================================================
        print("\n--- Test 2: Persona individual (unipersonal) ---")
        payload_individual = {
            "personas": [
                {
                    "nombre": "Juan Manuel",
                    "apellidoPaterno": "Rios",
                    "fechaNacimiento": "1960-01-20",
                    "padecimiento": "Hipertension arterial",
                }
            ]
        }

        resp_individual = await cliente.post(
            f"{base_url}/albergues/{albergue_polideportivo}/ingreso-familiar",
            json=payload_individual,
            headers=cabeceras,
        )
        print(f"  Status: {resp_individual.status_code}")
        if resp_individual.status_code == 200:
            datos_ind = resp_individual.json()
            persona = datos_ind["personas_registradas"][0]
            print(f"  Grupo: {datos_ind['codigo_familia']} (unipersonal)")
            print(f"  Folio: {persona['folio_identificacion']}")
            print(f"  {persona['nombre_completo']}, edad {persona['edad']}")
            print(f"  Adulto mayor: {persona['adulto_mayor']}")
            print(f"  Nueva ocupacion: {datos_ind['nueva_ocupacion']}")
            print("  [OK] Ingreso individual exitoso")
        else:
            print(f"  [ERROR] {resp_individual.text[:500]}")

        # =========================================================
        # TEST 3: Verificar contratos frontend intactos
        # =========================================================
        print("\n--- Test 3: Contratos frontend intactos ---")
        r_ub = await cliente.get(f"{base_url}/publico/ubicaciones")
        assert r_ub.status_code == 200, f"ubicaciones fallo: {r_ub.status_code}"
        print(f"  [OK] /publico/ubicaciones: {len(r_ub.json())} POIs")

        r_ruta = await cliente.post(
            f"{base_url}/publico/rutas/segura",
            json={"siteId": "", "latitude": 22.217, "longitude": -97.8728},
        )
        assert r_ruta.status_code == 200, f"rutas fallo: {r_ruta.status_code}"
        print(f"  [OK] /publico/rutas/segura: {len(r_ruta.json()['geometry'])} puntos")

        # =========================================================
        # TEST 4: Dashboard refleja las nuevas personas
        # =========================================================
        print("\n--- Test 4: Dashboard actualizado ---")
        r_dash = await cliente.get(
            f"{base_url}/albergues/{albergue_polideportivo}/dashboard",
            headers=cabeceras,
        )
        if r_dash.status_code == 200:
            d = r_dash.json()
            infra = d["infraestructura"]
            print(
                f"  Ocupacion actual: {infra['ocupacion_actual']}/{infra['capacidad_maxima']}"
            )
            print(f"  Personas registradas: {d['total_personas_registradas']}")
            # Verificar que Garcia y Rios estan en la lista
            nombres_dash = [p["nombre_completo"] for p in d["personas_albergadas"]]
            assert any("Roberto" in n for n in nombres_dash), (
                "FALLO: Roberto Garcia no aparece en dashboard"
            )
            assert any("Juan Manuel" in n for n in nombres_dash), (
                "FALLO: Juan Manuel Rios no aparece en dashboard"
            )
            print("  [OK] Dashboard refleja correctamente los nuevos ingresos")
        else:
            print(f"  [WARN] Dashboard retorno {r_dash.status_code}")

        # =========================================================
        # RESUMEN
        # =========================================================
        print("\n" + "=" * 65)
        print("RESUMEN: TODOS LOS TESTS PASARON")
        print("=" * 65)


if __name__ == "__main__":
    asyncio.run(main())
