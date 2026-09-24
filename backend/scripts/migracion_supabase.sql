-- ============================================================================
-- MIGRACION DDL PARA SUPABASE (POSTGRESQL)
-- PROYECTO: HACKATEC 2026 - PROTECCION CIVIL Y GESTION DE RIESGOS
-- ============================================================================

-- 1. Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Creacion de tipos ENUM de PostgreSQL si no existen
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'roloperativo') THEN
        CREATE TYPE roloperativo AS ENUM ('administrador_albergue', 'responsable_area', 'personal_operativo');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'areafuncional') THEN
        CREATE TYPE areafuncional AS ENUM ('recepcion_registro', 'alojamiento', 'bodega_suministros', 'salud_medica', 'alimentacion', 'seguridad', 'psicologia', 'limpieza_mantenimiento', 'general');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estadoestancia') THEN
        CREATE TYPE estadoestancia AS ENUM ('albergado', 'salida_temporal', 'egreso_definitivo', 'trasladado');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estadooperativoalbergue') THEN
        CREATE TYPE estadooperativoalbergue AS ENUM ('planeado', 'disponible', 'activado', 'lleno', 'cerrado', 'fuera_de_servicio');
    END IF;
END $$;

-- 3. Creacion de Tablas e Indices

-- Tabla: albergue
CREATE TABLE albergue (
	folio_identificador VARCHAR(50) NOT NULL, 
	nombre VARCHAR(255) NOT NULL, 
	direccion VARCHAR(500) NOT NULL, 
	municipio VARCHAR(150) NOT NULL, 
	localidad VARCHAR(150), 
	estado_republica VARCHAR(100) NOT NULL, 
	latitud FLOAT, 
	longitud FLOAT, 
	tipo_inmueble VARCHAR(100), 
	telefono_contacto VARCHAR(50), 
	admite_mascotas BOOLEAN NOT NULL, 
	estado_operativo estadooperativoalbergue NOT NULL, 
	observaciones VARCHAR(1000), 
	id UUID NOT NULL, 
	responsable_id UUID, 
	fecha_registro TIMESTAMP WITH TIME ZONE NOT NULL, 
	fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(responsable_id) REFERENCES "user" (id) ON DELETE SET NULL
);

CREATE INDEX ix_albergue_estado_operativo ON albergue (estado_operativo);
CREATE INDEX ix_albergue_nombre ON albergue (nombre);
CREATE INDEX ix_albergue_municipio ON albergue (municipio);
CREATE UNIQUE INDEX ix_albergue_folio_identificador ON albergue (folio_identificador);

-- Tabla: albergue_usuario
CREATE TABLE albergue_usuario (
	albergue_id UUID NOT NULL, 
	usuario_id UUID NOT NULL, 
	rol roloperativo NOT NULL, 
	area areafuncional NOT NULL, 
	activo BOOLEAN NOT NULL, 
	id UUID NOT NULL, 
	fecha_asignacion TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(albergue_id) REFERENCES albergue (id) ON DELETE CASCADE, 
	FOREIGN KEY(usuario_id) REFERENCES "user" (id) ON DELETE CASCADE
);

CREATE INDEX ix_albergue_usuario_area ON albergue_usuario (area);
CREATE INDEX ix_albergue_usuario_rol ON albergue_usuario (rol);
CREATE INDEX ix_albergue_usuario_usuario_id ON albergue_usuario (usuario_id);
CREATE INDEX ix_albergue_usuario_albergue_id ON albergue_usuario (albergue_id);

-- Tabla: grupo_familiar
CREATE TABLE grupo_familiar (
	albergue_id UUID NOT NULL, 
	codigo_familia VARCHAR(50) NOT NULL, 
	nombre_referente VARCHAR(255) NOT NULL, 
	total_integrantes INTEGER NOT NULL, 
	comunidad_origen VARCHAR(255), 
	necesidades_especiales VARCHAR(500), 
	id UUID NOT NULL, 
	fecha_registro TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(albergue_id) REFERENCES albergue (id) ON DELETE CASCADE
);

CREATE INDEX ix_grupo_familiar_albergue_id ON grupo_familiar (albergue_id);
CREATE INDEX ix_grupo_familiar_codigo_familia ON grupo_familiar (codigo_familia);

