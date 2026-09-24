from app.api.routes.ubicaciones import consultar_ubicaciones_base_datos

ubicaciones = consultar_ubicaciones_base_datos()
print(f"Total ubicaciones retornadas: {len(ubicaciones)}")

albergues = [u for u in ubicaciones if u.get("type") == "shelter"]
centros = [u for u in ubicaciones if u.get("type") == "collection_center"]
bloqueos = [u for u in ubicaciones if u.get("type") == "road_block"]

print(f"Albergues: {len(albergues)}")
print(f"Centros de acopio: {len(centros)}")
print(f"Bloqueos viales: {len(bloqueos)}")

print("\n--- LISTA DE ALBERGUES EN EL MAPA ---")
for a in albergues:
    print(f"ID: {a['id']:<15} | Nombre: {a['name']:<45} | Cap: {a['capacity']:<4} | Disp: {a['available']:<4} | Lat: {a['latitude']:.4f}, Lon: {a['longitude']:.4f}")

# Validacion de no existencia de mocks
nombres_prohibidos = ["uat", "polideportivo", "santo angel", "santo ángel", "san lucas"]
for a in albergues:
    nom_lower = a["name"].lower()
    for p in nombres_prohibidos:
        assert p not in nom_lower, f"ERROR: Se encontro mock {p} en {a['name']}"

print("\nTODAS LAS VALIDACIONES PASARON: CERO MOCKS DETECTADOS!")
