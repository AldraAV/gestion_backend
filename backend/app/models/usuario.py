import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.comun import obtener_fecha_hora_utc

if TYPE_CHECKING:
    from app.models.albergue import Albergue
    from app.models.albergue_usuario import AlbergueUsuario
    from app.models.item import Item


class RolOperativo(StrEnum):
    """Niveles de privilegios operativos para la plataforma de albergues."""

    COORDINADOR_EMERGENCIAS = "coordinador_emergencias"
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


RolOperativoAdmin = RolOperativo


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    rol: str = Field(default=RolOperativo.PERSONAL_OPERATIVO, max_length=50)

    @property
    def correo(self) -> str:
        return self.email

    @property
    def nombre(self) -> str | None:
        return self.full_name


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None
    rol: str | None = None


class User(UserBase, table=True):
    __tablename__: str = "user"

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

    @property
    def hash_password(self) -> str:
        return self.hashed_password

    @property
    def creado_en(self) -> datetime | None:
        return self.created_at


class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


# Alias soberanos para interoperabilidad total
Usuario = User
UsuarioBase = UserBase
UsuarioCreate = UserCreate
UsuarioUpdate = UserUpdate
UsuarioPublic = UserPublic
UsuariosPublic = UsersPublic
UsuarioAdmin = User
UsuarioAdminBase = UserBase
UsuarioAdminCreate = UserCreate
UsuarioAdminUpdate = UserUpdate
UsuarioAdminPublic = UserPublic
UsuariosAdminPublic = UsersPublic
