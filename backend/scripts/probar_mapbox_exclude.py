import asyncio
import httpx
import os
from app.core.config import settings

token = settings.MAPBOX_ACCESS_TOKEN or os.getenv("MAPBOX_ACCESS_TOKEN", "")

async def test_mapbox_exclude():
    # Coordenadas Tampico
    origen = "-97.8728,22.2170"
    destino = "-97.8384,22.2585"
    
    # 1. Ruta sin exclude
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{origen};{destino}"
    params_normal = {
        "geometries": "geojson",
        "steps": "true",
        "access_token": token
    }
    async with httpx.AsyncClient() as client:
        r1 = await client.get(url, params=params_normal)
        print("NORMAL STATUS:", r1.status_code)
        if r1.status_code == 200:
            print("NORMAL DISTANCE:", r1.json()["routes"][0]["distance"])

        # 2. Ruta con exclude=point(lon lat)
        # Bloqueo en Moctezuma: lat 22.2378, lon -97.8652
        params_exclude = {
            "geometries": "geojson",
            "steps": "true",
            "exclude": "point(-97.8652 22.2378)",
            "access_token": token
        }
        r2 = await client.get(url, params=params_exclude)
        print("EXCLUDE STATUS:", r2.status_code)
        if r2.status_code == 200:
            print("EXCLUDE DISTANCE:", r2.json()["routes"][0]["distance"])
            print("Exitosamente esquivado via Mapbox!")
        else:
            print("EXCLUDE ERROR:", r2.text)

        # 3. Probar multiples puntos
        params_multi = {
            "geometries": "geojson",
            "steps": "true",
            "exclude": "point(-97.8652 22.2378),point(-97.8437 22.2295)",
            "access_token": token
        }
        r3 = await client.get(url, params=params_multi)
        print("MULTI EXCLUDE STATUS:", r3.status_code)
        if r3.status_code == 200:
            print("MULTI DISTANCE:", r3.json()["routes"][0]["distance"])
            print("Multiples puntos esquivados con exito!")
        else:
            print("MULTI ERROR:", r3.text)

asyncio.run(test_mapbox_exclude())
