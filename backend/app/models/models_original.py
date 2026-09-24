import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Optional

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel


def obtener_fecha_hora_utc() -> datetime:
    """Retorna la fecha y hora actual en zona horaria UTC."""
    return datetime.now(UTC)


# Alias de compatibilidad con plantillas previas
get_datetime_utc = obtener_fecha_hora_utc


# ==============================================================================
# ENUMERACIONES DE ROLES OPERATIVOS, AREAS Y ESTATUS (HACKATEC)
# ==============================================================================


class RolOperativo(StrEnum):
    """Tres niveles de privilegios operativos para la plataforma de albergues."""

    ADMINISTRADOR_ALBERGUE = "administrador_albergue"
    RESPONSABLE_AREA = "responsable_area"
    PERSONAL_OPERATIVO = "personal_operativo"


class AreaFuncional(StrEnum):
    """Areas operativas funcionales dentro del albergue de proteccion civil."""

    RECEPCION_REGISTRO = "recepcion_registro"
    ALOJAMIENTO = "alojamiento"
    BODEGA_SUMINISTROS = "bodega_suministros"
    SALUD_MEDICA = "salud_medica"
    ALIMENTACION = "alimentacion"
    SEGURIDAD = "seguridad"
    PSICOLOGIA = "psicologia"
    LIMPIEZA_MANTENIMIENTO = "limpieza_mantenimiento"
    GENERAL = "general"


class EstadoEstancia(StrEnum):
    """Estatus del ciclo de estancia de una persona albergada."""

    ALBERGADO = "albergado"
    SALIDA_TEMPORAL = "salida_temporal"
    EGRESO_DEFINITIVO = "egreso_definitivo"
    TRASLADADO = "trasladado"


class EstadoOperativoAlbergue(StrEnum):
    """Estados del ciclo de vida operativo del refugio temporal."""

    PLANEADO = "planeado"
    DISPONIBLE = "disponible"
    ACTIVADO = "activado"
    LLENO = "lleno"
    CERRADO = "cerrado"
    FUERA_DE_SERVICIO = "fuera_de_servicio"


# ==============================================================================
# MODELOS DE USUARIO Y AUTENTICACION
# ==============================================================================


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None
    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=obtener_fecha_hora_utc,
        sa_type=DateTime(timezone=True),
    )
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    albergues_a_cargo: list["Albergue"] = Relationship(back_populates="responsable")
    asignaciones_albergue: list["AlbergueUsuario"] = Relationship(
        back_populates="usuario", cascade_delete=True
    )


class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# ==============================================================================
# MODELOS DE ELEMENTOS (ITEMS) DE PRUEBA / PLANTILLA
# ==============================================================================


class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=obtener_fecha_hora_utc,
        sa_type=DateTime(timezone=True),
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# ==============================================================================
# MODELOS DE SEGURIDAD Y TOKEN
# ==============================================================================


class Message(SQLModel):
    message: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


# ==============================================================================
# 1. MODELO DE ALBERGUE (ENTIDAD PRINCIPAL DE PROTECCION CIVIL)
# ==============================================================================


class AlbergueBase(SQLModel):
    folio_identificador: str = Field(unique=True, index=True, max_length=50)
    nombre: str = Field(index=True, max_length=255)
    direccion: str = Field(max_length=500)
    municipio: str = Field(index=True, max_length=150)
    localidad: str | None = Field(default=None, max_length=150)
    estado_republica: str = Field(default="Nacional", max_length=100)
    latitud: float | None = Field(default=None)
    longitud: float | None = Field(default=None)
    tipo_inmueble: str | None = Field(default=None, max_length=100)
    telefono_contacto: str | None = Field(default=None, max_length=50)
    admite_mascotas: bool = Field(default=False)
    estado_operativo: EstadoOperativoAlbergue = Field(
        default=EstadoOperativoAlbergue.ACTIVADO, index=True
    )
    observaciones: str | None = Field(default=None, max_length=1000)


class AlbergueCreate(AlbergueBase):
    responsable_id: uuid.UUID | None = None


