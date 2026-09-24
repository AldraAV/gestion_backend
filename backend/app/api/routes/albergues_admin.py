import uuid
from datetime import UTC, date, datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import AliasChoices, BaseModel, ConfigDict
from pydantic import Field as PydField
from sqlalchemy import text

from app.api.deps import CurrentUser, SessionDep
from app.models.albergue import (
    Albergue,
)
from app.models.albergue_usuario import (
    AlbergueUsuario,
    AlbergueUsuarioCreate,
    AlbergueUsuarioPublic,
    AlbergueUsuarioUpdate,
    PersonalAsignadoDetalle,
)
from app.models.dashboard_albergue import (
    AdministradorACargo,
    DashboardAlbergueRespuesta,
    PersonaAlbergadaItemDashboard,
    ResumenInfraestructuraDashboard,
    ResumenRecursoHumanoDashboard,
    ResumenSuministrosDashboard,
)
from app.models.infraestructura import InventarioInfraestructura
from app.models.usuario import RolOperativo

router = APIRouter(prefix="/albergues", tags=["albergues-admin"])


def verificar_acceso_albergue(
    usuario: CurrentUser, albergue_id: uuid.UUID, session: Any
) -> None:
    """Valida si el usuario tiene privilegios para acceder al albergue solicitado.

    Regla de autorizacion:
    - Superusuarios y usuarios con rol general 'coordinador_emergencias' tienen acceso
      global a cualquier albergue (multi-albergue).
    - Para los demas roles, la unica fuente de verdad operativa es la tabla 'albergue_usuario',
      requiriendo una asignacion activa para el albergue especifico.
    """
    if usuario.is_superuser:
        return

    rol_str = str(usuario.rol or "").lower()
    if rol_str == RolOperativo.COORDINADOR_EMERGENCIAS.value:
        return

    consulta = text("""
        SELECT id, rol, area, turno, activo
        FROM albergue_usuario
        WHERE usuario_id = :usuario_id
          AND albergue_id = :albergue_id
          AND activo = true
    """)
    asignacion = (
        session.execute(
            consulta, {"usuario_id": usuario.id, "albergue_id": albergue_id}
        )
        .mappings()
        .first()
    )

    if not asignacion:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene autorizacion para acceder a un albergue fuera de su asignacion operativa activa.",
        )


def puede_ver_datos_medicos(
    usuario: CurrentUser, albergue_id: uuid.UUID, session: Any
) -> bool:
    """Determina si el usuario tiene permisos para consultar diagnosticos y vulnerabilidades medicas.

    Regla de privacidad:
    - Coordinadores de emergencias y superusuarios: acceso global a telemetria medica.
    - Administradores de albergue asignados activamente a este refugio: acceso autorizado.
    - Responsables o personal asignados activamente al area funcional 'salud_medica': acceso autorizado.
    - Personal de logistica, bodega, recepcion o sin rol medico: datos anonimizados/None.
    """
    if usuario.is_superuser:
        return True

    rol_str = str(usuario.rol or "").lower()
    if rol_str == RolOperativo.COORDINADOR_EMERGENCIAS.value:
        return True

    consulta = text("""
        SELECT rol, area, activo
        FROM albergue_usuario
        WHERE usuario_id = :usuario_id
          AND albergue_id = :albergue_id
          AND activo = true
    """)
    asignacion = (
        session.execute(
            consulta, {"usuario_id": usuario.id, "albergue_id": albergue_id}
        )
        .mappings()
        .first()
    )

    if not asignacion:
        return False

    rol_operativo_local = str(asignacion["rol"] or "").lower()
    area_local = str(asignacion["area"] or "").lower()

    if rol_operativo_local in (
        RolOperativo.ADMINISTRADOR_ALBERGUE.value,
        "administrador",
    ):
        return True

    if area_local == "salud_medica":
        return True

    return False


# ==============================================================================
# CARGA MASIVA DE INMUEBLES / ALBERGUES (COORDINACION DE EMERGENCIAS)
# ==============================================================================


class InmuebleCargaMasiva(BaseModel):
    """Representa un inmueble a importar o actualizar de forma masiva."""

    model_config = ConfigDict(populate_by_name=True)

    folio_identificador: str = PydField(
        ...,
        max_length=50,
        validation_alias=AliasChoices(
            "folio_identificador", "folioIdentificador", "folio", "id_inmueble"
        ),
        description="Identificador unico del inmueble o refugio temporal",
    )
    nombre: str = PydField(
        ...,
        max_length=255,
        description="Nombre oficial del inmueble o albergue",
    )
    direccion: str = PydField(
        ...,
        max_length=500,
        description="Calle, numero y colonia",
    )
    municipio: str = PydField(
        ...,
        max_length=150,
        description="Municipio o alcaldia",
    )
    localidad: str | None = PydField(
        default=None,
        max_length=150,
        description="Localidad, poblado o comunidad",
    )
    estado_republica: str = PydField(
        default="Veracruz",
        max_length=100,
        validation_alias=AliasChoices("estado_republica", "estadoRepublica", "estado"),
        description="Entidad federativa",
    )
    latitud: float | None = PydField(
        default=None,
        description="Latitud en WGS84",
    )
    longitud: float | None = PydField(
        default=None,
        description="Longitud en WGS84",
    )
    tipo_inmueble: str | None = PydField(
        default=None,
        max_length=100,
        validation_alias=AliasChoices("tipo_inmueble", "tipoInmueble", "tipo"),
        description="Escuela, auditorio, polideportivo, templo, etc.",
    )
    telefono_contacto: str | None = PydField(
        default=None,
        max_length=50,
        validation_alias=AliasChoices(
            "telefono_contacto", "telefonoContacto", "telefono"
        ),
        description="Telefono de contacto o atencion",
    )
    admite_mascotas: bool = PydField(
        default=False,
        validation_alias=AliasChoices("admite_mascotas", "admiteMascotas"),
        description="Indica si cuenta con zona para animales de compania",
    )
    capacidad_maxima: int = PydField(
        default=100,
        ge=1,
        validation_alias=AliasChoices(
            "capacidad_maxima", "capacidadMaxima", "capacidad"
        ),
        description="Capacidad maxima estimada de personas",
    )
    observaciones: str | None = PydField(
        default=None,
        max_length=1000,
        description="Notas operativas adicionales",
    )


