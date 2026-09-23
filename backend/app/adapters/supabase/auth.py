"""
Modulo de autenticacion y verificacion de sesiones de Supabase.
Permite validar tokens JWT de usuarios y extraer credenciales de proveedores OAuth (ej. Google).
"""

from typing import Dict, Any, Optional
import jwt
import structlog
from app.core.config import settings
from .client import obtener_cliente_supabase, obtener_cliente_supabase_admin

registro = structlog.get_logger()

class ErrorAutenticacionSupabase(Exception):
    """Excepcion lanzada ante fallos en la verificacion de credenciales o tokens."""
    pass

def verificar_token_supabase(token_jwt: str) -> Dict[str, Any]:
    """
    Verifica y decodifica el token JWT emitido por Supabase Auth.
    Si se configuro SUPABASE_JWT_SECRET, realiza validacion criptografica estricta.
    """
    if not token_jwt:
        raise ErrorAutenticacionSupabase("Token de autorizacion no proporcionado.")
    
    try:
        if settings.SUPABASE_JWT_SECRET:
            datos_decodificados = jwt.decode(
                token_jwt,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated"
            )
        else:
            # En entornos de desarrollo sin el secreto local, decodifica verificando expiracion
            datos_decodificados = jwt.decode(
                token_jwt,
                options={"verify_signature": False, "verify_exp": True}
            )
        
        return datos_decodificados
    except jwt.ExpiredSignatureError:
        raise ErrorAutenticacionSupabase("El token de sesion de Supabase ha expirado.")
    except Exception as error_jwt:
        registro.warning("fallo_verificacion_jwt_supabase", error=str(error_jwt))
        raise ErrorAutenticacionSupabase(f"Token de sesion invalido: {str(error_jwt)}")

def obtener_usuario_por_token(token_jwt: str) -> Dict[str, Any]:
    """
    Consulta directamente a la API de Supabase Auth para obtener el perfil completo del usuario.
    """
    cliente = obtener_cliente_supabase()
    try:
        respuesta = cliente.auth.get_user(token_jwt)
        if not respuesta or not respuesta.user:
            raise ErrorAutenticacionSupabase("No se encontro un usuario activo para el token.")
        
        usuario = respuesta.user
        return {
            "id": usuario.id,
            "email": usuario.email,
            "app_metadata": usuario.app_metadata or {},
            "user_metadata": usuario.user_metadata or {},
            "identities": getattr(usuario, "identities", [])
        }
    except Exception as e:
        registro.error("error_obtener_usuario_supabase", error=str(e))
        raise ErrorAutenticacionSupabase(f"Error al validar usuario con Supabase: {str(e)}")

def extraer_token_google_de_sesion(usuario_o_claims: Dict[str, Any], cabecera_provider_token: Optional[str] = None) -> Optional[str]:
    """
    Extrae el token de acceso de Google (provider_token).
    1. Si el frontend lo envia explicitamente en la cabecera (X-Provider-Token), tiene prioridad.
    2. De lo contrario, inspecciona los metadatos o identities devueltos por Supabase Auth.
    """
    if cabecera_provider_token:
        return cabecera_provider_token
    
    # Inspeccionar en user_metadata o app_metadata de Supabase
    metadatos = usuario_o_claims.get("user_metadata", {})
    if "provider_token" in metadatos:
        return metadatos["provider_token"]
    
    app_meta = usuario_o_claims.get("app_metadata", {})
    if "provider_token" in app_meta:
        return app_meta["provider_token"]
        
    return None