class AlbergueUpdate(SQLModel):
    folio_identificador: str | None = Field(default=None, max_length=50)
    nombre: str | None = Field(default=None, max_length=255)
    direccion: str | None = Field(default=None, max_length=500)
    municipio: str | None = Field(default=None, max_length=150)
    localidad: str | None = Field(default=None, max_length=150)
    estado_republica: str | None = Field(default=None, max_length=100)
    latitud: float | None = None
    longitud: float | None = None
    tipo_inmueble: str | None = Field(default=None, max_length=100)
    telefono_contacto: str | None = Field(default=None, max_length=50)
    admite_mascotas: bool | None = None
    estado_operativo: EstadoOperativoAlbergue | None = None
    observaciones: str | None = Field(default=None, max_length=1000)
    responsable_id: uuid.UUID | None = None


class Albergue(AlbergueBase, table=True):
    __tablename__: str = "albergue"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    responsable_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    fecha_registro: datetime = Field(
        default_factory=obtener_fecha_hora_utc,
        sa_type=DateTime(timezone=True),
    )
    fecha_actualizacion: datetime = Field(
        default_factory=obtener_fecha_hora_utc,
        sa_type=DateTime(timezone=True),
    )

    # Relaciones cardinales 1 a 1
    responsable: User | None = Relationship(back_populates="albergues_a_cargo")
    inventario_suministros: Optional["InventarioSuministro"] = Relationship(
        back_populates="albergue",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False},
    )
    inventario_infraestructura: Optional["InventarioInfraestructura"] = Relationship(
        back_populates="albergue",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False},
    )
    inventario_recursos_humanos: Optional["InventarioRecursoHumano"] = Relationship(
        back_populates="albergue",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False},
    )

    # Relaciones 1 a N operativas
    personal_asignado: list["AlbergueUsuario"] = Relationship(
        back_populates="albergue", cascade_delete=True
    )
    personas_refugiadas: list["PersonaRefugiada"] = Relationship(
        back_populates="albergue", cascade_delete=True
    )
    grupos_familiares: list["GrupoFamiliar"] = Relationship(
        back_populates="albergue", cascade_delete=True
    )


class AlberguePublic(AlbergueBase):
    id: uuid.UUID
    responsable_id: uuid.UUID | None = None
    fecha_registro: datetime
    fecha_actualizacion: datetime


class AlberguesPublic(SQLModel):
    datos: list[AlberguePublic]
    total: int


# ==============================================================================
# 2. TABLA INTERMEDIA: ALBERGUE_USUARIO (ROLES DELEGADOS POR ALBERGUE)
# ==============================================================================


class AlbergueUsuarioBase(SQLModel):
    albergue_id: uuid.UUID = Field(
        foreign_key="albergue.id", index=True, ondelete="CASCADE"
    )
    usuario_id: uuid.UUID = Field(foreign_key="user.id", index=True, ondelete="CASCADE")
    rol: RolOperativo = Field(default=RolOperativo.PERSONAL_OPERATIVO, index=True)
    area: AreaFuncional = Field(default=AreaFuncional.GENERAL, index=True)
    activo: bool = Field(default=True)


class AlbergueUsuarioCreate(AlbergueUsuarioBase):
    pass


class AlbergueUsuarioUpdate(SQLModel):
    rol: RolOperativo | None = None
    area: AreaFuncional | None = None
    activo: bool | None = None


class AlbergueUsuario(AlbergueUsuarioBase, table=True):
    __tablename__: str = "albergue_usuario"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_asignacion: datetime = Field(
        default_factory=obtener_fecha_hora_utc,
        sa_type=DateTime(timezone=True),
    )

    albergue: Albergue | None = Relationship(back_populates="personal_asignado")
    usuario: User | None = Relationship(back_populates="asignaciones_albergue")


class AlbergueUsuarioPublic(AlbergueUsuarioBase):
    id: uuid.UUID
    fecha_asignacion: datetime


# ==============================================================================
# 3. NUCLEO DE REGISTRO: GRUPO FAMILIAR
# ==============================================================================


