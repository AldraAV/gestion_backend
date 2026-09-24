from pathlib import Path

import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from app.api.main import api_router
from app.core.config import settings

FRONTEND_DIR = Path(__file__).parent / "frontend"


def custom_generate_unique_id(route: APIRoute) -> str:
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


if settings.SENTRY_DSN and settings.FASTAPI_ENV != "development":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)



@app.middleware("http")
async def auditoria_peticiones(request: Request, call_next):
    # Sanitizar comillas accidentales al final de la ruta (ej. ' o %27)
    ruta_original = request.scope.get("path", "")
    if ruta_original.endswith("'"):
        request.scope["path"] = ruta_original.rstrip("'")

    cuerpo = await request.body()
    texto_cuerpo = cuerpo.decode("utf-8", errors="replace") if cuerpo else ""
    if texto_cuerpo:
        pass

    # Crear nueva request con el cuerpo para que los handlers lo puedan leer
    async def recibir():
        return {"type": "http.request", "body": cuerpo}

    request_reconstruida = Request(request.scope, receive=recibir)
    respuesta = await call_next(request_reconstruida)

    # Garantizar cabeceras CORS ante cualquier estatus de respuesta
    origen = request.headers.get("origin")
    if origen:
        respuesta.headers["Access-Control-Allow-Origin"] = origen
        respuesta.headers["Access-Control-Allow-Credentials"] = "true"
        respuesta.headers["Access-Control-Allow-Methods"] = "*"
        respuesta.headers["Access-Control-Allow-Headers"] = "*"

    return respuesta


app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Soporta llamadas oficiales con /api/v1 y llamadas directas sin prefijo (/publico/...)
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router)


if FRONTEND_DIR.exists():
    app.frontend("/", directory=FRONTEND_DIR)
else:

    @app.get("/")
    def inicio() -> dict[str, str]:
        return {
            "mensaje": f"Bienvenido a la API de {settings.PROJECT_NAME}",
            "documentacion": "/docs",
            "redoc": "/redoc",
            "estado": "activo",
        }
