import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from app.models.comun import obtener_fecha_hora_utc


class NivelAlertaRiesgo(StrEnum):
    """Semaforo de alerta de Proteccion Civil."""

    VERDE = "verde"
    AMARILLO = "amarillo"
    NARANJA = "naranja"
    ROJA = "roja"


class AlertaZonaRiesgoBase(SQLModel):
    codigo_alerta: str = Field(unique=True, index=True, max_length=50)
    titulo: str = Field(max_length=255)
    tipo_fenomeno: str = Field(
        default="Hidrometeorologico",
        max_length=100,
        description="Inundacion, desbordamiento de rio, deslave, ciclon",
    )
    nivel_alerta: NivelAlertaRiesgo = Field(
        default=NivelAlertaRiesgo.AMARILLO, index=True
    )
    descripcion: str = Field(max_length=2000)
    cuenca_rio: str | None = Field(
        default=None,
        max_length=150,
        description="Rio Cazones, Rio Panuco, Rio Tuxpan, Rio Tecolutla",
    )
    nivel_actual_metros: float | None = Field(default=None)
    nivel_critico_desbordamiento: float | None = Field(default=None)
    municipios_afectados: str | None = Field(
        default=None,
        max_length=1000,
        description="Lista o municipios delimitados en alerta",
    )
    latitud_referencia: float | None = Field(default=None)
    longitud_referencia: float | None = Field(default=None)
    radio_afectacion_km: float | None = Field(default=None)
    activo: bool = Field(default=True, index=True)
    # Geometria poligonal PostGIS (formato WKT para insercion)
    # Complementario a punto+radio, no lo reemplaza
    geometria_wkt: str | None = Field(
        default=None,
        max_length=10000,
        description="Geometria en formato WKT (POLYGON, MULTIPOLYGON) para PostGIS",
        exclude=True,  # No se serializa en respuestas publicas por defecto
    )


class AlertaZonaRiesgoCreate(AlertaZonaRiesgoBase):
    pass


class AlertaZonaRiesgoUpdate(SQLModel):
    codigo_alerta: str | None = Field(default=None, max_length=50)
    titulo: str | None = Field(default=None, max_length=255)
    tipo_fenomeno: str | None = Field(default=None, max_length=100)
    nivel_alerta: NivelAlertaRiesgo | None = None
    descripcion: str | None = Field(default=None, max_length=2000)
    cuenca_rio: str | None = Field(default=None, max_length=150)
    nivel_actual_metros: float | None = None
    nivel_critico_desbordamiento: float | None = None
    municipios_afectados: str | None = Field(default=None, max_length=1000)
    latitud_referencia: float | None = None
    longitud_referencia: float | None = None
    radio_afectacion_km: float | None = None
    activo: bool | None = None
    fecha_vigencia: datetime | None = None


class AlertaZonaRiesgo(AlertaZonaRiesgoBase, table=True):
    __tablename__: str = "alerta_zona_riesgo"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_emision: datetime = Field(
        default_factory=obtener_fecha_hora_utc,
        sa_type=DateTime(timezone=True),
    )
    fecha_vigencia: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
    )


class AlertaZonaRiesgoPublic(AlertaZonaRiesgoBase):
    id: uuid.UUID
    fecha_emision: datetime
    fecha_vigencia: datetime | None = None


class AlertasZonaRiesgoPublic(SQLModel):
    datos: list[AlertaZonaRiesgoPublic]
    total: int
