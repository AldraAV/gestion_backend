import urllib.request
import json

url = "https://broadcasting-pdf-men-closer.trycloudflare.com/api/v1/publico/ubicaciones"
with urllib.request.urlopen(url) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    print(f"TOTAL UBICACIONES PUBLICAS: {len(data)}")
    for d in data:
        print(f"[{d['type'].upper():<17}] {d['id']:<15} | {d['name']:<45} | Cap: {d.get('capacity')} | Disp: {d.get('available')}")

    # Validacion estricta
    prohibidos = ["uat", "polideportivo", "santo angel", "santo ángel", "san lucas"]
    for d in data:
        for p in prohibidos:
            assert p not in d["name"].lower(), f"Encontrado {p} en {d['name']}"

    print("\nVERIFICACION EXITOSA: Ningun mock en el mapa publico!")