class SolicitudCargaMasiva(BaseModel):
    """Payload de entrada para carga masiva de albergues."""

    model_config = ConfigDict(populate_by_name=True)
    inmuebles: list[InmuebleCargaMasiva] = PydField(
        ...,
        min_length=1,
        description="Lista de inmuebles a procesar",
    )


class InmuebleResultado(BaseModel):
    """Resultado individual de procesamiento de inmueble."""

    folio_identificador: str
    nombre: str
    municipio: str
    estado_republica: str
    accion: str
    id: str


class RespuestaCargaMasiva(BaseModel):
    """Respuesta consolidada de la operacion de carga masiva."""

    mensaje: str
    total_procesados: int
    creados: int
    actualizados: int
    detalles: list[InmuebleResultado]


@router.post(
    "/carga-masiva",
    response_model=RespuestaCargaMasiva,
    summary="Carga masiva de inmuebles y refugios temporales",
)
def carga_masiva_albergues(
    solicitud: SolicitudCargaMasiva,
    session: SessionDep,
    usuario_actual: CurrentUser,
) -> Any:
    """Importa o actualiza por lotes inmuebles de refugios temporales.

    Requiere rol de Coordinador de Emergencias o Superusuario.
    Para cada inmueble:
    - Si existe por 'folio_identificador': actualiza sus datos y la capacidad maxima.
    - Si no existe: lo crea e inicializa sus tres inventarios asociados (infraestructura,
      suministros basicos y recurso humano) de forma atomica.
    """
    es_coordinador = (
        usuario_actual.rol
        in (RolOperativo.COORDINADOR_EMERGENCIAS, "coordinador_emergencias")
        or usuario_actual.is_superuser
    )
    if not es_coordinador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operacion restringida a Coordinadores de Emergencias o Administradores del Sistema.",
        )

    creados = 0
    actualizados = 0
    detalles: list[InmuebleResultado] = []

    for inm in solicitud.inmuebles:
        albergue_id_existente = session.execute(
            text("SELECT id FROM albergue WHERE folio_identificador = :folio"),
            {"folio": inm.folio_identificador},
        ).scalar()

        if albergue_id_existente:
            session.execute(
                text("""
                UPDATE albergue
                SET nombre = :nombre,
                    direccion = :direccion,
                    municipio = :municipio,
                    localidad = :localidad,
                    estado_republica = :estado_republica,
                    latitud = :latitud,
                    longitud = :longitud,
                    tipo_inmueble = :tipo_inmueble,
                    telefono_contacto = :telefono_contacto,
                    admite_mascotas = :admite_mascotas,
                    observaciones = :observaciones,
                    fecha_actualizacion = NOW()
                WHERE id = :id
            """),
                {
                    "id": albergue_id_existente,
                    "nombre": inm.nombre,
                    "direccion": inm.direccion,
                    "municipio": inm.municipio,
                    "localidad": inm.localidad,
                    "estado_republica": inm.estado_republica,
                    "latitud": inm.latitud,
                    "longitud": inm.longitud,
                    "tipo_inmueble": inm.tipo_inmueble,
                    "telefono_contacto": inm.telefono_contacto,
                    "admite_mascotas": inm.admite_mascotas,
                    "observaciones": inm.observaciones,
                },
            )

            session.execute(
                text("""
                INSERT INTO inventario_infraestructura (
                    id, albergue_id, capacidad_maxima, dormitorios, banos,
                    regaderas, cocina, comedor, consultorio, bodega,
                    salidas_emergencia, extintores_instalados,
                    accesos_silla_ruedas, planta_electrica,
                    sistema_agua, estado_inmueble, fecha_actualizacion
                ) VALUES (
                    :id, :albergue_id, :capacidad_maxima, 0, 0,
                    0, 0, 0, 0, 0,
                    0, 0,
                    false, false,
                    'Red municipal', 'Operativo', NOW()
                )
                ON CONFLICT (albergue_id) DO UPDATE
                SET capacidad_maxima = EXCLUDED.capacidad_maxima,
                    fecha_actualizacion = NOW()
            """),
                {
                    "id": uuid.uuid4(),
                    "albergue_id": albergue_id_existente,
                    "capacidad_maxima": inm.capacidad_maxima,
                },
            )

            actualizados += 1
            detalles.append(
                InmuebleResultado(
                    folio_identificador=inm.folio_identificador,
                    nombre=inm.nombre,
                    municipio=inm.municipio,
                    estado_republica=inm.estado_republica,
                    accion="actualizado",
                    id=str(albergue_id_existente),
                )
            )
        else:
            nuevo_id = uuid.uuid4()
            session.execute(
                text("""
                INSERT INTO albergue (
                    id, folio_identificador, nombre, direccion,
                    municipio, localidad, estado_republica,
                    latitud, longitud, tipo_inmueble,
                    telefono_contacto, admite_mascotas, ocupacion_actual,
                    estado_operativo, observaciones, fecha_registro, fecha_actualizacion
                ) VALUES (
                    :id, :folio_identificador, :nombre, :direccion,
                    :municipio, :localidad, :estado_republica,
                    :latitud, :longitud, :tipo_inmueble,
                    :telefono_contacto, :admite_mascotas, 0,
                    'activado', :observaciones, NOW(), NOW()
                )
            """),
                {
                    "id": nuevo_id,
                    "folio_identificador": inm.folio_identificador,
                    "nombre": inm.nombre,
                    "direccion": inm.direccion,
                    "municipio": inm.municipio,
                    "localidad": inm.localidad,
                    "estado_republica": inm.estado_republica,
                    "latitud": inm.latitud,
                    "longitud": inm.longitud,
                    "tipo_inmueble": inm.tipo_inmueble,
                    "telefono_contacto": inm.telefono_contacto,
                    "admite_mascotas": inm.admite_mascotas,
                    "observaciones": inm.observaciones,
                },
            )

            session.execute(
                text("""
                INSERT INTO inventario_infraestructura (
                    id, albergue_id, capacidad_maxima, dormitorios, banos,
                    regaderas, cocina, comedor, consultorio, bodega,
                    salidas_emergencia, extintores_instalados,
                    accesos_silla_ruedas, planta_electrica,
                    sistema_agua, estado_inmueble, fecha_actualizacion
                ) VALUES (
                    :id, :albergue_id, :capacidad_maxima, 0, 0,
                    0, 0, 0, 0, 0,
                    0, 0,
                    false, false,
                    'Red municipal', 'Operativo', NOW()
                )
            """),
                {
                    "id": uuid.uuid4(),
                    "albergue_id": nuevo_id,
                    "capacidad_maxima": inm.capacidad_maxima,
                },
            )

            session.execute(
                text("""
                INSERT INTO inventario_suministro (
                    id, albergue_id, agua_potable, alimentos_no_perecederos,
                    formula_infantil, medicamentos_basicos, material_curacion,
                    cobijas, colchonetas, ropa, kits_higiene, panales,
                    cubrebocas, productos_limpieza, bolsas_residuos,
                    linternas, pilas, extintores_reserva, herramientas,
                    material_oficina, fecha_actualizacion
                ) VALUES (
                    :id, :albergue_id, :agua, :alimentos,
                    0, 0, 0,
                    :cobijas, :colchonetas, 0, :kits, 0,
                    0, 0, 0,
                    0, 0, 0, 0,
                    0, NOW()
                )
            """),
                {
                    "id": uuid.uuid4(),
                    "albergue_id": nuevo_id,
                    "agua": float(inm.capacidad_maxima * 3),
                    "alimentos": inm.capacidad_maxima * 3,
                    "colchonetas": inm.capacidad_maxima,
                    "cobijas": inm.capacidad_maxima,
                    "kits": inm.capacidad_maxima,
                },
            )

            session.execute(
                text("""
                INSERT INTO inventario_recurso_humano (
                    id, albergue_id, administrador, medicos, enfermeria,
                    psicologia, cocineros, personal_limpieza, seguridad,
                    trabajadores_sociales, traductores, voluntarios,
                    conductores, responsables_bodega, fecha_actualizacion
                ) VALUES (
                    :id, :albergue_id, 1, 0, 0,
                    0, 0, 0, 0,
                    0, 0, 0,
                    0, 0, NOW()
                )
            """),
                {
                    "id": uuid.uuid4(),
                    "albergue_id": nuevo_id,
                },
            )

            creados += 1
            detalles.append(
                InmuebleResultado(
                    folio_identificador=inm.folio_identificador,
                    nombre=inm.nombre,
                    municipio=inm.municipio,
                    estado_republica=inm.estado_republica,
                    accion="creado",
                    id=str(nuevo_id),
                )
            )

    session.commit()

    return RespuestaCargaMasiva(
        mensaje=f"Carga masiva procesada: {creados} creados, {actualizados} actualizados.",
        total_procesados=len(solicitud.inmuebles),
        creados=creados,
        actualizados=actualizados,
        detalles=detalles,
    )


