import json
from pathlib import Path


def generar_documento():
    with open("schema_inspeccion.json", encoding="utf-8") as f:
        datos = json.load(f)

    lineas = []
    lineas.append("# ESTRUCTURA TECNICA DE TABLAS Y ESQUEMA DE BASE DE DATOS")
    lineas.append("> SISTEMA SIGRAS - PROTECCION CIVIL / HACKATEC 2026")
    lineas.append(
        "> Documento tecnico parseado de las tablas fisicas en PostgreSQL (Supabase) y modelos de dominio."
    )
    lineas.append("")
    lineas.append("---")
    lineas.append("")
    lineas.append("## 1. RESUMEN EJECUTIVO DEL ESQUEMA FISICO")
    lineas.append("")
    lineas.append(
        "La base de datos en Supabase cuenta actualmente con **11 tablas fisicas** en el esquema `public`:"
    )
    lineas.append("")
    lineas.append(
        "| Tabla Fisica | Total Filas | Rol Operativo en la Contingencia | Relacion Principal |"
    )
    lineas.append("| :--- | :---: | :--- | :--- |")
    lineas.append(
        "| `albergue` | 5 | Refugios temporales habilitados en Tampico/Madero | Pertenece a un responsable (`user.id`) |"
    )
    lineas.append(
        "| `albergue_usuario` | 0 | Asignacion de personal y brigadistas a refugios | Intermedia entre `albergue` y `user` |"
    )
    lineas.append(
        "| `alerta_zona_riesgo` | 2 | Puntos y poligonos de inundacion / bloqueo vial | Independiente (Geoespacial) |"
    )
    lineas.append(
        "| `grupo_familiar` | 0 | Censos de nucleos familiares acogidos | Depende de `albergue.id` |"
    )
    lineas.append(
        "| `inventario_infraestructura` | 0 | Capacidad fisica, banos, cocina, accesibilidad | 1 a 1 con `albergue.id` |"
    )
    lineas.append(
        "| `inventario_recurso_humano` | 0 | Plantilla medica, operativa y voluntariado | 1 a 1 con `albergue.id` |"
    )
    lineas.append(
        "| `inventario_suministro` | 0 | Conteo de viveres, agua, colchonetas y medicinas | 1 a 1 con `albergue.id` |"
    )
    lineas.append(
        "| `persona_refugiada` | 0 | Censo nominal y triaje individual de evacuados | Pertenece a `albergue` y `grupo_familiar` |"
    )
    lineas.append(
        "| `user` | 1 | Operadores, coordinadores y brigadistas del sistema | Superadministrador activo verificado |"
    )
    lineas.append(
        "| `item` | 0 | Tabla residual del boilerplate original FastAPI | Depende de `user.id` |"
    )
    lineas.append(
        "| `alembic_version` | 1 | Registro de migraciones aplicadas | Tabla tecnica del sistema |"
    )
    lineas.append("")
    lineas.append("---")
    lineas.append("")
    lineas.append("## 2. DIAGRAMA CONCEPTUAL DE RELACIONES (ENTIDAD - RELACION)")
    lineas.append("")
    lineas.append("```mermaid")
    lineas.append("erDiagram")
    lineas.append('    USER ||--o{ ALBERGUE : "administra"')
    lineas.append('    USER ||--o{ ALBERGUE_USUARIO : "asignado_en"')
    lineas.append('    USER ||--o{ PERSONA_REFUGIADA : "registra_ingreso"')
    lineas.append('    USER ||--o{ PERSONA_REFUGIADA : "autoriza_egreso"')
    lineas.append('    USER ||--o{ ITEM : "posee"')
    lineas.append('    ALBERGUE ||--o{ ALBERGUE_USUARIO : "cuenta_con"')
    lineas.append('    ALBERGUE ||--o| INVENTARIO_INFRAESTRUCTURA : "posee_capacidad"')
    lineas.append('    ALBERGUE ||--o| INVENTARIO_RECURSO_HUMANO : "posee_personal"')
    lineas.append('    ALBERGUE ||--o| INVENTARIO_SUMINISTRO : "almacena_viveres"')
    lineas.append('    ALBERGUE ||--o{ GRUPO_FAMILIAR : "aloja_familias"')
    lineas.append('    ALBERGUE ||--o{ PERSONA_REFUGIADA : "aloja_personas"')
    lineas.append('    GRUPO_FAMILIAR ||--o{ PERSONA_REFUGIADA : "agrupa_miembros"')
    lineas.append("```")
    lineas.append("")
    lineas.append("---")
    lineas.append("")
    lineas.append("## 3. DESGLOSE DETALLADO TABLA POR TABLA")
    lineas.append("")

    descripciones_tablas = {
        "albergue": {
            "proposito": "Registro maestro de inmuebles habilitados como refugios temporales de emergencia en la zona conurbada.",
            "columnas_desc": {
                "id": "Identificador unico universal (UUID v4) del albergue.",
                "folio_identificador": "Codigo oficial de control administrativo de Proteccion Civil (ej. ALB-TAM-001).",
                "nombre": "Nombre descriptivo del inmueble (ej. Auditorio Municipal, Polideportivo Oriente).",
                "direccion": "Domicilio fisico completo con calle, numero y colonia.",
                "municipio": "Municipio de radicacion (Tampico, Ciudad Madero, Altamira).",
                "localidad": "Colonia, asentamiento o ejido especifico.",
                "estado_republica": "Entidad federativa (Tamaulipas / Veracruz).",
                "latitud": "Coordenada geografica de latitud en formato WGS84 para navegacion Mapbox.",
                "longitud": "Coordenada geografica de longitud en formato WGS84 para navegacion Mapbox.",
                "tipo_inmueble": "Clasificacion fisica del edificio (Escuela, Gimnasio, Centro Comunitario, Auditorio).",
                "telefono_contacto": "Linea telefonica directa de atencion o recepcion.",
                "admite_mascotas": "Booleano que autoriza la aceptacion de animales de compania en zona adaptada.",
                "estado_operativo": "Estado operativo actual: planeado, disponible, activado, lleno, cerrado, fuera_de_servicio.",
                "observaciones": "Anotaciones sobre condiciones de acceso, vias o recomendaciones de uso.",
                "responsable_id": "Enlace al usuario operador o coordinador responsable del albergue.",
                "fecha_registro": "Marca de tiempo de creacion en el sistema (UTC).",
                "fecha_actualizacion": "Marca de tiempo del ultimo corte o edicion de datos.",
            },
        },
        "albergue_usuario": {
            "proposito": "Tabla intermedia para gestionar los turnos, roles especificos y brigadas de usuarios dentro de un albergue.",
            "columnas_desc": {
                "id": "Identificador unico de la asignacion de personal.",
                "albergue_id": "Clave foranea que referencia al albergue asignado.",
                "usuario_id": "Clave foranea que referencia al usuario o brigadista operativo.",
                "rol": "Rol desempenado en este centro (coordinador, medico, enfermero, bodeguero, etc.).",
                "area": "Area operativa asignada (recepcion, salud, cocina, seguridad, logistica).",
                "activo": "Bandera de estado que indica si la persona esta de turno o comisionada actualmente.",
                "fecha_asignacion": "Fecha y hora de asignacion de la guardia o brigada.",
            },
        },
        "alerta_zona_riesgo": {
            "proposito": "Alertas hidrometeorologicas, desbordamientos de rios y bloqueos de vialidades que alimentan el mapa y el calculador de rutas seguras.",
            "columnas_desc": {
                "id": "Identificador unico universal de la alerta.",
                "codigo_alerta": "Codigo o folio oficial del boletin de alerta (ej. ALT-HIDRO-001).",
                "titulo": "Titulo conciso del evento (ej. Calle inundada 65 cm, Crecida Rio Panuco).",
                "tipo_fenomeno": "Clase de fenomeno perturbador (Inundacion severa, Encharcamiento, Deslave, Vía cerrada).",
                "nivel_alerta": "Semaforo de severidad: verde, amarillo, naranja, rojo.",
                "descripcion": "Detalle tecnico de la afectacion, tirante de agua estimado y vias alternas.",
                "cuenca_rio": "Nombre de la cuenca, laguna o cuerpo de agua relacionado (ej. Rio Panuco, Laguna del Carpintero).",
                "nivel_actual_metros": "Lectura hidrometrica actual en escala metrica.",
                "nivel_critico_desbordamiento": "Cota de escala a partir de la cual ocurre desbordamiento en zonas habitadas.",
                "municipios_afectados": "Listado de demarcaciones o colonias bajo impacto.",
                "latitud_referencia": "Punto central de latitud del bloqueo o zona de riesgo.",
                "longitud_referencia": "Punto central de longitud del bloqueo o zona de riesgo.",
                "radio_afectacion_km": "Radio de influencia geografica en kilometros para evitar enrutamiento.",
                "activo": "Estatus de la alerta en tiempo real (True = amenaza activa).",
                "fecha_emision": "Marca temporal de publicacion de la alerta.",
                "fecha_vigencia": "Fecha estimada de finalizacion del alertamiento.",
            },
        },
        "grupo_familiar": {
            "proposito": "Registro de cohesion de familias damnificadas para mantener unidas a las personas durante la asignacion de dormitorios y viveres.",
            "columnas_desc": {
                "id": "Identificador unico del grupo familiar.",
                "albergue_id": "Albergue en el cual se encuentra instalada la familia.",
                "codigo_familia": "Folio unico de nucleo familiar para control en puerta (ej. FAM-TAM-012).",
                "nombre_referente": "Nombre y apellidos del tutor, padre, madre o jefe de familia responsable.",
                "total_integrantes": "Cantidad total de integrantes que conforman el grupo familiar.",
                "comunidad_origen": "Colonia, sector o municipio del que provienen evacuados.",
                "necesidades_especiales": "Descripcion de necesidades medicas, lactancia, medicamentos cronicos o cuidados.",
                "fecha_registro": "Marca temporal del arribo y recepcion de la familia.",
            },
        },
        "inventario_infraestructura": {
            "proposito": "Capacidad instalada, balance hidraulico y dictamen de seguridad estructural de cada albergue (Relacion 1 a 1).",
            "columnas_desc": {
                "id": "Identificador unico del registro de infraestructura.",
                "albergue_id": "Albergue al que pertenece la infraestructura evaluada.",
                "capacidad_maxima": "Aforo maximo nominal de personas que pueden pernoctar con seguridad.",
                "dormitorios": "Numero de salones o naves acondicionadas como dormitorios.",
                "banos": "Cantidad de sanitarios higienicos funcionales.",
                "regaderas": "Numero de regaderas para aseo corporal disponibles.",
                "cocina": "Numero de estufas o areas habilitadas para preparacion de alimentos calientes.",
                "comedor": "Capacidad o modulos de comedor comunitario.",
                "consultorio": "Modulos dedicados para triaje medico y primeros auxilios.",
                "bodega": "Espacios secos y seguros destinados a almacenamiento de viveres.",
                "salidas_emergencia": "Puertas de escape senalizadas y despejadas.",
                "extintores": "Equipos contra incendios vigentes y presurizados.",
                "accesos_silla_ruedas": "Indicador si cuenta con rampas y accesibilidad universal.",
                "planta_electrica": "Existencia de generador electrico auxiliar ante cortes de luz.",
                "sistema_agua": "Modo de suministro de agua (red_publica, cisterna, pozo, pipa).",
                "estado_inmueble": "Dictamen estructural de Proteccion Civil (optimo, bueno, regular, etc.).",
                "fecha_actualizacion": "Fecha de la ultima inspeccion fisica del inmueble.",
            },
        },
        "inventario_recurso_humano": {
            "proposito": "Conteo y distribucion por especialidad del personal desplegado en el refugio (Relacion 1 a 1).",
            "columnas_desc": {
                "id": "Identificador unico del censo de recursos humanos.",
                "albergue_id": "Albergue al que esta adscrito este equipo de trabajo.",
                "administrador": "Conteo de coordinadores generales de refugio presentes.",
                "medicos": "Medicos titulados en turno activo.",
                "enfermeria": "Personal de enfermeria y primeros auxilios.",
                "psicologia": "Profesionales de intervencion en crisis y apoyo emocional.",
                "cocineros": "Personal asignado a preparacion y racionamiento de comida.",
                "personal_limpieza": "Personal de intendencia, sanitizacion y manejo de residuos.",
                "seguridad": "Guardias municipales, policias o personal de control de accesos.",
                "trabajadores_sociales": "Trabajadores sociales para censo y vinculacion familiar.",
                "traductores": "Interpretes de lenguas originarias o idiomas extranjeros.",
                "voluntarios": "Voluntarios acreditados de la sociedad civil.",
                "conductores": "Choferes asignados a ambulancias, vans y transporte de evacudados.",
                "responsables_bodega": "Encargados de recepcion de donativos y entrega de suministros.",
                "fecha_actualizacion": "Marca temporal del ultimo pase de lista operativo.",
            },
        },
        "inventario_suministro": {
            "proposito": "Balance consolidado de viveres, abrigo, medicamentos y herramientas almacenadas en el refugio (Relacion 1 a 1).",
            "columnas_desc": {
                "id": "Identificador unico del inventario de suministros.",
                "albergue_id": "Albergue depositario de los insumos.",
                "agua_potable": "Volumen en litros de agua purificada disponible para consumo.",
                "alimentos_no_perecederos": "Raciones o paquetes de comida enlatada y no perecedera.",
                "formula_infantil": "Latas de leche maternizada para bebes y lactantes.",
                "medicamentos_basicos": "Unidades o cajas de analgesicos, antibioticos y suero oral.",
                "material_curacion": "Paquetes de gasas, vendas, alcohol, antisepticos y guantes.",
                "cobijas": "Piezas de frazadas o cobijas termicas limpias.",
                "colchonetas": "Colchonetas de hule espuma o vinil para descanso.",
                "ropa": "Prendas de vestir ordenadas por talla y genero.",
                "kits_higiene": "Paquetes personales con jabon, pasta dental, cepillo y toalla.",
                "panales": "Paquetes de panales para infantes y adultos mayores.",
                "cubrebocas": "Mascarillas quirurgicas o KN95 para prevencion sanitaria.",
                "productos_limpieza": "Cloro, detergentes, escobas y desinfectante ambiental.",
                "bolsas_residuos": "Rollos de bolsas de plastico grueso para desechos biologicos y comunes.",
                "linternas": "Linternas manuales o reflectores recargables.",
                "pilas": "Pilas secas de distintos calibres (AA, AAA, D).",
                "extintores": "Extintores adicionales almacenados en reserva.",
                "herramientas": "Juegos de palas, carretillas, zapapicos, martillos y desarmadores.",
                "material_oficina": "Papeleria, carpetas, gafetes y plumas para el registro censal.",
                "fecha_actualizacion": "Marca de tiempo del ultimo balance de almacen.",
            },
        },
        "persona_refugiada": {
            "proposito": "Padron nominal individualizado de cada ciudadano evacuado, registrando triaje medico, vulnerabilidades, ubicacion de pernocta y salida.",
            "columnas_desc": {
                "id": "Identificador unico universal de la persona refugiada.",
                "albergue_id": "Albergue en el que se encuentra alojada la persona.",
                "grupo_familiar_id": "Enlace a la familia a la que pertenece (opcional si viaja sola).",
                "folio_identificacion": "Folio unico individual de ingreso (ej. REF-2026-0045).",
                "nombre": "Nombre o nombres de pila de la persona.",
                "apellido_paterno": "Primer apellido.",
                "apellido_materno": "Segundo apellido.",
                "curp": "Clave Unica de Registro de Poblacion de Mexico.",
                "fecha_nacimiento": "Fecha de nacimiento registrada.",
                "genero": "Genero (masculino, femenino, otro).",
                "municipio_origen": "Municipio de donde fue evacuada la persona.",
                "localidad_origen": "Colonia, barrio o poblado de residencia original.",
                "telefono_contacto": "Telefono personal si se cuenta con comunicacion.",
                "contacto_emergencia_nombre": "Nombre de un pariente o contacto externo no damnificado.",
                "contacto_emergencia_telefono": "Telefono del contacto externo de emergencia.",
                "condicion_medica": "Padecimientos preexistentes (diabetes, hipertension, dialisis, etc.).",
                "discapacidad": "Indicador de discapacidad motriz, visual, auditiva o intelectual.",
                "embarazo": "Indicador de estado de gestacion activo.",
                "adulto_mayor": "Indicador si la persona tiene 60 anos o mas.",
                "menor_de_edad": "Indicador si la persona es menor a 18 anos.",
                "necesidad_especial": "Detalle sobre dietas, medicamentos de rescate o atencion prioritaria.",
                "dormitorio_asignado": "Salon, carpa o aula donde duerme la persona.",
                "numero_cama_colchoneta": "Numero o etiqueta de colchoneta/cama asignada.",
                "estado_estancia": "Estatus en el albergue: ingresado, en_albergue, egresado, trasladado.",
                "motivo_salida": "Motivo del retiro (Retorno a domicilio, traslado a hospital, con parientes).",
                "destino_salida": "Direccion o ciudad hacia donde partio la persona al salir.",
                "observaciones": "Anotaciones medicas, psicologicas o legales relevantes.",
                "registrado_por_id": "Usuario o brigadista que capturo el ingreso.",
                "egreso_por_id": "Usuario o autoridad que autorizo y registro el egreso.",
                "fecha_ingreso": "Momento exacto en que fue recibida la persona.",
                "fecha_salida": "Momento en que concluyo su estancia en el refugio.",
            },
        },
        "user": {
            "proposito": "Usuarios, brigadistas, coordinadores de Proteccion Civil y administradores autorizados para operar la plataforma.",
            "columnas_desc": {
                "id": "Identificador unico universal del usuario.",
                "email": "Correo electronico institucional utilizado como nombre de usuario para login.",
                "hashed_password": "Hash seguro de contrasena cifrado mediante algoritmo Argon2.",
                "full_name": "Nombre completo y cargo institucional del funcionario o brigadista.",
                "is_active": "Bandera booleana de activacion de la cuenta.",
                "is_superuser": "Bandera booleana que otorga privilegios totales de superadministrador.",
                "rol": "Rol operativo: 'coordinador_emergencias', 'administrador_albergue', 'personal_operativo'.",
                "alcance_id": "Jurisdiccion o albergue especifico que tiene asignado para administracion.",
                "created_at": "Fecha y hora de alta del usuario en la plataforma.",
            },
        },
        "item": {
            "proposito": "Tabla heredada de la plantilla base de FastAPI (Full-Stack Template). No cumple funcion en SIGRAS.",
            "columnas_desc": {
                "id": "Identificador UUID del item.",
                "title": "Titulo del item de prueba.",
                "description": "Descripcion del item de prueba.",
                "owner_id": "Clave foranea que referencia a user.id.",
                "created_at": "Fecha de creacion.",
            },
        },
        "alembic_version": {
            "proposito": "Tabla de control interno del motor de migraciones de Alembic.",
            "columnas_desc": {
                "version_num": "Identificador alfanumerico del hash de revision de la migracion actual."
            },
        },
    }

    contador_tabla = 1
    for nombre_tabla, info in sorted(datos.items()):
        meta = descripciones_tablas.get(nombre_tabla, {})
        lineas.append(f"### 3.{contador_tabla} Tabla: `{nombre_tabla}`")
        contador_tabla += 1
        lineas.append(f"* **Total de Filas Actuales:** `{info['filas_totales']}`")
        lineas.append(
            f"* **Proposito Operativo:** {meta.get('proposito', 'Sin descripcion disponible.')}"
        )

        # Llaves
        pk_str = (
            ", ".join(f"`{c}`" for c in info["primary_key"])
            if info["primary_key"]
            else "Ninguna"
        )
        lineas.append(f"* **Clave Primaria (Primary Key):** {pk_str}")

        if info["foreign_keys"]:
            lineas.append("* **Claves Foraneas (Foreign Keys):**")
            for fk in info["foreign_keys"]:
                cols_o = ", ".join(fk["columna_origen"])
                cols_d = ", ".join(fk["columna_destino"])
                lineas.append(
                    f"  - `{cols_o}` ➔ referencia a `{fk['tabla_destino']}.{cols_d}`"
                )
        else:
            lineas.append("* **Claves Foraneas (Foreign Keys):** Ninguna")

        # Indices y Uniques
        if info.get("indexes"):
            indices_str = []
            for idx in info["indexes"]:
                cols = ", ".join(idx["columnas"]) if idx.get("columnas") else ""
                tipo_u = " (UNIQUE)" if idx.get("unique") else ""
                indices_str.append(f"`{idx['nombre']}` ({cols}){tipo_u}")
            lineas.append(f"* **Indices Existentes:** {', '.join(indices_str)}")

        lineas.append("")
        lineas.append(
            "| Columna | Tipo de Dato Fisica | Nulo | Default | Restriccion | Descripcion Funcional |"
        )
        lineas.append("| :--- | :--- | :---: | :---: | :---: | :--- |")

        cols_desc = meta.get("columnas_desc", {})
        for col in info["columnas"]:
            c_nom = col["nombre"]
            c_tipo = col["tipo"]
            c_null = "NULL" if col["nullable"] else "**NOT NULL**"
            c_def = f"`{col['default']}`" if col["default"] is not None else "-"

            restricciones = []
            if c_nom in info["primary_key"]:
                restricciones.append("PK")
            for fk in info["foreign_keys"]:
                if c_nom in fk["columna_origen"]:
                    restricciones.append(f"FK -> `{fk['tabla_destino']}`")
            for idx in info.get("indexes", []):
                if idx.get("unique") and c_nom in (idx.get("columnas") or []):
                    restricciones.append("UNIQUE")

            restr_str = " | ".join(restricciones) if restricciones else "-"
            desc_str = cols_desc.get(c_nom, "Campo operativo de la tabla.")
            lineas.append(
                f"| `{c_nom}` | `{c_tipo}` | {c_null} | {c_def} | {restr_str} | {desc_str} |"
            )

        lineas.append("")
        lineas.append("---")
        lineas.append("")

    lineas.append(
        "## 4. TABLAS DEFINIDAS EN MODELOS SQLMODEL (PENDIENTES DE CREACION FISICA)"
    )
    lineas.append("")
    lineas.append(
        "En el modulo `app/models/` existen modelos definidos que **no estan creados fisicamente en Supabase**:"
    )
    lineas.append("")
    lineas.append("### 4.1 `reporte_ciudadano` (`app/models/reporte_ciudadano.py`)")
    lineas.append(
        "Permite capturar alertas y emergencias enviadas por la ciudadania desde el mapa publico."
    )
    lineas.append("* **Campos proyectados:**")
    lineas.append("  - `id`: UUID (PK)")
    lineas.append("  - `folio_reporte`: VARCHAR(50) (UNIQUE, INDEX)")
    lineas.append(
        "  - `tipo_emergencia`: Enum ('inundacion_severa', 'persona_atrapada', 'deslave_bloqueo_camino', 'requiere_evacuacion', 'desabasto_suministros', 'atencion_medica_urgente', 'otro')"
    )
    lineas.append("  - `descripcion`: VARCHAR(2000)")
    lineas.append("  - `latitud`: DOUBLE PRECISION (INDEX)")
    lineas.append("  - `longitud`: DOUBLE PRECISION (INDEX)")
    lineas.append("  - `direccion_referencia`: VARCHAR(500)")
    lineas.append("  - `municipio`: VARCHAR(150) (INDEX)")
    lineas.append("  - `localidad`: VARCHAR(150)")
    lineas.append(
        "  - `nivel_prioridad`: Enum ('baja', 'media', 'alta', 'critica_vida_en_riesgo')"
    )
    lineas.append(
        "  - `estado_reporte`: Enum ('recibido', 'en_verificacion', 'brigada_asignada', 'atendido', 'cancelado')"
    )
    lineas.append("  - `personas_afectadas`: INTEGER (DEFAULT 1)")
    lineas.append("  - `personas_vulnerables`: INTEGER (DEFAULT 0)")
    lineas.append("  - `telefono_contacto`: VARCHAR(50)")
    lineas.append("  - `url_evidencia_multimedia`: VARCHAR(1000)")
    lineas.append("  - `brigada_asignada_id`: UUID (FK -> `user.id`, NULL)")
    lineas.append("  - `fecha_reporte`: TIMESTAMP WITH TIME ZONE")
    lineas.append("  - `fecha_atencion`: TIMESTAMP WITH TIME ZONE (NULL)")
    lineas.append("")
    lineas.append(
        "### 4.2 Modelos Normalizados 3FN de Suministros (`app/models/suministro.py`)"
    )
    lineas.append(
        "Modelos disenados para desglosar insumos por catalogo maestro y movimientos de entrada/salida:"
    )
    lineas.append(
        "1. `catalogo_suministro`: Catalogo maestro de articulos con codigo de barras/clave, categoria y unidad de medida."
    )
    lineas.append(
        "2. `inventario_articulo_suministro`: Existencias por articulo en cada albergue (Relacion N a M con stock actual y minimo)."
    )
    lineas.append(
        "3. `movimiento_suministro`: Bitacora transaccional de donaciones, traslados, consumos y mermas con firma del responsable."
    )
    lineas.append("")
    lineas.append("---")
    lineas.append("")
    lineas.append("## 5. DIAGNOSTICO Y RECOMENDACIONES DE SANEAMIENTO")
    lineas.append("")
    lineas.append(
        "### Recomendacion 1: Depurar Tablas Innecesarias que Complicarian la Operacion"
    )
    lineas.append(
        '* **`item`:** Es un residuo del template original de FastAPI con 0 registros. Debe mantenerse ignorada o eliminarse (`DROP TABLE "item" CASCADE`) si no se requiere, evitando contaminar el esquema operativo.'
    )
    lineas.append(
        "* **Modelos 3FN complejos de Suministros:** El modelo simple actual `inventario_suministro` con 1 fila por albergue (conteos directos de agua, colchonetas, comida, medicinas) es **inmensamente mas facil de operar** durante un hackaton y una emergencia real que gestionar tablas maestras normalizadas y transacciones complejas."
    )
    lineas.append("")
    lineas.append(
        '### Recomendacion 2: Mantener la Tabla Fisica `"user"` con Nombres Compatibles'
    )
    lineas.append(
        '* La tabla física se llama `"user"` y ya cuenta con `rol` y `alcance_id`.'
    )
    lineas.append(
        "* Jamas renombrar fisicamente a `usuarios_admin` en PostgreSQL porque romperia las 4 claves foraneas existentes (`albergue.responsable_id`, `albergue_usuario.usuario_id`, `persona_refugiada.registrado_por_id`, `persona_refugiada.egreso_por_id`)."
    )
    lineas.append(
        "* En el backend de Python, el patron de `@property` (`correo`, `nombre`, `hash_password`) en `app/models/usuario.py` garantiza el uso 100% en espanol sin tocar las columnas fisicas de PostgreSQL."
    )
    lineas.append("")
    lineas.append("### Recomendacion 3: Simplificacion de `persona_refugiada`")
    lineas.append(
        "* La tabla contiene 31 columnas, lo cual es exhaustivo para estadisticas post-desastre."
    )
    lineas.append(
        "* Sin embargo, durante el arribo rapido a puerta (Triaje en Puerta), solo se deben exigir como obligatorios: `folio_identificacion`, `nombre`, `apellido_paterno`, `genero`, y `estado_estancia`."
    )
    lineas.append(
        "* Todas las demas columnas (`curp`, `telefono`, `condicion_medica`, `observaciones`) ya estan configuradas como `NULL` permisivo, permitiendo admision ultrarrapida en menos de 30 segundos."
    )
    lineas.append("")
    lineas.append("---")
    lineas.append(
        "*Documento generado automaticamente tras la inspeccion fisica de PostgreSQL Supabase.*"
    )

    texto = "\n".join(lineas)

    # Escribir a MUACK_2.0
    ruta_muack = Path(
        r"c:\Users\carde\Desktop\MUACK_2.0\ESTRUCTURA_TABLAS_BASE_DE_DATOS.md"
    )
    ruta_muack.write_text(texto, encoding="utf-8")
    print(f"Documento escrito en: {ruta_muack}")

    # Escribir a HACKATEC_proyecto
    ruta_hackatec = Path(
        r"C:\Users\carde\Desktop\HACKATEC_proyecto\ESTRUCTURA_TABLAS_BASE_DE_DATOS.md"
    )
    ruta_hackatec.write_text(texto, encoding="utf-8")
    print(f"Documento escrito en: {ruta_hackatec}")


if __name__ == "__main__":
    generar_documento()