class GrupoFamiliarBase(SQLModel):
    albergue_id: uuid.UUID = Field(
        foreign_key="albergue.id", index=True, ondelete="CASCADE"
    )
    codigo_familia: str = Field(index=True, max_length=50)
    nombre_referente: str = Field(max_length=255)
    total_integrantes: int = Field(default=1)
    comunidad_origen: str | None = Field(default=None, max_length=255)
    necesidades_especiales: str | None = Field(default=None, max_length=500)


class GrupoFamiliarCreate(GrupoFamiliarBase):
    pass


class GrupoFamiliarUpdate(SQLModel):
    codigo_familia: str | None = Field(default=None, max_length=50)
    nombre_referente: str | None = Field(default=None, max_length=255)
    total_integrantes: int | None = None
    comunidad_origen: str | None = Field(default=None, max_length=255)
    necesidades_especiales: str | None = Field(default=None, max_length=500)


class GrupoFamiliar(GrupoFamiliarBase, table=True):
    __tablename__: str = "grupo_familiar"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_registro: datetime = Field(
        default_factory=obtener_fecha_hora_utc,
        sa_type=DateTime(timezone=True),
    )

    albergue: Albergue | None = Relationship(back_populates="grupos_familiares")
    integrantes: list["PersonaRefugiada"] = Relationship(
        back_populates="grupo_familiar"
    )


class GrupoFamiliarPublic(GrupoFamiliarBase):
    id: uuid.UUID
    fecha_registro: datetime


# ==============================================================================
# 4. TABLA DE PERSONAS REFUGIADAS (CONTROL ADMINISTRATIVO ENTRADA / SALIDA)
# ==============================================================================


class PersonaRefugiadaBase(SQLModel):
    albergue_id: uuid.UUID = Field(
        foreign_key="albergue.id", index=True, ondelete="CASCADE"
    )
    grupo_familiar_id: uuid.UUID | None = Field(
        default=None, foreign_key="grupo_familiar.id", index=True, ondelete="SET NULL"
    )
    folio_identificacion: str = Field(unique=True, index=True, max_length=50)
    nombre: str = Field(max_length=150)
    apellido_paterno: str = Field(max_length=150)
    apellido_materno: str | None = Field(default=None, max_length=150)
    curp: str | None = Field(default=None, max_length=20, index=True)
    fecha_nacimiento: datetime | None = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    genero: str | None = Field(default=None, max_length=30)
    municipio_origen: str | None = Field(default=None, max_length=150)
    localidad_origen: str | None = Field(default=None, max_length=150)
    telefono_contacto: str | None = Field(default=None, max_length=50)
    contacto_emergencia_nombre: str | None = Field(default=None, max_length=255)
    contacto_emergencia_telefono: str | None = Field(default=None, max_length=50)

    # Vulnerabilidades identificadas
    condicion_medica: str | None = Field(default=None, max_length=500)
    discapacidad: bool = Field(default=False)
    embarazo: bool = Field(default=False)
    adulto_mayor: bool = Field(default=False)
    menor_de_edad: bool = Field(default=False)
    necesidad_especial: str | None = Field(default=None, max_length=500)

    # Asignacion de espacio físico
    dormitorio_asignado: str | None = Field(default=None, max_length=100)
    numero_cama_colchoneta: str | None = Field(default=None, max_length=50)

    # Estatus de estancia y control de egreso
    estado_estancia: EstadoEstancia = Field(
        default=EstadoEstancia.ALBERGADO, index=True
    )
    motivo_salida: str | None = Field(default=None, max_length=255)
    destino_salida: str | None = Field(default=None, max_length=255)
    observaciones: str | None = Field(default=None, max_length=1000)


class PersonaRefugiadaCreate(PersonaRefugiadaBase):
    registrado_por_id: uuid.UUID | None = None