@router.get(
    "/mi-albergue",
    response_model=DashboardAlbergueRespuesta,
    summary="Dashboard directo del albergue a cargo del Administrador autenticado",
)
def obtener_mi_albergue(
    session: SessionDep,
    usuario_actual: CurrentUser,
) -> Any:
    """Permite al Administrador de Albergue autenticado consultar directamente el albergue bajo su responsabilidad."""
    # 1. Buscar en albergue_usuario si tiene una asignacion activa
    consulta_asignacion = text("""
        SELECT albergue_id
        FROM albergue_usuario
        WHERE usuario_id = :usuario_id
          AND activo = true
        ORDER BY fecha_asignacion DESC
        LIMIT 1
    """)
    albergue_id = session.execute(
        consulta_asignacion, {"usuario_id": usuario_actual.id}
    ).scalar()

    # 2. Si no tiene asignacion fija (ej. superusuario), tomar el primer albergue activo
    if not albergue_id:
        albergue_id = session.execute(
            text("SELECT id FROM albergue ORDER BY nombre ASC LIMIT 1")
        ).scalar()

    if not albergue_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontro ningun albergue activo a cargo del usuario.",
        )

    return obtener_dashboard_albergue(
        id=albergue_id, session=session, usuario_actual=usuario_actual
    )


