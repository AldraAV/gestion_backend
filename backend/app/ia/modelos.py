"""Esquemas de datos para el subsistema de inferencia de IA utilizando SQLModel."""

from typing import Any

from sqlmodel import Field, SQLModel


class MensajeChat(SQLModel):
    """Estructura de un mensaje conversacional."""

    rol: str = Field(description="Rol del emisor: system, user o assistant")
    contenido: str = Field(description="Texto del mensaje")


class PeticionInferencia(SQLModel):
    """Parametros de entrada para una solicitud de generacion."""

    mensajes: list[MensajeChat] = Field(
        description="Lista de mensajes en la conversacion"
    )
    modelo_preferido: str | None = Field(
        default=None, description="Identificador del modelo solicitado (opcional)"
    )
    temperatura: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Grado de aleatoriedad en la respuesta"
    )
    max_tokens: int | None = Field(
        default=2048, gt=0, description="Tope maximo de tokens en la respuesta"
    )
    permitir_fallback: bool = Field(
        default=True,
        description="Si es verdadero, conmuta al siguiente proveedor en caso de falla",
    )


class RegistroFalloProveedor(SQLModel):
    """Informacion sobre un intento fallido con un proveedor."""

    proveedor: str
    error: str
    codigo_estado: int | None = None


class RespuestaInferencia(SQLModel):
    """Resultado exitoso de una consulta de inferencia con trazabilidad."""

    contenido: str = Field(description="Texto generado por el modelo")
    proveedor_utilizado: str = Field(
        description="Nombre del proveedor que respondio exitosamente"
    )
    modelo_utilizado: str = Field(
        description="Identificador del modelo que genero la respuesta"
    )
    tiempo_latencia_segundos: float = Field(
        description="Latencia total en segundos de la peticion exitosa"
    )
    proveedores_fallidos: list[RegistroFalloProveedor] = Field(
        default_factory=list,
        description="Lista de proveedores que fallaron antes de alcanzar el exito",
    )
    metadatos_adicionales: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadatos tecnicos opcionales (tokens, finish_reason)",
    )
