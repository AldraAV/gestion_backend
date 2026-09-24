import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.comun import obtener_fecha_hora_utc

if TYPE_CHECKING:
    from app.models.albergue_usuario import AlbergueUsuario
    from app.models.grupo_familiar import GrupoFamiliar
    from app.models.infraestructura import (
        InventarioInfraestructura,
        InventarioInfraestructuraPublic,
    )
    from app.models.persona_refugiada import PersonaRefugiada
    from app.models.recurso_humano import (
        InventarioRecursoHumano,
        InventarioRecursoHumanoPublic,
    )
    from app.models.suministro import (
        InventarioSuministro,
        InventarioSuministroPublic,
    )
    from app.models.usuario import User


class EstadoOperativoAlbergue(StrEnum):
    """Estados del ciclo de vida operativo del refugio temporal."""

    PLANEADO = "planeado"
    DISPONIBLE = "disponible"
    ACTIVADO = "activado"
    LLENO = "lleno"
    CERRADO = "cerrado"
    FUERA_DE_SERVICIO = "fuera_de_servicio"


class AlbergueBase(SQLModel):
    folio_identificador: str = Field(unique=True, index=True, max_length=50)
    nombre: str = Field(index=True, max_length=255)
    direccion: str = Field(max_length=500)
    municipio: str = Field(index=True, max_length=150)
    localidad: str | None = Field(default=None, max_length=150)
    estado_republica: str = Field(default="Veracruz", max_length=100)
    latitud: float | None = Field(default=None)
    longitud: float | None = Field(default=None)
    tipo_inmueble: str | None = Field(default=None, max_length=100)
    telefono_contacto: str | None = Field(default=None, max_length=50)
    admite_mascotas: bool = Field(default=False)
    ocupacion_actual: int = Field(
        default=0, ge=0, description="Numero actual de personas alojadas"
    )
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
    ocupacion_actual: int | None = None
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

    # Relaciones cardinales 1 a 1 de inventario
    responsable: Optional["User"] = Relationship(back_populates="albergues_a_cargo")
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


class AlbergueDetallePublic(AlberguePublic):
    inventario_suministros: Optional["InventarioSuministroPublic"] = None
    inventario_infraestructura: Optional["InventarioInfraestructuraPublic"] = None
    inventario_recursos_humanos: Optional["InventarioRecursoHumanoPublic"] = None
    total_personas_albergadas: int | None = None
    total_familias: int | None = None