@router.get(
    "/{id}/dashboard",
    response_model=DashboardAlbergueRespuesta,
    summary="Dashboard consolidado de control para Administrador de Albergue",
)
def obtener_dashboard_albergue(
    id: uuid.UUID,
    session: SessionDep,
    usuario_actual: CurrentUser,
) -> Any:
    """Retorna la vista consolidada de ocupacion, suministros criticos per capita,

    personal operativo y lista de personas albergadas con proteccion de datos sensibles.
    """
    verificar_acceso_albergue(usuario_actual, id, session)

    # 1. Consultar la vista SQL consolidada
    consulta_vista = text("""
        SELECT *
        FROM vista_dashboard_albergue
        WHERE albergue_id = :albergue_id
    """)
    fila_vista = session.execute(consulta_vista, {"albergue_id": id}).mappings().first()

    if not fila_vista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Albergue con identificador {id} no encontrado en el sistema.",
        )

    # 2. Consultar el Administrador a cargo del albergue
    consulta_admin = text("""
        SELECT u.id, u.full_name, u.email, u.rol
        FROM albergue_usuario au
        JOIN "user" u ON u.id = au.usuario_id
        WHERE au.albergue_id = :albergue_id
          AND (au.rol::text IN ('administrador', 'administrador_albergue') OR u.rol::text IN ('administrador_albergue', 'coordinador_emergencias'))
          AND au.activo = true
        LIMIT 1
    """)
    fila_admin = session.execute(consulta_admin, {"albergue_id": id}).mappings().first()

    admin_a_cargo = None
    if fila_admin:
        admin_a_cargo = AdministradorACargo(
            id=fila_admin["id"],
            nombre=fila_admin["full_name"] or "Administrador Responsable",
            email=fila_admin["email"],
            rol=str(fila_admin["rol"] or "administrador_albergue"),
        )
    elif usuario_actual.is_superuser or str(usuario_actual.rol or "") in ("administrador_albergue", "coordinador_emergencias"):
        admin_a_cargo = AdministradorACargo(
            id=usuario_actual.id,
            nombre=usuario_actual.full_name or "Administrador Responsable",
            email=usuario_actual.email,
            rol=str(usuario_actual.rol or "administrador_albergue"),
        )

    # 2. Consultar lista nominal de personas albergadas activas
    consulta_personas = text("""
        SELECT
            id,
            folio_identificacion,
            nombre,
            apellido_paterno,
            apellido_materno,
            genero,
            dormitorio_asignado,
            numero_cama_colchoneta,
            estado_estancia,
            fecha_ingreso,
            condicion_medica,
            discapacidad,
            necesidad_especial
        FROM persona_refugiada
        WHERE albergue_id = :albergue_id
          AND estado_estancia IN ('albergado', 'salida_temporal')
        ORDER BY fecha_ingreso DESC
    """)
    filas_personas = (
        session.execute(consulta_personas, {"albergue_id": id}).mappings().fetchall()
    )

    # 3. Aplicar filtro de privacidad medica segun rol
    acceso_medico = puede_ver_datos_medicos(usuario_actual, id, session)
    lista_personas = []
    for p in filas_personas:
        nombre_completo = f"{p['nombre']} {p['apellido_paterno']}"
        if p.get("apellido_materno"):
            nombre_completo += f" {p['apellido_materno']}"

        lista_personas.append(
            PersonaAlbergadaItemDashboard(
                id=p["id"],
                folio_identificacion=p["folio_identificacion"],
                nombre_completo=nombre_completo,
                genero=p.get("genero"),
                dormitorio_asignado=p.get("dormitorio_asignado"),
                numero_cama_colchoneta=p.get("numero_cama_colchoneta"),
                estado_estancia=p["estado_estancia"],
                fecha_ingreso=p["fecha_ingreso"],
                condicion_medica=p.get("condicion_medica") if acceso_medico else None,
                discapacidad=p.get("discapacidad") if acceso_medico else None,
                necesidad_especial=p.get("necesidad_especial")
                if acceso_medico
                else None,
            )
        )

    # 4. Ensamblar respuesta estructurada
    return DashboardAlbergueRespuesta(
        albergue_id=fila_vista["albergue_id"],
        folio_identificador=fila_vista["folio_identificador"],
        nombre=fila_vista["nombre"],
        municipio=fila_vista["municipio"],
        localidad=fila_vista.get("localidad"),
        direccion=fila_vista["direccion"],
        estado_operativo=fila_vista["estado_operativo"],
        semaforo=fila_vista["semaforo"],
        fecha_ultimo_corte=fila_vista.get("fecha_ultimo_corte"),
        administrador_a_cargo=admin_a_cargo,
        infraestructura=ResumenInfraestructuraDashboard(
            capacidad_maxima=fila_vista["capacidad_maxima"],
            ocupacion_actual=fila_vista["ocupacion_actual"],
            cupo_disponible=fila_vista["cupo_disponible"],
            porcentaje_ocupacion=float(fila_vista["porcentaje_ocupacion"] or 0.0),
            semaforo=fila_vista["semaforo"],
            dormitorios=fila_vista["dormitorios"],
            banos=fila_vista["banos"],
            regaderas=fila_vista["regaderas"],
            cocina=fila_vista["cocina"],
            comedor=fila_vista["comedor"],
            consultorio=fila_vista["consultorio"],
            bodega=fila_vista["bodega"],
            salidas_emergencia=fila_vista["salidas_emergencia"],
            extintores_instalados=fila_vista["extintores_instalados"],
            accesos_silla_ruedas=fila_vista["accesos_silla_ruedas"],
            planta_electrica=fila_vista["planta_electrica"],
            sistema_agua=fila_vista["sistema_agua"],
            estado_inmueble=fila_vista["estado_inmueble"],
        ),
        recurso_humano=ResumenRecursoHumanoDashboard(
            personal_administracion=fila_vista["personal_administracion"],
            personal_medicos=fila_vista["personal_medicos"],
            personal_enfermeria=fila_vista["personal_enfermeria"],
            personal_psicologia=fila_vista["personal_psicologia"],
            personal_cocineros=fila_vista["personal_cocineros"],
            personal_limpieza=fila_vista["personal_limpieza"],
            personal_seguridad=fila_vista["personal_seguridad"],
            personal_voluntarios=fila_vista["personal_voluntarios"],
            total_personal_salud=fila_vista["total_personal_salud"],
        ),
        suministros=ResumenSuministrosDashboard(
            agua_potable_litros=float(fila_vista["agua_potable_litros"] or 0.0),
            agua_litros_por_persona=float(fila_vista["agua_litros_por_persona"] or 0.0),
            alerta_agua_critica=fila_vista["alerta_agua_critica"],
            raciones_alimentos=fila_vista["raciones_alimentos"],
            raciones_por_persona=float(fila_vista["raciones_por_persona"] or 0.0),
            alerta_alimentos_critica=fila_vista["alerta_alimentos_critica"],
            colchonetas_disponibles=fila_vista["colchonetas_disponibles"],
            alerta_colchonetas_deficit=fila_vista["alerta_colchonetas_deficit"],
            cobijas_disponibles=fila_vista["cobijas_disponibles"],
            kits_higiene_disponibles=fila_vista["kits_higiene_disponibles"],
            medicamentos_cajas=fila_vista["medicamentos_cajas"],
            material_curacion_paquetes=fila_vista["material_curacion_paquetes"],
            extintores_reserva=fila_vista["extintores_reserva"],
        ),
        personas_albergadas=lista_personas,
        total_personas_registradas=len(lista_personas),
    )