class PersonaRefugiadaUpdate(SQLModel):
    nombre: str | None = Field(default=None, max_length=150)
    apellido_paterno: str | None = Field(default=None, max_length=150)
    apellido_materno: str | None = Field(default=None, max_length=150)
    curp: str | None = Field(default=None, max_length=20)
    fecha_nacimiento: datetime | None = None
    genero: str | None = Field(default=None, max_length=30)
    municipio_origen: str | None = Field(default=None, max_length=150)
    localidad_origen: str | None = Field(default=None, max_length=150)
    telefono_contacto: str | None = Field(default=None, max_length=50)
    contacto_emergencia_nombre: str | None = Field(default=None, max_length=255)
    contacto_emergencia_telefono: str | None = Field(default=None, max_length=50)
    condicion_medica: str | None = Field(default=None, max_length=500)
    discapacidad: bool | None = None
    embarazo: bool | None = None
    adulto_mayor: bool | None = None
    menor_de_edad: bool | None = None
    necesidad_especial: str | None = Field(default=None, max_length=500)
    dormitorio_asignado: str | None = Field(default=None, max_length=100)
    numero_cama_colchoneta: str | None = Field(default=None, max_length=50)
    estado_estancia: EstadoEstancia | None = None
    fecha_salida: datetime | None = None
    motivo_salida: str | None = Field(default=None, max_length=255)
    destino_salida: str | None = Field(default=None, max_length=255)
    observaciones: str | None = Field(default=None, max_length=1000)
    egreso_por_id: uuid.UUID | None = None


class RegistroSalidaRefugiado(SQLModel):
    """Esquema especializado para la delegacion del tramite administrativo de salida."""

    fecha_salida: datetime | None = None
    motivo_salida: str = Field(max_length=255)
    destino_salida: str | None = Field(default=None, max_length=255)
    observaciones: str | None = Field(default=None, max_length=1000)
    estado_estancia: EstadoEstancia = EstadoEstancia.EGRESO_DEFINITIVO


class PersonaRefugiada(PersonaRefugiadaBase, table=True):
    __tablename__: str = "persona_refugiada"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_ingreso: datetime = Field(
        default_factory=obtener_fecha_hora_utc,
        sa_type=DateTime(timezone=True),
    )
    fecha_salida: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
    )
    registrado_por_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    egreso_por_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )

    albergue: Albergue | None = Relationship(back_populates="personas_refugiadas")
    grupo_familiar: GrupoFamiliar | None = Relationship(back_populates="integrantes")
    registrado_por: User | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[PersonaRefugiada.registrado_por_id]"}
    )
    egreso_por: User | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[PersonaRefugiada.egreso_por_id]"}
    )


class PersonaRefugiadaPublic(PersonaRefugiadaBase):
    id: uuid.UUID
    fecha_ingreso: datetime
    fecha_salida: datetime | None = None
    registrado_por_id: uuid.UUID | None = None
    egreso_por_id: uuid.UUID | None = None


class PersonasRefugiadasPublic(SQLModel):
    datos: list[PersonaRefugiadaPublic]
    total: int


# ==============================================================================
# 5. INVENTARIO DE SUMINISTROS (18 CAMPOS ESPECIFICOS DE PROTECCION CIVIL)
# ==============================================================================


class InventarioSuministroBase(SQLModel):
    agua_potable: float = Field(
        default=0.0, description="Litros disponibles de agua potable"
    )
    alimentos_no_perecederos: int = Field(
        default=0, description="Raciones o unidades de alimentos no perecederos"
    )
    formula_infantil: int = Field(
        default=0, description="Latas o unidades de formula infantil"
    )
    medicamentos_basicos: int = Field(
        default=0, description="Unidades o cajas de medicamentos basicos"
    )
    material_curacion: int = Field(
        default=0, description="Kits o paquetes de material de curacion"
    )
    cobijas: int = Field(default=0, description="Piezas de cobijas")
    colchonetas: int = Field(default=0, description="Piezas de colchonetas")
    ropa: int = Field(default=0, description="Prendas o paquetes de ropa limpia")
    kits_higiene: int = Field(default=0, description="Kits personales de higiene")
    panales: int = Field(
        default=0, description="Paquetes de panales para infantes o adultos"
    )
    cubrebocas: int = Field(default=0, description="Piezas o cajas de cubrebocas")
    productos_limpieza: int = Field(
        default=0, description="Unidades de articulos de limpieza general"
    )
    bolsas_residuos: int = Field(
        default=0, description="Paquetes o rollos de bolsas para residuos"
    )
    linternas: int = Field(default=0, description="Unidades operativas de linternas")
    pilas: int = Field(default=0, description="Piezas o paquetes de pilas")
    extintores: int = Field(default=0, description="Extintores en reserva o almacen")
    herramientas: int = Field(
        default=0, description="Juegos o piezas de herramientas basicas"
    )
    material_oficina: int = Field(
        default=0, description="Material de oficina para registro y censo"
    )


