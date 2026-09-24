"""
Modulo de inicializacion del cliente oficial de Supabase.
Provee acceso al cliente publico (con clave anon) y al cliente administrativo (service_role).
"""

from functools import lru_cache

import structlog

from app.core.config import settings
from supabase import Client, create_client

registro = structlog.get_logger()


class ErrorConfiguracionSupabase(Exception):
    """Excepcion lanzada cuando faltan credenciales requeridas de Supabase."""

    pass


@lru_cache(maxsize=1)
def obtener_cliente_supabase() -> Client:
    """
    Retorna una instancia singleton del cliente Supabase usando la clave anonima publica.
    Ideal para consultas que respetan politicas de seguridad a nivel de fila (RLS).
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        registro.warning(
            "supabase_credenciales_no_configuradas", url=settings.SUPABASE_URL
        )
        raise ErrorConfiguracionSupabase(
            "SUPABASE_URL o SUPABASE_KEY no estan configuradas en el entorno."
        )

    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


@lru_cache(maxsize=1)
def obtener_cliente_supabase_admin() -> Client:
    """
    Retorna una instancia singleton del cliente Supabase con privilegios administrativos (service_role).
    Utilizar exclusivamente en el backend para tareas privilegiadas.
    """
    clave_admin = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
    if not settings.SUPABASE_URL or not clave_admin:
        raise ErrorConfiguracionSupabase(
            "SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY no estan configuradas."
        )

    return create_client(settings.SUPABASE_URL, clave_admin)
