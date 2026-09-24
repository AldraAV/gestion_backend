import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.comun import obtener_fecha_hora_utc

if TYPE_CHECKING:
    from app.models.albergue import Albergue


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

    albergue: Optional["Albergue"] = Relationship(
        back_populates="inventario_recursos_humanos"
    )


class InventarioRecursoHumanoPublic(InventarioRecursoHumanoBase):
    id: uuid.UUID
    albergue_id: uuid.UUID
    fecha_actualizacion: datetime