class InventarioSuministroCreate(InventarioSuministroBase):
    albergue_id: uuid.UUID


class InventarioSuministroUpdate(SQLModel):
    agua_potable: float | None = None
    alimentos_no_perecederos: int | None = None
    formula_infantil: int | None = None
    medicamentos_basicos: int | None = None
    material_curacion: int | None = None
    cobijas: int | None = None
    colchonetas: int | None = None
    ropa: int | None = None
    kits_higiene: int | None = None
    panales: int | None = None
    cubrebocas: int | None = None
    productos_limpieza: int | None = None
    bolsas_residuos: int | None = None
    linternas: int | None = None
    pilas: int | None = None
    extintores: int | None = None
    herramientas: int | None = None
    material_oficina: int | None = None


class InventarioSuministro(InventarioSuministroBase, table=True):
    __tablename__: str = "inventario_suministro"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    albergue_id: uuid.UUID = Field(
        foreign_key="albergue.id", unique=True, index=True, ondelete="CASCADE"
    )
    fecha_actualizacion: datetime = Field(
        default_factory=obtener_fecha_hora_utc,
        sa_type=DateTime(timezone=True),
    )

    albergue: Albergue | None = Relationship(back_populates="inventario_suministros")


class InventarioSuministroPublic(InventarioSuministroBase):
    id: uuid.UUID
    albergue_id: uuid.UUID
    fecha_actualizacion: datetime


# ==============================================================================
# 6. INVENTARIO DE INFRAESTRUCTURA (14 CAMPOS DE CAPACIDAD Y SERVICIOS)
# ==============================================================================


class InventarioInfraestructuraBase(SQLModel):
    capacidad_maxima: int = Field(
        default=0, description="Capacidad maxima total de personas albergadas"
    )
    dormitorios: int = Field(
        default=0, description="Dormitorios o areas de descanso delimitadas"
    )
    banos: int = Field(
        default=0, description="Numero de sanitarios o banos habilitados"
    )
    regaderas: int = Field(default=0, description="Numero de regaderas funcionales")
    cocina: int = Field(
        default=0, description="Numero o modulos de cocinas habilitadas"
    )
    comedor: int = Field(
        default=0, description="Numero de comedores o capacidad de comensales"
    )
    consultorio: int = Field(
        default=0, description="Numero de consultorios medicos habilitados"
    )
    bodega: int = Field(default=0, description="Numero de bodegas o almacenes seguros")
    salidas_emergencia: int = Field(
        default=0, description="Numero de salidas de emergencia despejadas"
    )
    extintores: int = Field(
        default=0, description="Numero de extintores fijos instalados en el inmueble"
    )
    accesos_silla_ruedas: bool = Field(
        default=False, description="Disponibilidad de rampas y accesibilidad"
    )
    planta_electrica: bool = Field(
        default=False, description="Disponibilidad de planta electrica de emergencia"
    )
    sistema_agua: str = Field(
        default="Red municipal",
        max_length=100,
        description="Tipo o fuente del sistema de agua",
    )
    estado_inmueble: str = Field(
        default="Operativo",
        max_length=100,
        description="Condicion fisica y estructural del inmueble",
    )


class InventarioInfraestructuraCreate(InventarioInfraestructuraBase):
    albergue_id: uuid.UUID


class InventarioInfraestructuraUpdate(SQLModel):
    capacidad_maxima: int | None = None
    dormitorios: int | None = None
    banos: int | None = None
    regaderas: int | None = None
    cocina: int | None = None
    comedor: int | None = None
    consultorio: int | None = None
    bodega: int | None = None
    salidas_emergencia: int | None = None
    extintores: int | None = None
    accesos_silla_ruedas: bool | None = None
    planta_electrica: bool | None = None
    sistema_agua: str | None = Field(default=None, max_length=100)
    estado_inmueble: str | None = Field(default=None, max_length=100)


