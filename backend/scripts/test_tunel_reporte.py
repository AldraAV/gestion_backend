import httpx
import json

url_tunel = "https://kits-amended-hartford-hollywood.trycloudflare.com/api/v1/publico/reportes"

datos = {
    "descripcion": "Reporte de prueba en vivo: Arbol cayo sobre cable de alta tension y bloqueo la calle Altamira en Tampico.",
    "latitud": "22.250",
    "longitud": "-97.865",
    "nivel_prioridad": "alta"
}

jpeg_minimo = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9"

archivos = {
    "archivo": ("foto_arbol.jpg", jpeg_minimo, "image/jpeg")
}

try:
    with httpx.Client(timeout=25.0) as cliente:
        resp = cliente.post(url_tunel, data=datos, files=archivos)
        print("Status HTTP:", resp.status_code)
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print("Error:", e)
