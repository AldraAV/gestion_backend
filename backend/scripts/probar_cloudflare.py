import httpx

cliente = httpx.Client(timeout=15.0)
url = "https://regular-studio-tex-removable.trycloudflare.com"

print("1. Probando Ubicaciones en Cloudflare...")
r1 = cliente.get(f"{url}/api/v1/publico/ubicaciones")
print("Status Ubicaciones:", r1.status_code, "Items:", len(r1.json()))

print("2. Probando Ruta Segura en Cloudflare...")
r2 = cliente.post(
    f"{url}/api/v1/publico/rutas/segura",
    json={"siteId": "sh-polideportivo", "latitude": 22.2548, "longitude": -97.8487},
)
print("Status Ruta:", r2.status_code)
if r2.status_code == 200:
    print("Destino:", r2.json().get("destination", {}).get("name"))
