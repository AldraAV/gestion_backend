from datetime import UTC, datetime


def obtener_fecha_hora_utc() -> datetime:
    """Retorna la fecha y hora actual en zona horaria UTC."""
    return datetime.now(UTC)


# Alias de compatibilidad con plantillas previas
get_datetime_utc = obtener_fecha_hora_utc
