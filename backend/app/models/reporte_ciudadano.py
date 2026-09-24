import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.comun import obtener_fecha_hora_utc

if TYPE_CHECKING:
    from app.models.usuario import User


class TipoEmergenciaCiudadana(StrEnum):
    """Clasificacion de incidentes reportados por la ciudadania."""

    INUNDACION_SEVERA = "inundacion_severa"
    PERSONA_ATRAPADA = "persona_atrapada"
    DESLAVE_BLOQUEO_CAMINO = "deslave_bloqueo_camino"
    REQUIERE_EVACUACION = "requiere_evacuacion"
    DESABASTO_SUMINISTROS = "desabasto_suministros"
    ATENCION_MEDICA_URGENTE = "atencion_medica_urgente"
    OTRO = "otro"


class NivelPrioridadEmergencia(StrEnum):
    """Nivel de triaje y atencion de proteccion civil."""

    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA_VIDA_EN_RIESGO = "critica_vida_en_riesgo"


class EstadoReporteCiudadano(StrEnum):
    """Ciclo de despacho y respuesta operativa del reporte."""

    RECIBIDO = "recibido"
    EN_VERIFICACION = "en_verificacion"
    BRIGADA_ASIGNADA = "brigada_asignada"
    ATENDIDO = "atendido"
    CANCELADO = "cancelado"


class ReporteCiudadanoBase(SQLModel):
    folio_reporte: str = Field(unique=True, index=True, max_length=50)
    tipo_emergencia: TipoEmergenciaCiudadana = Field(
        default=TipoEmergenciaCiudadana.INUNDACION_SEVERA, index=True
    )
    descripcion: str = Field(max_length=2000)
    latitud: float = Field(index=True)
    longitud: float = Field(index=True)
    direccion_referencia: str = Field(max_length=500)
    municipio: str = Field(index=True, max_length=150)
    localidad: str | None = Field(default=None, max_length=150)
    nivel_prioridad: NivelPrioridadEmergencia = Field(
        default=NivelPrioridadEmergencia.ALTA, index=True
    )
    estado_reporte: EstadoReporteCiudadano = Field(
        default=EstadoReporteCiudadano.RECIBIDO, index=True
    )
    personas_afectadas: int = Field(default=1, ge=1)
    personas_vulnerables: int = Field(default=0, ge=0)
    telefono_contacto: str | None = Field(default=None, max_length=50)
    url_evidencia_multimedia: str | None = Field(default=None, max_length=1000)


class ReporteCiudadanoCreate(ReporteCiudadanoBase):
    pass


class ReporteCiudadanoUpdate(SQLModel):
    tipo_emergencia: TipoEmergenciaCiudadana | None = None
    descripcion: str | None = Field(default=None, max_length=2000)
    latitud: float | None = None
    longitud: float | None = None
    direccion_referencia: str | None = Field(default=None, max_length=500)
    municipio: str | None = Field(default=None, max_length=150)
    localidad: str | None = Field(default=None, max_length=150)
    nivel_prioridad: NivelPrioridadEmergencia | None = None
    estado_reporte: EstadoReporteCiudadano | None = None
    personas_afectadas: int | None = None
    personas_vulnerables: int | None = None
    telefono_contacto: str | None = Field(default=None, max_length=50)
    url_evidencia_multimedia: str | None = Field(default=None, max_length=1000)
    brigada_asignada_id: uuid.UUID | None = None
    fecha_atencion: datetime | None = None


class ReporteCiudadano(ReporteCiudadanoBase, table=True):
    __tablename__: str = "reporte_ciudadano"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    brigada_asignada_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    fecha_reporte: datetime = Field(
        default_factory=obtener_fecha_hora_utc,
        sa_type=DateTime(timezone=True),
    )
    fecha_atencion: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
    )

    brigada_asignada: Optional["User"] = Relationship()


class ReporteCiudadanoPublic(ReporteCiudadanoBase):
    id: uuid.UUID
    brigada_asignada_id: uuid.UUID | None = None
    fecha_reporte: datetime
    fecha_atencion: datetime | None = None


class ReportesCiudadanosPublic(SQLModel):
    datos: list[ReporteCiudadanoPublic]
    total: int
