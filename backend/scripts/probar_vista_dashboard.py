from sqlalchemy import text

from app.core.db import engine

with engine.connect() as conn:
    print("--- PROBANDO CONSULTA A VISTA_DASHBOARD_ALBERGUE ---")
    filas = conn.execute(
        text(
            "SELECT albergue_id, nombre, municipio, semaforo, ocupacion_actual, capacidad_maxima, cupo_disponible, agua_litros_por_persona, raciones_por_persona, total_personal_salud FROM vista_dashboard_albergue"
        )
    ).fetchall()
    for f in filas:
        print(
            f"Albergue: {f[1]} ({f[2]}) | Semaforo: {f[3]} | Ocupacion: {f[4]}/{f[5]} (Disp: {f[6]}) | Agua/persona: {f[7]}L | Comida/persona: {f[8]} | Personal Salud: {f[9]}"
        )

    print("\n--- PROBANDO CONSULTA A REPORTE_CIUDADANO ---")
    rep_cols = [
        r[0]
        for r in conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'reporte_ciudadano'"
            )
        ).fetchall()
    ]
    print("Columnas de reporte_ciudadano:", rep_cols)
