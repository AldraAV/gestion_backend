import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.comun import obtener_fecha_hora_utc

if TYPE_CHECKING:
    from app.models.albergue import Albergue


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
    extintores_instalados: int = Field(
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
    extintores_instalados: int | None = None
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

    albergue: Optional["Albergue"] = Relationship(
        back_populates="inventario_infraestructura"
    )


class InventarioInfraestructuraPublic(InventarioInfraestructuraBase):
    id: uuid.UUID
    albergue_id: uuid.UUID
    fecha_actualizacion: datetime