class InventarioInfraestructura(InventarioInfraestructuraBase, table=True):
    __tablename__: str = "inventario_infraestructura"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    albergue_id: uuid.UUID = Field(
        foreign_key="albergue.id", unique=True, index=True, ondelete="CASCADE"
    )
    fecha_actualizacion: datetime = Field(
        default_factory=obtener_fecha_hora_utc,
        sa_type=DateTime(timezone=True),
    )

    albergue: Albergue | None = Relationship(
        back_populates="inventario_infraestructura"
    )


class InventarioInfraestructuraPublic(InventarioInfraestructuraBase):
    id: uuid.UUID
    albergue_id: uuid.UUID
    fecha_actualizacion: datetime


# ==============================================================================
# 7. INVENTARIO DE RECURSOS HUMANOS (12 PERFILES OPERATIVOS)
# ==============================================================================


class InventarioRecursoHumanoBase(SQLModel):
    administrador: int = Field(
        default=0, description="Personal administrativo o coordinadores en turno"
    )
    medicos: int = Field(default=0, description="Medicos generales o especialistas")
    enfermeria: int = Field(default=0, description="Personal de enfermeria activo")
    psicologia: int = Field(
        default=0, description="Especialistas en atencion psicologica o contencion"
    )
    cocineros: int = Field(
        default=0, description="Personal encargado de preparacion de alimentos"
    )
    personal_limpieza: int = Field(
        default=0, description="Personal de aseo y saneamiento ambiental"
    )
    seguridad: int = Field(default=0, description="Personal de seguridad o vigilancia")
    trabajadores_sociales: int = Field(
        default=0, description="Trabajadores sociales para censo y vinculacion"
    )
    traductores: int = Field(
        default=0, description="Traductores o interpretes linguisticos"
    )
    voluntarios: int = Field(default=0, description="Voluntarios de apoyo general")
    conductores: int = Field(
        default=0, description="Conductores de vehiculos o ambulancias"
    )
    responsables_bodega: int = Field(
        default=0, description="Responsables de control de bodega y suministros"
    )


class InventarioRecursoHumanoCreate(InventarioRecursoHumanoBase):
    albergue_id: uuid.UUID


class InventarioRecursoHumanoUpdate(SQLModel):
    administrador: int | None = None
    medicos: int | None = None
    enfermeria: int | None = None
    psicologia: int | None = None
    cocineros: int | None = None
    personal_limpieza: int | None = None
    seguridad: int | None = None
    trabajadores_sociales: int | None = None
    traductores: int | None = None
    voluntarios: int | None = None
    conductores: int | None = None
    responsables_bodega: int | None = None


class InventarioRecursoHumano(InventarioRecursoHumanoBase, table=True):
    __tablename__: str = "inventario_recurso_humano"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    albergue_id: uuid.UUID = Field(
        foreign_key="albergue.id", unique=True, index=True, ondelete="CASCADE"
    )
    fecha_actualizacion: datetime = Field(
        default_factory=obtener_fecha_hora_utc,
        sa_type=DateTime(timezone=True),
    )

    albergue: Albergue | None = Relationship(
        back_populates="inventario_recursos_humanos"
    )


class InventarioRecursoHumanoPublic(InventarioRecursoHumanoBase):
    id: uuid.UUID
    albergue_id: uuid.UUID
    fecha_actualizacion: datetime


# ==============================================================================
# 8. ESQUEMAS COMPUESTOS DE RESPUESTA
# ==============================================================================


class AlbergueDetallePublic(AlberguePublic):
    inventario_suministros: InventarioSuministroPublic | None = None
    inventario_infraestructura: InventarioInfraestructuraPublic | None = None
    inventario_recursos_humanos: InventarioRecursoHumanoPublic | None = None
    total_personas_albergadas: int | None = None
    total_familias: int | None = None