@router.post(
    "/{id}/ingreso-atomico",
    summary="Incremento atomico de ocupacion con validacion de capacidad maxima",
)
def registrar_ingreso_atomico(
    id: uuid.UUID,
    session: SessionDep,
    usuario_actual: CurrentUser,
) -> dict[str, Any]:
    """Ejecuta un UPDATE atomico que incrementa la ocupacion en 1 si no sobrepasa la capacidad maxima."""
    verificar_acceso_albergue(usuario_actual, id, session)

    sentencia = text("""
        UPDATE albergue
        SET ocupacion_actual = ocupacion_actual + 1,
            fecha_actualizacion = now()
        WHERE id = :id AND ocupacion_actual + 1 <= COALESCE((
            SELECT capacidad_maxima FROM inventario_infraestructura WHERE albergue_id = :id
        ), 999999)
        RETURNING ocupacion_actual;
    """)
    resultado = session.execute(sentencia, {"id": id}).scalar()
    session.commit()

    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El albergue ha alcanzado su capacidad maxima instalada. Rechazando ingreso.",
        )

    return {
        "mensaje": "Ingreso registrado exitosamente de forma atomica.",
        "albergue_id": id,
        "nueva_ocupacion_actual": resultado,
    }


@router.post("/{id}/egreso-atomico", summary="Decremento atomico de ocupacion")
def registrar_egreso_atomico(
    id: uuid.UUID,
    session: SessionDep,
    usuario_actual: CurrentUser,
) -> dict[str, Any]:
    """Ejecuta un UPDATE atomico que decrementa la ocupacion en 1 garantizando no bajar de 0."""
    verificar_acceso_albergue(usuario_actual, id, session)

    sentencia = text("""
        UPDATE albergue
        SET ocupacion_actual = GREATEST(0, ocupacion_actual - 1),
            fecha_actualizacion = now()
        WHERE id = :id
        RETURNING ocupacion_actual;
    """)
    resultado = session.execute(sentencia, {"id": id}).scalar()
    session.commit()

    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Albergue con identificador {id} no encontrado.",
        )

    return {
        "mensaje": "Egreso registrado exitosamente de forma atomica.",
        "albergue_id": id,
        "nueva_ocupacion_actual": resultado,
    }


# ==============================================================================
# GESTION ATOMICA DE INFRAESTRUCTURA (CONTRATO OFICIAL FRONTEND)
# ==============================================================================

AREAS_INFRAESTRUCTURA: dict[str, str] = {
    "dormitorios": "Dormitorios",
    "banos": "Baños",
    "regaderas": "Regaderas",
    "cocina": "Cocina",
    "comedor": "Comedor",
    "consultorio": "Consultorio Médico",
    "bodega": "Bodega",
    "salidas_emergencia": "Salidas de Emergencia",
    "extintores_instalados": "Extintores Instalados",
}


class AreaInfraestructura(BaseModel):
    """Representa un area administrable del albergue."""

    id: str = PydField(..., description="Nombre de columna en base de datos")
    nombre: str = PydField(..., description="Nombre legible para la UI")
    cantidad: int = PydField(..., ge=0, description="Cantidad entera no negativa")


class ConsultaInfraestructuraRespuesta(BaseModel):
    """Respuesta del endpoint GET /albergues/{id}/infraestructura."""

    areas: list[AreaInfraestructura]
    fechaActualizacion: str | None = None


class SolicitudAjusteArea(BaseModel):
    """Payload para POST /albergues/{id}/infraestructura/{areaId}/ajuste."""

    delta: int = PydField(..., description="Incremento (+1) o decremento (-1)")


class RespuestaAjusteArea(BaseModel):
    """Respuesta exitosa de ajuste atomico de infraestructura."""

    success: bool = True
    area: AreaInfraestructura


@router.get(
    "/{id}/infraestructura",
    response_model=ConsultaInfraestructuraRespuesta,
    summary="Consultar areas de infraestructura del albergue",
)
def consultar_infraestructura_albergue(
    id: uuid.UUID,
    session: SessionDep,
    usuario_actual: CurrentUser,
) -> Any:
    """Retorna las 9 areas administrables de infraestructura y su ultima fecha de actualizacion."""
    try:
        verificar_acceso_albergue(usuario_actual, id, session)
    except HTTPException as exc:
        if exc.status_code == status.HTTP_403_FORBIDDEN:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"code": "SIN_PERMISOS", "detail": str(exc.detail)},
            )
        raise exc

    consulta = text("""
        SELECT
            dormitorios, banos, regaderas, cocina, comedor,
            consultorio, bodega, salidas_emergencia, extintores_instalados,
            fecha_actualizacion
        FROM inventario_infraestructura
        WHERE albergue_id = :albergue_id
    """)
    fila = session.execute(consulta, {"albergue_id": id}).mappings().first()

    if not fila:
        albergue = session.get(Albergue, id)
        if not albergue:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "code": "ALBERGUE_NO_ENCONTRADO",
                    "detail": f"Albergue {id} no encontrado.",
                },
            )
        nueva_infra = InventarioInfraestructura(albergue_id=id)
        session.add(nueva_infra)
        session.commit()
        fila = session.execute(consulta, {"albergue_id": id}).mappings().first()

    areas = [
        AreaInfraestructura(id=col, nombre=nombre, cantidad=int(fila[col] or 0))
        for col, nombre in AREAS_INFRAESTRUCTURA.items()
    ]

    fecha_act = fila["fecha_actualizacion"]
    fecha_iso = fecha_act.isoformat() if fecha_act else None

    return ConsultaInfraestructuraRespuesta(
        areas=areas,
        fechaActualizacion=fecha_iso,
    )


