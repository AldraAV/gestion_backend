import warnings
from pathlib import Path
from typing import Literal, Self

from pydantic import (
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

_directorio_backend = Path(__file__).resolve().parent.parent.parent
_directorio_raiz = _directorio_backend.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            str(_directorio_backend / ".env"),
            str(_directorio_raiz / ".env"),
            ".env",
            "../.env",
        ),
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    FASTAPI_ENV: Literal["development"] | None = None

    PROJECT_NAME: str
    SENTRY_DSN: HttpUrl | None = None
    DATABASE_URL: PostgresDsn

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _use_psycopg_driver(cls, value: str | PostgresDsn) -> str:
        database_url = str(value)
        for scheme in ("postgres://", "postgresql://"):
            if database_url.startswith(scheme):
                return database_url.replace(scheme, "postgresql+psycopg://", 1)
        return database_url

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    # Configuracion de Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""
    SUPABASE_PUBLISHABLE_KEY: str = ""
    SUPABASE_JWKS_URL: str = ""

    # Configuracion de Google Drive y OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_SERVICE_ACCOUNT_JSON: str = ""
    GOOGLE_SERVICE_ACCOUNT_FILE: str = ""
    GOOGLE_DRIVE_ROOT_FOLDER_ID: str = ""

    # Proveedores de Inferencia IA (HackaTec)
    NVIDIA_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    CEREBRAS_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""
    LLM7_API_KEY: str = ""
    ZAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    COHERE_API_KEY: str = ""
    HF_TOKEN: str = ""
    JINA_API_KEY: str = ""
    DEEPINFRA_API_KEY: str = ""
    VOYAGE_API_KEY: str = ""
    VOYAGE_ENDPOINT: str = "https://ai.mongodb.com"

    # Proveedores de datos de desastres (APIs externas - sin persistencia)
    USGS_EARTHQUAKE_BASE_URL: str = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    CONAGUA_SMN_BASE_URL: str = ""
    FIRMS_API_KEY: str = ""
    FIRMS_BASE_URL: str = "https://firms.modaps.eosdis.nasa.gov/api"
    GDACS_FEED_URL: str = "https://www.gdacs.org/xml/rss.xml"
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    CLIMA_PROVIDER: str = "openmeteo"
    MAPBOX_ACCESS_TOKEN: str = ""

    # Cache TTL en segundos por proveedor
    CACHE_TTL_SISMOS: int = 300
    CACHE_TTL_CLIMA: int = 900
    CACHE_TTL_INCENDIOS: int = 21600
    CACHE_TTL_GLOBAL: int = 21600

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.FASTAPI_ENV == "development":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        for host in self.DATABASE_URL.hosts():
            self._check_default_secret("DATABASE_URL password", host["password"])
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self


settings = Settings()  # type: ignore # ty: ignore[unused-ignore-comment]
