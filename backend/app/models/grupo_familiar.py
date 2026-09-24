import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.comun import obtener_fecha_hora_utc

if TYPE_CHECKING:
    from app.models.albergue import Albergue
    from app.models.persona_refugiada import PersonaRefugiada


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

    albergue: Optional["Albergue"] = Relationship(back_populates="grupos_familiares")
    integrantes: list["PersonaRefugiada"] = Relationship(
        back_populates="grupo_familiar"
    )


class GrupoFamiliarPublic(GrupoFamiliarBase):
    id: uuid.UUID
    fecha_registro: datetime
