"""
Paquete adaptador para Supabase (Auth, Base de Datos, Storage).
"""

from .auth import (
    ErrorAutenticacionSupabase,
    extraer_token_google_de_sesion,
    obtener_usuario_por_token,
    verificar_token_supabase,
)
from .client import (
    ErrorConfiguracionSupabase,
    obtener_cliente_supabase,
    obtener_cliente_supabase_admin,
)
from .storage import (
    AlmacenamientoSupabase,
    ErrorStorageSupabase,
)

__all__ = [
    "obtener_cliente_supabase",
    "obtener_cliente_supabase_admin",
    "ErrorConfiguracionSupabase",
    "verificar_token_supabase",
    "obtener_usuario_por_token",
    "extraer_token_google_de_sesion",
    "ErrorAutenticacionSupabase",
    "AlmacenamientoSupabase",
    "ErrorStorageSupabase",
]
