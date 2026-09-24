import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.comun import obtener_fecha_hora_utc

if TYPE_CHECKING:
    from app.models.albergue import Albergue
    from app.models.usuario import User


# ==============================================================================
# ENUMERACIONES DE SUMINISTROS Y MOVIMIENTOS
# ==============================================================================


class CategoriaSuministro(StrEnum):
    """Categorias oficiales de insumos de Proteccion Civil."""

    AGUA_ALIMENTOS = "agua_alimentos"
    ABRIGO_PERNOCTA = "abrigo_pernocta"
    HIGIENE_SALUD = "higiene_salud"
    EQUIPO_HERRAMIENTAS = "equipo_herramientas"
    PROTECCION_SEGURIDAD = "proteccion_seguridad"
    MEDICAMENTOS = "medicamentos"
    GENERAL = "general"


class TipoMovimientoSuministro(StrEnum):
    """Tipos de transacciones para trazabilidad de donaciones y consumos."""

    ENTRADA_DONACION = "entrada_donacion"
    ENTRADA_GOBIERNO = "entrada_gobierno"
    SALIDA_CONSUMO = "salida_consumo"
    SALIDA_TRASLADO = "salida_traslado"
    MERMA_DANADO = "merma_danado"


# ==============================================================================
# 1. CATALOGO MAESTRO DE SUMINISTROS (NORMALIZADO 3FN)
# ==============================================================================


class CatalogoSuministroBase(SQLModel):
    codigo: str = Field(unique=True, index=True, max_length=50)
    nombre: str = Field(index=True, max_length=200)
    categoria: CategoriaSuministro = Field(
        default=CategoriaSuministro.GENERAL, index=True
    )
    unidad_medida: str = Field(
        default="piezas",
        max_length=50,
        description="Litros, piezas, cajas, paquetes, kg",
    )
    es_critico: bool = Field(
        default=False,
        description="Indica si es un articulo de supervivencia inmediata",
    )
    descripcion: str | None = Field(default=None, max_length=500)


class CatalogoSuministroCreate(CatalogoSuministroBase):
    pass


class CatalogoSuministroUpdate(SQLModel):
    codigo: str | None = Field(default=None, max_length=50)
    nombre: str | None = Field(default=None, max_length=200)
    categoria: CategoriaSuministro | None = None
    unidad_medida: str | None = Field(default=None, max_length=50)
    es_critico: bool | None = None
    descripcion: str | None = Field(default=None, max_length=500)


class CatalogoSuministro(CatalogoSuministroBase, table=True):
    __tablename__: str = "catalogo_suministro"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_registro: datetime = Field(
        default_factory=obtener_fecha_hora_utc,
        sa_type=DateTime(timezone=True),
    )

    inventarios: list["InventarioArticuloSuministro"] = Relationship(
        back_populates="suministro"
    )
    movimientos: list["MovimientoSuministro"] = Relationship(
        back_populates="suministro"
    )


class CatalogoSuministroPublic(CatalogoSuministroBase):
    id: uuid.UUID
    fecha_registro: datetime


class CatalogosSuministroPublic(SQLModel):
    datos: list[CatalogoSuministroPublic]
    total: int


# ==============================================================================
# 2. INVENTARIO RELACIONAL POR ALBERGUE Y ARTICULO (NORMALIZADO 3FN)
# ==============================================================================


class InventarioArticuloSuministroBase(SQLModel):
    albergue_id: uuid.UUID = Field(
        foreign_key="albergue.id", index=True, ondelete="CASCADE"
    )
    suministro_id: uuid.UUID = Field(
        foreign_key="catalogo_suministro.id", index=True, ondelete="CASCADE"
    )
    cantidad_disponible: float = Field(
        default=0.0, ge=0.0, description="Existencias actuales en almacen"
    )
    cantidad_minima_sugerida: float = Field(
        default=0.0, ge=0.0, description="Umbral de alerta de desabasto"
    )


class InventarioArticuloSuministroCreate(InventarioArticuloSuministroBase):
    pass


class InventarioArticuloSuministroUpdate(SQLModel):
    cantidad_disponible: float | None = None
    cantidad_minima_sugerida: float | None = None


class InventarioArticuloSuministro(InventarioArticuloSuministroBase, table=True):
    __tablename__: str = "inventario_articulo_suministro"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_actualizacion: datetime = Field(
        default_factory=obtener_fecha_hora_utc,
        sa_type=DateTime(timezone=True),
    )

    albergue: Optional["Albergue"] = Relationship()
    suministro: CatalogoSuministro | None = Relationship(back_populates="inventarios")


class InventarioArticuloSuministroPublic(InventarioArticuloSuministroBase):
    id: uuid.UUID
    fecha_actualizacion: datetime
    suministro: CatalogoSuministroPublic | None = None


# ==============================================================================
# 3. MOVIMIENTOS Y TRAZABILIDAD DE SUMINISTROS (DONACIONES / AUDITORIA)
# ==============================================================================


class MovimientoSuministroBase(SQLModel):
    albergue_id: uuid.UUID = Field(
        foreign_key="albergue.id", index=True, ondelete="CASCADE"
    )
    suministro_id: uuid.UUID = Field(
        foreign_key="catalogo_suministro.id", index=True, ondelete="CASCADE"
    )
    tipo_movimiento: TipoMovimientoSuministro = Field(index=True)
    cantidad: float = Field(gt=0.0, description="Cantidad transaccionada")
    origen_destino: str | None = Field(
        default=None,
        max_length=255,
        description="Donante, institucion de origen o refugio de destino",
    )
    observaciones: str | None = Field(default=None, max_length=500)


class MovimientoSuministroCreate(MovimientoSuministroBase):
    responsable_id: uuid.UUID | None = None


class MovimientoSuministro(MovimientoSuministroBase, table=True):
    __tablename__: str = "movimiento_suministro"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    responsable_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    fecha_registro: datetime = Field(
        default_factory=obtener_fecha_hora_utc,
        sa_type=DateTime(timezone=True),
    )

    albergue: Optional["Albergue"] = Relationship()
    suministro: CatalogoSuministro | None = Relationship(back_populates="movimientos")
    responsable: Optional["User"] = Relationship()


class MovimientoSuministroPublic(MovimientoSuministroBase):
    id: uuid.UUID
    responsable_id: uuid.UUID | None = None
    fecha_registro: datetime


# ==============================================================================
# 4. TABLA DE RESUMEN DE SUMINISTROS (COMPATIBILIDAD CON V1)
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
    extintores_reserva: int = Field(
        default=0, description="Extintores en reserva o almacen"
    )
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
    extintores_reserva: int | None = None
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

    albergue: Optional["Albergue"] = Relationship(
        back_populates="inventario_suministros"
    )


class InventarioSuministroPublic(InventarioSuministroBase):
    id: uuid.UUID
    albergue_id: uuid.UUID
    fecha_actualizacion: datetime
