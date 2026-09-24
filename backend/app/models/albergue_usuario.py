import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.comun import obtener_fecha_hora_utc
from app.models.usuario import AreaFuncional, RolOperativo

if TYPE_CHECKING:
    from app.models.albergue import Albergue
    from app.models.usuario import User


class TurnoOperativo(StrEnum):
    """Turnos operativos asignables al personal comisionado en el albergue."""

    MATUTINO = "matutino"
    VESPERTINO = "vespertino"
    NOCTURNO = "nocturno"
    COMPLETO = "completo"


class AlbergueUsuarioBase(SQLModel):
    albergue_id: uuid.UUID = Field(
        foreign_key="albergue.id", index=True, ondelete="CASCADE"
    )
    usuario_id: uuid.UUID = Field(foreign_key="user.id", index=True, ondelete="CASCADE")
    rol: str = Field(
        default=RolOperativo.PERSONAL_OPERATIVO.value, index=True, max_length=50
    )
    area: str = Field(default=AreaFuncional.GENERAL.value, index=True, max_length=50)
    turno: str = Field(default=TurnoOperativo.COMPLETO.value, index=True, max_length=50)
    activo: bool = Field(default=True, index=True)


class AlbergueUsuarioCreate(AlbergueUsuarioBase):
    pass


class AlbergueUsuarioUpdate(SQLModel):
    rol: str | None = None
    area: str | None = None
    turno: str | None = None
    activo: bool | None = None


class AlbergueUsuario(AlbergueUsuarioBase, table=True):
    __tablename__: str = "albergue_usuario"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_asignacion: datetime = Field(
        default_factory=obtener_fecha_hora_utc,
        sa_type=DateTime(timezone=True),
    )

    albergue: Optional["Albergue"] = Relationship(back_populates="personal_asignado")
    usuario: Optional["User"] = Relationship(back_populates="asignaciones_albergue")


class AlbergueUsuarioPublic(AlbergueUsuarioBase):
    id: uuid.UUID
    fecha_asignacion: datetime


class AlberguesUsuarioPublic(SQLModel):
    datos: list[AlbergueUsuarioPublic]
    total: int


class PersonalAsignadoDetalle(SQLModel):
    id: uuid.UUID
    albergue_id: uuid.UUID
    usuario_id: uuid.UUID
    email: str
    nombre_completo: str | None = None
    rol: str
    area: str
    turno: str
    activo: bool
    fecha_asignacion: datetime
