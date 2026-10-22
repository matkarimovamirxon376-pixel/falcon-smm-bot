"""Handler routerlari."""
from aiogram import Router

from app.handlers import common, services


def setup_routers() -> Router:
    router = Router()
    router.include_router(common.router)
    router.include_router(services.router)
    return router
