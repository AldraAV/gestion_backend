import httpx

cliente = httpx.Client(timeout=10.0)

print("--- PROBANDO GET /api/v1/publico/ubicaciones ---")
r1 = cliente.get("http://127.0.0.1:8000/api/v1/publico/ubicaciones")
print("Status r1:", r1.status_code)
datos1 = r1.json()
print("Cantidad de ubicaciones:", len(datos1))
for u in datos1:
    print(
        f"  Punto: [{u.get('type')}] {u.get('id')} - {u.get('name')} ({u.get('latitude')}, {u.get('longitude')})"
    )

print("\n--- PROBANDO GET /publico/ubicaciones ---")
r2 = cliente.get("http://127.0.0.1:8000/publico/ubicaciones")
print("Status r2:", r2.status_code)

print("\n--- PROBANDO POST /publico/rutas/segura ---")
r3 = cliente.post(
    "http://127.0.0.1:8000/publico/rutas/segura",
    json={"siteId": "sh-polideportivo", "latitude": 22.2548, "longitude": -97.8487},
)
print("Status r3:", r3.status_code)
if r3.status_code == 200:
    res = r3.json()
    print("Destino resuelto:", res.get("destination"))
    print("Distancia metros:", res.get("distanceMeters"))
    print("Puntos en geometria:", len(res.get("geometry", [])))
