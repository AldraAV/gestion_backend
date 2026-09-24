import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.comun import obtener_fecha_hora_utc

if TYPE_CHECKING:
    from app.models.albergue import Albergue
    from app.models.grupo_familiar import GrupoFamiliar
    from app.models.usuario import User


class EstadoEstancia(StrEnum):
    """Estatus del ciclo de estancia de una persona albergada."""

    ALBERGADO = "albergado"
    SALIDA_TEMPORAL = "salida_temporal"
    EGRESO_DEFINITIVO = "egreso_definitivo"
    TRASLADADO = "trasladado"


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

    albergue: Optional["Albergue"] = Relationship(back_populates="personas_refugiadas")
    grupo_familiar: Optional["GrupoFamiliar"] = Relationship(
        back_populates="integrantes"
    )
    registrado_por: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[PersonaRefugiada.registrado_por_id]"}
    )
    egreso_por: Optional["User"] = Relationship(
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
