"""Script para compilar el DDL exacto en dialecto PostgreSQL de las nuevas tablas
de Albergue, Inventarios, Roles y Refugiados para Supabase.
"""

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

from app.models import SQLModel


def compilar_ddl_postgresql() -> str:
    nombres_tablas = [
        "albergue",
        "albergue_usuario",
        "grupo_familiar",
        "persona_refugiada",
        "inventario_suministro",
        "inventario_infraestructura",
        "inventario_recurso_humano",
    ]

    sentencias = [
        "-- ============================================================================",
        "-- MIGRACION DDL PARA SUPABASE (POSTGRESQL)",
        "-- PROYECTO: HACKATEC 2026 - PROTECCION CIVIL Y GESTION DE RIESGOS",
        "-- ============================================================================",
        "",
        "-- 1. Extensiones necesarias",
        'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";',
        'CREATE EXTENSION IF NOT EXISTS "pgcrypto";',
        "",
        "-- 2. Creacion de tipos ENUM de PostgreSQL si no existen",
        "DO $$ BEGIN",
        "    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'roloperativo') THEN",
        "        CREATE TYPE roloperativo AS ENUM ('administrador_albergue', 'responsable_area', 'personal_operativo');",
        "    END IF;",
        "    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'areafuncional') THEN",
        "        CREATE TYPE areafuncional AS ENUM ('recepcion_registro', 'alojamiento', 'bodega_suministros', 'salud_medica', 'alimentacion', 'seguridad', 'psicologia', 'limpieza_mantenimiento', 'general');",
        "    END IF;",
        "    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estadoestancia') THEN",
        "        CREATE TYPE estadoestancia AS ENUM ('albergado', 'salida_temporal', 'egreso_definitivo', 'trasladado');",
        "    END IF;",
        "    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estadooperativoalbergue') THEN",
        "        CREATE TYPE estadooperativoalbergue AS ENUM ('planeado', 'disponible', 'activado', 'lleno', 'cerrado', 'fuera_de_servicio');",
        "    END IF;",
        "END $$;",
        "",
        "-- 3. Creacion de Tablas e Indices",
        "",
    ]

    for nombre in nombres_tablas:
        tabla = SQLModel.metadata.tables[nombre]
        sentencia_crear = str(
            CreateTable(tabla).compile(dialect=postgresql.dialect())
        ).strip()
        sentencias.append(f"-- Tabla: {nombre}")
        sentencias.append(sentencia_crear + ";\n")

        # Indices de la tabla
        for indice in tabla.indexes:
            sentencia_indice = str(
                CreateIndex(indice).compile(dialect=postgresql.dialect())
            ).strip()
            sentencias.append(sentencia_indice + ";")
        sentencias.append("")

    return "\n".join(sentencias)


if __name__ == "__main__":
    ddl = compilar_ddl_postgresql()
    with open("scripts/migracion_supabase.sql", "w", encoding="utf-8") as f:
        f.write(ddl)
    print("DDL generado exitosamente en scripts/migracion_supabase.sql")
