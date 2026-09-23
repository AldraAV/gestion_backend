"""
Paquete adaptador para Supabase (Auth, Base de Datos, Storage).
"""

from .client import (
    obtener_cliente_supabase,
    obtener_cliente_supabase_admin,
    ErrorConfiguracionSupabase,
)
from .auth import (
    verificar_token_supabase,
    obtener_usuario_por_token,
    extraer_token_google_de_sesion,
    ErrorAutenticacionSupabase,
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
