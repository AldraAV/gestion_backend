import json

from sqlalchemy import inspect, text

from app.core.db import engine


def inspeccionar():
    inspector = inspect(engine)
    tablas = inspector.get_table_names(schema="public")
    print(f"Total de tablas encontradas: {len(tablas)}")

    resultado = {}
    with engine.connect() as conn:
        for tabla in sorted(tablas):
            columnas = inspector.get_columns(tabla, schema="public")
            pk = inspector.get_pk_constraint(tabla, schema="public")
            fks = inspector.get_foreign_keys(tabla, schema="public")
            uniques = inspector.get_unique_constraints(tabla, schema="public")
            indexes = inspector.get_indexes(tabla, schema="public")

            try:
                conteo = conn.execute(text(f'SELECT COUNT(*) FROM "{tabla}"')).scalar()
            except Exception as e:
                conteo = f"Error: {e}"

            resultado[tabla] = {
                "filas_totales": conteo,
                "primary_key": pk.get("constrained_columns", []) if pk else [],
                "foreign_keys": [
                    {
                        "columna_origen": fk.get("constrained_columns", []),
                        "tabla_destino": fk.get("referred_table"),
                        "columna_destino": fk.get("referred_columns", []),
                    }
                    for fk in fks
                ],
                "columnas": [
                    {
                        "nombre": c["name"],
                        "tipo": str(c["type"]),
                        "nullable": c["nullable"],
                        "default": str(c.get("default"))
                        if c.get("default") is not None
                        else None,
                    }
                    for c in columnas
                ],
                "unique_constraints": uniques,
                "indexes": [
                    {
                        "nombre": idx.get("name"),
                        "columnas": idx.get("column_names"),
                        "unique": idx.get("unique"),
                    }
                    for idx in indexes
                ],
            }

    ruta_salida = "schema_inspeccion.json"
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, default=str)
    print(f"Esquema exportado exitosamente a {ruta_salida}")


if __name__ == "__main__":
    inspeccionar()
