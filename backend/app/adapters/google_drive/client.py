"""
Fabrica del cliente de Google Drive API v3.
Soporta autenticacion dual:
1. Token delegado OAuth de usuario (obtenido de Supabase Auth provider_token).
2. Credenciales de Cuenta de Servicio (Service Account) para operaciones del backend.
"""

import json
import os

import structlog
from google.oauth2 import credentials as oauth_credentials
from google.oauth2 import service_account
from googleapiclient.discovery import Resource, build

from app.core.config import settings

registro = structlog.get_logger()

ALCANCES_DRIVE_PREDETERMINADOS = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]


class ErrorCredencialesGoogleDrive(Exception):
    """Excepcion lanzada cuando las credenciales de Google Drive son invalidas o inexistentes."""

    pass


def obtener_servicio_drive_usuario(token_acceso_oauth: str) -> Resource:
    """
    Construye el cliente de Google Drive utilizando el token OAuth delegado de un usuario autenticado.
    Este token proviene habitualmente de la sesion OAuth de Supabase (provider_token).
    """
    if not token_acceso_oauth:
        raise ErrorCredencialesGoogleDrive(
            "Token de acceso de Google OAuth no proporcionado."
        )

    try:
        credenciales = oauth_credentials.Credentials(
            token=token_acceso_oauth, scopes=ALCANCES_DRIVE_PREDETERMINADOS
        )
        servicio = build("drive", "v3", credentials=credenciales, cache_discovery=False)
        return servicio
    except Exception as e:
        registro.error("error_construir_servicio_drive_oauth", error=str(e))
        raise ErrorCredencialesGoogleDrive(
            f"Fallo al inicializar cliente de Drive con token OAuth: {str(e)}"
        )


def obtener_servicio_drive_sistema() -> Resource:
    """
    Construye el cliente de Google Drive utilizando una Cuenta de Servicio (Service Account).
    Prioridad:
    1. Variable GOOGLE_SERVICE_ACCOUNT_JSON (JSON en string para despliegues serverless o Docker).
    2. Variable GOOGLE_SERVICE_ACCOUNT_FILE (Ruta local a service_account.json).
    3. Variable de entorno estandar GOOGLE_APPLICATION_CREDENTIALS.
    """
    try:
        credenciales = None

        # 1. Intentar cargar desde JSON en string
        if settings.GOOGLE_SERVICE_ACCOUNT_JSON:
            info_cuenta = json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
            credenciales = service_account.Credentials.from_service_account_info(
                info_cuenta, scopes=ALCANCES_DRIVE_PREDETERMINADOS
            )
        # 2. Intentar cargar desde ruta de archivo configurada en settings
        elif settings.GOOGLE_SERVICE_ACCOUNT_FILE and os.path.exists(
            settings.GOOGLE_SERVICE_ACCOUNT_FILE
        ):
            credenciales = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_SERVICE_ACCOUNT_FILE,
                scopes=ALCANCES_DRIVE_PREDETERMINADOS,
            )
        # 3. Intentar variable de entorno estandar de Google
        elif "GOOGLE_APPLICATION_CREDENTIALS" in os.environ and os.path.exists(
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
        ):
            credenciales = service_account.Credentials.from_service_account_file(
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
                scopes=ALCANCES_DRIVE_PREDETERMINADOS,
            )

        if not credenciales:
            raise ErrorCredencialesGoogleDrive(
                "No se encontraron credenciales de Cuenta de Servicio configuradas. "
                "Defina GOOGLE_SERVICE_ACCOUNT_JSON o GOOGLE_SERVICE_ACCOUNT_FILE."
            )

        servicio = build("drive", "v3", credentials=credenciales, cache_discovery=False)
        return servicio
    except Exception as e:
        registro.error("error_construir_servicio_drive_sistema", error=str(e))
        raise ErrorCredencialesGoogleDrive(
            f"Fallo al inicializar cliente de Drive con Service Account: {str(e)}"
        )


def resolver_servicio_drive(token_usuario: str | None = None) -> Resource:
    """
    Selector inteligente: si se provee un token de usuario, utiliza el contexto del usuario;
    de lo contrario, recurre a la Cuenta de Servicio del sistema.
    """
    if token_usuario:
        return obtener_servicio_drive_usuario(token_usuario)
    return obtener_servicio_drive_sistema()
