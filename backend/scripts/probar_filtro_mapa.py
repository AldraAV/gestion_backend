import psycopg
from app.core.config import settings

cadena = str(settings.DATABASE_URL).replace("+psycopg", "")
with psycopg.connect(cadena) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT a.folio_identificador, a.nombre, a.latitud, a.longitud, a.direccion, a.tipo_inmueble, a.observaciones,
                   ii.capacidad_maxima, a.ocupacion_actual
            FROM albergue a
            LEFT JOIN inventario_infraestructura ii ON ii.albergue_id = a.id
            WHERE a.latitud IS NOT NULL AND a.longitud IS NOT NULL
            ORDER BY a.nombre
        """)
        filas = cur.fetchall()
        print(f"Total registros con lat/lon en BD: {len(filas)}")

        MOCKS_A_EXCLUIR = {
            "hc-uat",
            "sh-polideportivo",
            "sh-san-lucas",
            "TAM-TAM-002",
            "REF-MAD-001"
        }
        NOMBRES_EXCLUIR = [
            "uat",
            "polideportivo oriente",
            "santo angel",
            "santo ángel",
            "san lucas",
            "españa 1101"
        ]

        albergues_reales = []
        for f in filas:
            folio, nombre, lat, lon, direccion, tipo, obs, cap_max, ocup = f
            folio_norm = str(folio or "").strip()
            nombre_norm = str(nombre or "").lower().strip()
            
            es_mock = (
                folio_norm in MOCKS_A_EXCLUIR 
                or any(m in nombre_norm for m in NOMBRES_EXCLUIR)
            )
            if es_mock:
                print(f"[EXCLUIDO MOCK] {folio_norm} - {nombre}")
            else:
                capacidad = cap_max if cap_max is not None else 100
                ocupacion = ocup if ocup is not None else 0
                disponible = max(0, capacidad - ocupacion)
                albergues_reales.append({
                    "id": folio_norm,
                    "name": nombre,
                    "lat": lat,
                    "lon": lon,
                    "capacity": capacidad,
                    "available": disponible
                })
                print(f"[INCLUIDO REAL] {folio_norm} - {nombre} (Cap: {capacidad}, Disp: {disponible})")

        print(f"\nTOTAL ALBERGUES REALES RESTANTES: {len(albergues_reales)}")
