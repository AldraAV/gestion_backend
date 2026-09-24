from fastapi import APIRouter

from app.api.routes import (
    albergues_admin,
    drive,
    items,
    login,
    mapa_incidencias,
    private,
    rutas_seguras,
    supabase_storage,
    ubicaciones,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(drive.router)
api_router.include_router(supabase_storage.router)
api_router.include_router(rutas_seguras.router)
api_router.include_router(ubicaciones.enrutador)
api_router.include_router(mapa_incidencias.router)
api_router.include_router(albergues_admin.router, prefix="/admin")
api_router.include_router(albergues_admin.router)


if settings.FASTAPI_ENV == "development":
    api_router.include_router(private.router)