@router.post(
    "/{id}/infraestructura/{area_id}/ajuste",
    response_model=RespuestaAjusteArea,
    summary="Ajuste atomico (+1 / -1) de un area de infraestructura",
)
def ajustar_area_infraestructura(
    id: uuid.UUID,
    area_id: str,
    solicitud: SolicitudAjusteArea,
    session: SessionDep,
    usuario_actual: CurrentUser,
) -> Any:
    """Ajusta atomicamente la cantidad de un area de infraestructura."""
    # 1. Validar permisos
    try:
        verificar_acceso_albergue(usuario_actual, id, session)
    except HTTPException as exc:
        if exc.status_code == status.HTTP_403_FORBIDDEN:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"code": "SIN_PERMISOS", "detail": str(exc.detail)},
            )
        raise exc

    # 2. Validar lista blanca contra inyeccion SQL
    area_columna = area_id.strip().lower()
    if area_columna not in AREAS_INFRAESTRUCTURA:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "code": "AREA_NO_ENCONTRADA",
                "detail": f"El area '{area_id}' no es valida.",
            },
        )

    # 3. Validar delta distinto de cero
    if solicitud.delta == 0:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": "CANTIDAD_INVALIDA",
                "detail": "El delta no puede ser cero.",
            },
        )

    nombre_area = AREAS_INFRAESTRUCTURA[area_columna]

    # 4. Asegurar existencia de inventario
    fila_previa = (
        session.execute(
            text(
                f"SELECT {area_columna} FROM inventario_infraestructura WHERE albergue_id = :albergue_id FOR UPDATE"
            ),
            {"albergue_id": id},
        )
        .mappings()
        .first()
    )

    if not fila_previa:
        albergue = session.get(Albergue, id)
        if not albergue:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "code": "ALBERGUE_NO_ENCONTRADO",
                    "detail": f"Albergue {id} no encontrado.",
                },
            )
        nueva_infra = InventarioInfraestructura(albergue_id=id)
        session.add(nueva_infra)
        session.commit()
        fila_previa = (
            session.execute(
                text(
                    f"SELECT {area_columna} FROM inventario_infraestructura WHERE albergue_id = :albergue_id FOR UPDATE"
                ),
                {"albergue_id": id},
            )
            .mappings()
            .first()
        )

    cantidad_actual = int(fila_previa[area_columna] or 0)

    # 5. UPDATE atomico con control de cota minima >= 0
    sentencia_update = text(f"""
        UPDATE inventario_infraestructura
        SET {area_columna} = {area_columna} + :delta,
            fecha_actualizacion = NOW()
        WHERE albergue_id = :albergue_id
          AND ({area_columna} + :delta) >= 0
        RETURNING {area_columna};
    """)
    resultado = session.execute(
        sentencia_update, {"albergue_id": id, "delta": solicitud.delta}
    ).scalar()

    if resultado is None:
        session.rollback()
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": "CANTIDAD_INVALIDA",
                "area": {
                    "id": area_columna,
                    "nombre": nombre_area,
                    "cantidad": cantidad_actual,
                },
            },
        )

    session.commit()

    return RespuestaAjusteArea(
        success=True,
        area=AreaInfraestructura(
            id=area_columna, nombre=nombre_area, cantidad=int(resultado)
        ),
    )


# ==============================================================================
# GESTION OPERATIVA DE PERSONAL POR ALBERGUE (FUENTE DE VERDAD: albergue_usuario)
# ==============================================================================


@router.get(
    "/{id}/personal",
    response_model=list[PersonalAsignadoDetalle],
    summary="Listar personal comisionado al albergue (Fuente de verdad operativa)",
)
def listar_personal_albergue(
    id: uuid.UUID,
    session: SessionDep,
    usuario_actual: CurrentUser,
) -> Any:
    """Consulta la lista de personal comisionado al albergue con rol, area, turno y estado activo."""
    verificar_acceso_albergue(usuario_actual, id, session)
    consulta = text("""
        SELECT
            au.id,
            au.albergue_id,
            au.usuario_id,
            u.email,
            u.full_name AS nombre_completo,
            au.rol,
            au.area,
            au.turno,
            au.activo,
            au.fecha_asignacion
        FROM albergue_usuario au
        JOIN "user" u ON u.id = au.usuario_id
        WHERE au.albergue_id = :albergue_id
        ORDER BY au.activo DESC, au.fecha_asignacion DESC
    """)
    filas = session.execute(consulta, {"albergue_id": id}).mappings().fetchall()
    return [PersonalAsignadoDetalle(**f) for f in filas]


@router.post(
    "/{id}/personal",
    response_model=AlbergueUsuarioPublic,
    summary="Asignar o comisionar personal operativo al albergue",
)
def asignar_personal_albergue(
    id: uuid.UUID,
    datos_asignacion: AlbergueUsuarioCreate,
    session: SessionDep,
    usuario_actual: CurrentUser,
) -> Any:
    """Registra una nueva comision de usuario en el albergue especificando rol, area y turno."""
    verificar_acceso_albergue(usuario_actual, id, session)

    # Asegurar que el albergue corresponda al de la ruta
    if datos_asignacion.albergue_id != id:
        datos_asignacion.albergue_id = id

    nueva_asignacion = AlbergueUsuario.model_validate(datos_asignacion)
    session.add(nueva_asignacion)
    session.commit()
    session.refresh(nueva_asignacion)
    return nueva_asignacion


@router.patch(
    "/{id}/personal/{asignacion_id}",
    response_model=AlbergueUsuarioPublic,
    summary="Actualizar rol, area, turno o estatus de asignacion operativa",
)
def actualizar_asignacion_personal(
    id: uuid.UUID,
    asignacion_id: uuid.UUID,
    datos_actualizacion: AlbergueUsuarioUpdate,
    session: SessionDep,
    usuario_actual: CurrentUser,
) -> Any:
    """Actualiza rol especifico, area, turno o desactiva la asignacion de un brigadista/operador."""
    verificar_acceso_albergue(usuario_actual, id, session)
    asignacion = session.get(AlbergueUsuario, asignacion_id)
    if not asignacion or asignacion.albergue_id != id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignacion operativa no encontrada para este albergue.",
        )

    datos_dict = datos_actualizacion.model_dump(exclude_unset=True)
    asignacion.sqlmodel_update(datos_dict)
    session.add(asignacion)
    session.commit()
    session.refresh(asignacion)
    return asignacion


@router.delete(
    "/{id}/personal/{asignacion_id}",
    summary="Desactivar asignacion de personal en el albergue",
)
def desactivar_asignacion_personal(
    id: uuid.UUID,
    asignacion_id: uuid.UUID,
    session: SessionDep,
    usuario_actual: CurrentUser,
) -> dict[str, Any]:
    """Marca como inactiva la asignacion operativa de un usuario en el albergue."""
    verificar_acceso_albergue(usuario_actual, id, session)
    asignacion = session.get(AlbergueUsuario, asignacion_id)
    if not asignacion or asignacion.albergue_id != id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignacion operativa no encontrada para este albergue.",
        )

    asignacion.activo = False
    session.add(asignacion)
    session.commit()
    return {
        "mensaje": "Asignacion operativa desactivada exitosamente.",
        "asignacion_id": asignacion_id,
        "activo": False,
    }