-- Tabla: persona_refugiada
CREATE TABLE persona_refugiada (
	albergue_id UUID NOT NULL, 
	grupo_familiar_id UUID, 
	folio_identificacion VARCHAR(50) NOT NULL, 
	nombre VARCHAR(150) NOT NULL, 
	apellido_paterno VARCHAR(150) NOT NULL, 
	apellido_materno VARCHAR(150), 
	curp VARCHAR(20), 
	fecha_nacimiento TIMESTAMP WITH TIME ZONE, 
	genero VARCHAR(30), 
	municipio_origen VARCHAR(150), 
	localidad_origen VARCHAR(150), 
	telefono_contacto VARCHAR(50), 
	contacto_emergencia_nombre VARCHAR(255), 
	contacto_emergencia_telefono VARCHAR(50), 
	condicion_medica VARCHAR(500), 
	discapacidad BOOLEAN NOT NULL, 
	embarazo BOOLEAN NOT NULL, 
	adulto_mayor BOOLEAN NOT NULL, 
	menor_de_edad BOOLEAN NOT NULL, 
	necesidad_especial VARCHAR(500), 
	dormitorio_asignado VARCHAR(100), 
	numero_cama_colchoneta VARCHAR(50), 
	estado_estancia estadoestancia NOT NULL, 
	motivo_salida VARCHAR(255), 
	destino_salida VARCHAR(255), 
	observaciones VARCHAR(1000), 
	id UUID NOT NULL, 
	fecha_ingreso TIMESTAMP WITH TIME ZONE NOT NULL, 
	fecha_salida TIMESTAMP WITH TIME ZONE, 
	registrado_por_id UUID, 
	egreso_por_id UUID, 
	PRIMARY KEY (id), 
	FOREIGN KEY(albergue_id) REFERENCES albergue (id) ON DELETE CASCADE, 
	FOREIGN KEY(grupo_familiar_id) REFERENCES grupo_familiar (id) ON DELETE SET NULL, 
	FOREIGN KEY(registrado_por_id) REFERENCES "user" (id) ON DELETE SET NULL, 
	FOREIGN KEY(egreso_por_id) REFERENCES "user" (id) ON DELETE SET NULL
);

CREATE INDEX ix_persona_refugiada_curp ON persona_refugiada (curp);
CREATE INDEX ix_persona_refugiada_estado_estancia ON persona_refugiada (estado_estancia);
CREATE INDEX ix_persona_refugiada_albergue_id ON persona_refugiada (albergue_id);
CREATE UNIQUE INDEX ix_persona_refugiada_folio_identificacion ON persona_refugiada (folio_identificacion);
CREATE INDEX ix_persona_refugiada_grupo_familiar_id ON persona_refugiada (grupo_familiar_id);

-- Tabla: inventario_suministro
CREATE TABLE inventario_suministro (
	agua_potable FLOAT NOT NULL, 
	alimentos_no_perecederos INTEGER NOT NULL, 
	formula_infantil INTEGER NOT NULL, 
	medicamentos_basicos INTEGER NOT NULL, 
	material_curacion INTEGER NOT NULL, 
	cobijas INTEGER NOT NULL, 
	colchonetas INTEGER NOT NULL, 
	ropa INTEGER NOT NULL, 
	kits_higiene INTEGER NOT NULL, 
	panales INTEGER NOT NULL, 
	cubrebocas INTEGER NOT NULL, 
	productos_limpieza INTEGER NOT NULL, 
	bolsas_residuos INTEGER NOT NULL, 
	linternas INTEGER NOT NULL, 
	pilas INTEGER NOT NULL, 
	extintores INTEGER NOT NULL, 
	herramientas INTEGER NOT NULL, 
	material_oficina INTEGER NOT NULL, 
	id UUID NOT NULL, 
	albergue_id UUID NOT NULL, 
	fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(albergue_id) REFERENCES albergue (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX ix_inventario_suministro_albergue_id ON inventario_suministro (albergue_id);

-- Tabla: inventario_infraestructura
CREATE TABLE inventario_infraestructura (
	capacidad_maxima INTEGER NOT NULL, 
	dormitorios INTEGER NOT NULL, 
	banos INTEGER NOT NULL, 
	regaderas INTEGER NOT NULL, 
	cocina INTEGER NOT NULL, 
	comedor INTEGER NOT NULL, 
	consultorio INTEGER NOT NULL, 
	bodega INTEGER NOT NULL, 
	salidas_emergencia INTEGER NOT NULL, 
	extintores INTEGER NOT NULL, 
	accesos_silla_ruedas BOOLEAN NOT NULL, 
	planta_electrica BOOLEAN NOT NULL, 
	sistema_agua VARCHAR(100) NOT NULL, 
	estado_inmueble VARCHAR(100) NOT NULL, 
	id UUID NOT NULL, 
	albergue_id UUID NOT NULL, 
	fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(albergue_id) REFERENCES albergue (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX ix_inventario_infraestructura_albergue_id ON inventario_infraestructura (albergue_id);

-- Tabla: inventario_recurso_humano
CREATE TABLE inventario_recurso_humano (
	administrador INTEGER NOT NULL, 
	medicos INTEGER NOT NULL, 
	enfermeria INTEGER NOT NULL, 
	psicologia INTEGER NOT NULL, 
	cocineros INTEGER NOT NULL, 
	personal_limpieza INTEGER NOT NULL, 
	seguridad INTEGER NOT NULL, 
	trabajadores_sociales INTEGER NOT NULL, 
	traductores INTEGER NOT NULL, 
	voluntarios INTEGER NOT NULL, 
	conductores INTEGER NOT NULL, 
	responsables_bodega INTEGER NOT NULL, 
	id UUID NOT NULL, 
	albergue_id UUID NOT NULL, 
	fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(albergue_id) REFERENCES albergue (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX ix_inventario_recurso_humano_albergue_id ON inventario_recurso_humano (albergue_id);
