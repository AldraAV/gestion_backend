import httpx

cliente = httpx.Client(timeout=15.0)

print("--- PROBANDO RUTA PARA cc-centro (Plaza de Armas) LOCAL ---")
try:
    r = cliente.post(
        "http://127.0.0.1:8000/api/v1/publico/rutas/segura",
        json={"siteId": "cc-centro", "latitude": 22.2548, "longitude": -97.8487},
    )
    print("Status local:", r.status_code)
    print("Respuesta local:", r.text)
except Exception as e:
    print("Error local:", e)

print("\n--- PROBANDO RUTA PARA cc-centro POR CLOUDFLARE ---")
try:
    r2 = cliente.post(
        "https://regular-studio-tex-removable.trycloudflare.com/api/v1/publico/rutas/segura",
        json={"siteId": "cc-centro", "latitude": 22.2548, "longitude": -97.8487},
    )
    print("Status Cloudflare:", r2.status_code)
    print("Respuesta Cloudflare:", r2.text[:200])
except Exception as e:
    print("Error Cloudflare:", e)