# ==============================================================================
# INGRESO FAMILIAR INTELIGENTE (ENDPOINT PRINCIPAL PARA EL FRONTEND)
# ==============================================================================


class IntegranteFamiliarEntrada(BaseModel):
    """Esquema de entrada por cada persona que el frontend envia en el array.

    Soporta camelCase y snake_case indistintamente para flexibilidad
    del equipo de frontend.
    """

    model_config = ConfigDict(populate_by_name=True)

    nombre: str = PydField(
        ...,
        min_length=1,
        max_length=150,
        description="Nombre(s) de pila de la persona",
    )
    apellido_paterno: str = PydField(
        ...,
        min_length=1,
        max_length=150,
        validation_alias=AliasChoices("apellido_paterno", "apellidoPaterno"),
        description="Primer apellido",
    )
    apellido_materno: str | None = PydField(
        default=None,
        max_length=150,
        validation_alias=AliasChoices("apellido_materno", "apellidoMaterno"),
        description="Segundo apellido (opcional)",
    )
    fecha_nacimiento: date = PydField(
        ...,
        validation_alias=AliasChoices("fecha_nacimiento", "fechaNacimiento"),
        description="Fecha de nacimiento en formato YYYY-MM-DD",
    )
    padecimiento: str | None = PydField(
        default=None,
        max_length=500,
        validation_alias=AliasChoices(
            "padecimiento", "condicion_medica", "condicionMedica"
        ),
        description="Condicion medica o padecimiento reportado (opcional)",
    )
    discapacidad: bool = PydField(
        default=False,
        validation_alias=AliasChoices("discapacidad", "esDiscapacitado"),
        description="Indica si la persona presenta alguna discapacidad",
    )
    embarazo: bool = PydField(
        default=False,
        validation_alias=AliasChoices("embarazo", "embarazada", "estaEmbarazada"),
        description="Indica si la persona se encuentra en periodo de gestacion o embarazo",
    )


class SolicitudIngresoFamiliar(BaseModel):
    """Payload que el frontend envia para registrar un grupo de personas."""

    model_config = ConfigDict(populate_by_name=True)

    personas: list[IntegranteFamiliarEntrada] = PydField(
        ...,
        min_length=1,
        description="Array con los datos de cada integrante del grupo",
    )
    comunidad_origen: str | None = PydField(
        default=None,
        max_length=255,
        validation_alias=AliasChoices("comunidad_origen", "comunidadOrigen"),
        description="Comunidad o colonia de procedencia del grupo",
    )


class PersonaRegistradaRespuesta(BaseModel):
    """Datos de confirmacion de cada persona registrada exitosamente."""

    id: str
    folio_identificacion: str
    nombre_completo: str
    edad: int
    menor_de_edad: bool
    adulto_mayor: bool
    discapacidad: bool = False
    embarazo: bool = False
    condicion_medica: str | None = None


class RespuestaIngresoFamiliar(BaseModel):
    """Respuesta consolidada del registro de ingreso familiar."""

    mensaje: str
    grupo_familiar_id: str
    codigo_familia: str
    albergue_id: str
    total_ingresados: int
    nueva_ocupacion: int
    personas_registradas: list[PersonaRegistradaRespuesta]


def _calcular_edad(fecha_nacimiento: date) -> int:
    """Calcula la edad actual en anios a partir de la fecha de nacimiento."""
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return max(edad, 0)


def _generar_codigo_familia(albergue_id: uuid.UUID) -> str:
    """Genera un codigo de familia unico con formato legible para trazabilidad."""
    ahora = datetime.now(UTC)
    fragmento_hex = uuid.uuid4().hex[:4].upper()
    fecha_corta = ahora.strftime("%Y%m%d")
    prefijo_albergue = str(albergue_id)[:4].upper()
    return f"FAM-{fecha_corta}-{prefijo_albergue}-{fragmento_hex}"


def _generar_folio_refugiado(albergue_id: uuid.UUID) -> str:
    """Genera un folio unico de identificacion para cada persona refugiada."""
    fragmento_albergue = str(albergue_id)[:4].upper()
    fragmento_unico = uuid.uuid4().hex[:6].upper()
    return f"REF-{fragmento_albergue}-{fragmento_unico}"


