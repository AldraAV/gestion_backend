import json

with open("schema_inspeccion.json", encoding="utf-8") as f:
    datos = json.load(f)

print(f"Total tablas: {len(datos)}")
for nombre_tabla, info in datos.items():
    print(f"\n--- TABLA: {nombre_tabla} (Filas: {info['filas_totales']}) ---")
    print(f"  PK: {info['primary_key']}")
    print(f"  FKs: {info['foreign_keys']}")
    print("  Columnas:")
    for col in info["columnas"]:
        pk_str = " [PK]" if col["nombre"] in info["primary_key"] else ""
        fk_str = ""
        for fk in info["foreign_keys"]:
            if col["nombre"] in fk["columna_origen"]:
                fk_str = f" [FK -> {fk['tabla_destino']}.{fk['columna_destino']}]"
        print(
            f"    - {col['nombre']}: {col['tipo']} | Nullable: {col['nullable']}{pk_str}{fk_str}"
        )
