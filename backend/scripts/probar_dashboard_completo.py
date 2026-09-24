import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"
POLIDEPORTIVO_ID = "e552f605-7202-44ac-9e73-8bcbc607be50"
SAN_LUCAS_ID = "b6d10286-864c-4b48-9e1d-b80a72950ff6"


def obtener_token(correo, contrasena):
    res = requests.post(
        f"{BASE_URL}/login/access-token",
        data={"username": correo, "password": contrasena},
    )
    if res.status_code != 200:
        raise Exception(f"Fallo login para {correo}: {res.status_code} - {res.text}")
    return res.json()["access_token"]


def probar():
    print("=== INICIANDO BATERIA DE PRUEBAS DEL DASHBOARD Y ATOMICIDAD ===")

    print("\n1. Autenticando usuarios de prueba...")
    token_javier = obtener_token("javier@proteccioncivil.gob.mx", "Javier1234!")
    print("   [OK] Token obtenido para Javier (Administrador de Albergue)")

    token_logistica = obtener_token(
        "logistica@proteccioncivil.gob.mx", "Logistica1234!"
    )
    print("   [OK] Token obtenido para Operador de Logistica (Personal Operativo)")

    token_admin = obtener_token("admin@proteccioncivil.gob.mx", "Admin1234!")
    print("   [OK] Token obtenido para Administrador General (Coordinador)")

    headers_javier = {"Authorization": f"Bearer {token_javier}"}
    headers_logistica = {"Authorization": f"Bearer {token_logistica}"}
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    print(
        "\n2. Probando GET /admin/albergues/{id}/dashboard con Javier (Admin de este albergue)..."
    )
    res = requests.get(
        f"{BASE_URL}/admin/albergues/{POLIDEPORTIVO_ID}/dashboard",
        headers=headers_javier,
    )
    print(f"   Status Code: {res.status_code}")
    assert res.status_code == 200, f"Error: {res.text}"
    data = res.json()
    print(f"   Albergue: {data['nombre']} ({data['municipio']})")
    print(f"   Semaforo: {data['semaforo']}")
    print(
        f"   Ocupacion: {data['infraestructura']['ocupacion_actual']} / {data['infraestructura']['capacidad_maxima']} (Disp: {data['infraestructura']['cupo_disponible']})"
    )
    print(f"   Agua por persona: {data['suministros']['agua_litros_por_persona']} L")
    print(f"   Raciones por persona: {data['suministros']['raciones_por_persona']}")
    print(
        f"   Extintores instalados (fijos): {data['infraestructura']['extintores_instalados']}"
    )
    print(
        f"   Extintores en reserva (bodega): {data['suministros']['extintores_reserva']}"
    )
    print(f"   Total personal salud: {data['recurso_humano']['total_personal_salud']}")
    print(f"   Total refugiados en lista: {data['total_personas_registradas']}")

    # Validar visibilidad medica para Javier
    refugiados_por_folio = {
        p["folio_identificacion"]: p for p in data["personas_albergadas"]
    }
    maria_elena = refugiados_por_folio["REF-TAM-001"]
    print(
        f"   Refugiada Maria Elena (Javier): {maria_elena['nombre_completo']} | Condicion Medica: {maria_elena['condicion_medica']}"
    )
    assert maria_elena["condicion_medica"] == "Hipertension arterial y asma moderada", (
        "Javier DEBE ver la condicion medica de Maria Elena"
    )
    print(
        "   [OK] Javier puede ver condiciones medicas por ser Administrador de Albergue."
    )

    print("\n3. Probando privacidad medica con Operador de Logistica...")
    res_log = requests.get(
        f"{BASE_URL}/admin/albergues/{POLIDEPORTIVO_ID}/dashboard",
        headers=headers_logistica,
    )
    assert res_log.status_code == 200
    data_log = res_log.json()
    refugiados_log_por_folio = {
        p["folio_identificacion"]: p for p in data_log["personas_albergadas"]
    }
    maria_elena_log = refugiados_log_por_folio["REF-TAM-001"]
    print(
        f"   Refugiada Maria Elena (Logistica): {maria_elena_log['nombre_completo']} | Condicion Medica: {maria_elena_log['condicion_medica']}"
    )
    assert maria_elena_log["condicion_medica"] is None, (
        "Logistica NO DEBE ver condicion medica"
    )
    assert maria_elena_log["discapacidad"] is None, "Logistica NO DEBE ver discapacidad"
    assert maria_elena_log["necesidad_especial"] is None, (
        "Logistica NO DEBE ver necesidad especial"
    )
    print(
        "   [OK] Datos sensibles excluidos exitosamente para personal no medico / no administrador."
    )

    print("\n4. Probando restriccion de alcance_id (Javier intenta ver San Lucas)...")
    res_bloqueo = requests.get(
        f"{BASE_URL}/admin/albergues/{SAN_LUCAS_ID}/dashboard", headers=headers_javier
    )
    print(f"   Status Code: {res_bloqueo.status_code} (Esperado 403)")
    assert res_bloqueo.status_code == 403, (
        f"Esperado 403 pero recibio {res_bloqueo.status_code}"
    )
    print(f"   Detalle: {res_bloqueo.json()['detail']}")
    print("   [OK] Restriccion por alcance_id validada exitosamente.")

    print(
        "\n5. Probando vista multi-albergue con Coordinador General (Admin ve San Lucas)..."
    )
    res_admin_sl = requests.get(
        f"{BASE_URL}/admin/albergues/{SAN_LUCAS_ID}/dashboard", headers=headers_admin
    )
    print(f"   Status Code: {res_admin_sl.status_code} (Esperado 200)")
    assert res_admin_sl.status_code == 200
    print(f"   Coordinador consulto: {res_admin_sl.json()['nombre']}")
    print("   [OK] Coordinador General tiene acceso multi-albergue confirmado.")

    print("\n6. Probando Ingreso Atomico...")
    res_ingreso = requests.post(
        f"{BASE_URL}/admin/albergues/{POLIDEPORTIVO_ID}/ingreso-atomico",
        headers=headers_javier,
    )
    assert res_ingreso.status_code == 200
    nueva_ocupacion = res_ingreso.json()["nueva_ocupacion_actual"]
    print(f"   Ingreso registrado. Nueva ocupacion: {nueva_ocupacion}")
    assert nueva_ocupacion == 4, f"Esperado 4 pero fue {nueva_ocupacion}"

    print("\n7. Probando Egreso Atomico...")
    res_egreso = requests.post(
        f"{BASE_URL}/admin/albergues/{POLIDEPORTIVO_ID}/egreso-atomico",
        headers=headers_javier,
    )
    assert res_egreso.status_code == 200
    ocupacion_tras_egreso = res_egreso.json()["nueva_ocupacion_actual"]
    print(f"   Egreso registrado. Nueva ocupacion: {ocupacion_tras_egreso}")
    assert ocupacion_tras_egreso == 3, f"Esperado 3 pero fue {ocupacion_tras_egreso}"

    print("\n=== TODAS LAS PRUEBAS FINALIZARON EXITOSAMENTE (100% BLINDADO) ===")


if __name__ == "__main__":
    probar()