@router.post(
    "/{id}/ingreso-familiar",
    response_model=RespuestaIngresoFamiliar,
    summary="Ingreso inteligente de grupo familiar o persona individual al albergue",
)
def registrar_ingreso_familiar(
    id: uuid.UUID,
    solicitud: SolicitudIngresoFamiliar,
    session: SessionDep,
    usuario_actual: CurrentUser,
) -> Any:
    """Registra el ingreso de un grupo de personas (o individuo) al albergue.

    Flujo transaccional atomico (todo-o-nada):
    1. Valida que el usuario tenga acceso al albergue.
    2. Verifica que haya capacidad suficiente para TODO el grupo.
       Si no alcanza, rechaza la transaccion completa (no se separa a la familia).
    3. Crea el GrupoFamiliar (incluso si es 1 sola persona = unipersonal).
    4. Registra cada PersonaRefugiada con inferencia automatica de vulnerabilidades
       por edad (menor_de_edad, adulto_mayor) y condicion medica.
    5. Incrementa la ocupacion del albergue en +N de forma atomica.
    6. Retorna la confirmacion con folios, edades y alertas de vulnerabilidad.
    """
    verificar_acceso_albergue(usuario_actual, id, session)

    total_personas = len(solicitud.personas)

    # =====================================================================
    # PASO 1: VERIFICAR CAPACIDAD ATOMICAMENTE (BLINDAJE ANTES DE INSERTAR)
    # =====================================================================
    # Bloquear fila del albergue para evitar condiciones de carrera
    consulta_albergue = text("""
        SELECT ocupacion_actual
        FROM albergue
        WHERE id = :albergue_id
        FOR UPDATE
    """)
    fila_albergue = (
        session.execute(consulta_albergue, {"albergue_id": id}).mappings().first()
    )

    if not fila_albergue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Albergue con identificador {id} no encontrado en el sistema.",
        )

    ocupacion_actual = int(fila_albergue["ocupacion_actual"])

    # Obtener capacidad maxima sin bloqueo (tabla auxiliar)
    consulta_capacidad = text("""
        SELECT COALESCE(capacidad_maxima, 999999) AS capacidad_maxima
        FROM inventario_infraestructura
        WHERE albergue_id = :albergue_id
    """)
    fila_cap = (
        session.execute(consulta_capacidad, {"albergue_id": id}).mappings().first()
    )
    capacidad_maxima = int(fila_cap["capacidad_maxima"]) if fila_cap else 999999
    cupo_disponible = capacidad_maxima - ocupacion_actual

    if total_personas > cupo_disponible:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Capacidad insuficiente para el grupo completo. "
                f"Cupo disponible: {cupo_disponible} lugares. "
                f"Integrantes del grupo: {total_personas}. "
                f"No se permite separar a la familia. "
                f"Considere reubicar al grupo a otro albergue con mayor disponibilidad."
            ),
        )

    # =====================================================================
    # PASO 2: CREAR GRUPO FAMILIAR
    # =====================================================================
    primer_integrante = solicitud.personas[0]
    nombre_referente = (
        f"{primer_integrante.nombre} {primer_integrante.apellido_paterno}"
    )
    if primer_integrante.apellido_materno:
        nombre_referente += f" {primer_integrante.apellido_materno}"

    # Consolidar padecimientos del grupo para necesidades_especiales
    padecimientos_grupo = [
        p.padecimiento
        for p in solicitud.personas
        if p.padecimiento and p.padecimiento.strip()
    ]
    necesidades_texto = "; ".join(padecimientos_grupo) if padecimientos_grupo else None

    codigo_familia = _generar_codigo_familia(id)
    grupo_id = uuid.uuid4()

    session.execute(
        text("""
        INSERT INTO grupo_familiar (
            id, albergue_id, codigo_familia, nombre_referente,
            total_integrantes, comunidad_origen, necesidades_especiales,
            fecha_registro
        ) VALUES (
            :id, :albergue_id, :codigo_familia, :nombre_referente,
            :total_integrantes, :comunidad_origen, :necesidades_especiales,
            NOW()
        )
    """),
        {
            "id": grupo_id,
            "albergue_id": id,
            "codigo_familia": codigo_familia,
            "nombre_referente": nombre_referente,
            "total_integrantes": total_personas,
            "comunidad_origen": solicitud.comunidad_origen,
            "necesidades_especiales": necesidades_texto,
        },
    )

    # =====================================================================
    # PASO 3: REGISTRAR CADA PERSONA CON INFERENCIA DE VULNERABILIDADES
    # =====================================================================
    personas_registradas: list[PersonaRegistradaRespuesta] = []

    for persona in solicitud.personas:
        persona_id = uuid.uuid4()
        folio = _generar_folio_refugiado(id)
        edad = _calcular_edad(persona.fecha_nacimiento)

        es_menor = edad < 18
        es_adulto_mayor = edad >= 60

        # Nombre completo para la respuesta
        nombre_completo = f"{persona.nombre} {persona.apellido_paterno}"
        if persona.apellido_materno:
            nombre_completo += f" {persona.apellido_materno}"

        # Convertir date a datetime para el campo sa_type DateTime(timezone=True)
        fecha_nac_dt = datetime(
            persona.fecha_nacimiento.year,
            persona.fecha_nacimiento.month,
            persona.fecha_nacimiento.day,
            tzinfo=UTC,
        )

        session.execute(
            text("""
            INSERT INTO persona_refugiada (
                id, albergue_id, grupo_familiar_id, folio_identificacion,
                nombre, apellido_paterno, apellido_materno,
                fecha_nacimiento, condicion_medica,
                discapacidad, embarazo,
                menor_de_edad, adulto_mayor,
                estado_estancia, registrado_por_id, fecha_ingreso
            ) VALUES (
                :id, :albergue_id, :grupo_familiar_id, :folio,
                :nombre, :apellido_paterno, :apellido_materno,
                :fecha_nacimiento, :condicion_medica,
                :discapacidad, :embarazo,
                :menor_de_edad, :adulto_mayor,
                'albergado', :registrado_por_id, NOW()
            )
        """),
            {
                "id": persona_id,
                "albergue_id": id,
                "grupo_familiar_id": grupo_id,
                "folio": folio,
                "nombre": persona.nombre,
                "apellido_paterno": persona.apellido_paterno,
                "apellido_materno": persona.apellido_materno,
                "fecha_nacimiento": fecha_nac_dt,
                "condicion_medica": persona.padecimiento,
                "discapacidad": persona.discapacidad,
                "embarazo": persona.embarazo,
                "menor_de_edad": es_menor,
                "adulto_mayor": es_adulto_mayor,
                "registrado_por_id": usuario_actual.id,
            },
        )

        personas_registradas.append(
            PersonaRegistradaRespuesta(
                id=str(persona_id),
                folio_identificacion=folio,
                nombre_completo=nombre_completo,
                edad=edad,
                menor_de_edad=es_menor,
                adulto_mayor=es_adulto_mayor,
                discapacidad=persona.discapacidad,
                embarazo=persona.embarazo,
                condicion_medica=persona.padecimiento,
            )
        )

    # =====================================================================
    # PASO 4: INCREMENTO ATOMICO DE OCUPACION (+N)
    # =====================================================================
    resultado_ocupacion = session.execute(
        text("""
        UPDATE albergue
        SET ocupacion_actual = ocupacion_actual + :cantidad,
            fecha_actualizacion = NOW()
        WHERE id = :albergue_id
        RETURNING ocupacion_actual
    """),
        {
            "cantidad": total_personas,
            "albergue_id": id,
        },
    ).scalar()

    # =====================================================================
    # COMMIT TRANSACCIONAL: TODO-O-NADA
    # =====================================================================
    session.commit()

    return RespuestaIngresoFamiliar(
        mensaje=(
            f"Ingreso exitoso. {total_personas} persona(s) registrada(s) "
            f"en el grupo familiar {codigo_familia}."
        ),
        grupo_familiar_id=str(grupo_id),
        codigo_familia=codigo_familia,
        albergue_id=str(id),
        total_ingresados=total_personas,
        nueva_ocupacion=resultado_ocupacion,
        personas_registradas=personas_registradas,
    )
