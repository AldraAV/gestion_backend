from sqlalchemy import text

from app.core.db import engine

with engine.connect() as conn:
    print("--- TIPOS DE COLUMNAS ACTUALES EN POSTGRESQL ---")
    filas = conn.execute(
        text("""
        SELECT table_name, column_name, udt_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name IN ('albergue', 'persona_refugiada', 'albergue_usuario', 'inventario_infraestructura', 'inventario_suministro')
          AND column_name IN ('estado_operativo', 'estado_estancia', 'rol', 'area', 'extintores', 'ocupacion_actual')
        ORDER BY table_name, column_name;
    """)
    ).fetchall()
    for f in filas:
        print(f"Tabla: {f[0]} | Columna: {f[1]} | udt_name: {f[2]} | data_type: {f[3]}")

    print("\n--- ENUMS NATIVOS EXISTENTES EN POSTGRESQL ---")
    enums = conn.execute(
        text("""
        SELECT t.typname, e.enumlabel
        FROM pg_type t
        JOIN pg_enum e ON t.oid = e.enumtypid
        JOIN pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname = 'public'
        ORDER BY t.typname, e.enumsortorder;
    """)
    ).fetchall()

    enums_agrupados = {}
    for e in enums:
        enums_agrupados.setdefault(e[0], []).append(e[1])
    for nombre, valores in enums_agrupados.items():
        print(f"ENUM {nombre}: {valores}")
