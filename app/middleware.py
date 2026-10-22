"""Har bir handlerga umumiy obyektlarni (API client, storage) uzatuvchi middleware."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.falcon_api import FalconAPI
from app.storage import OrderStorage


class DependenciesMiddleware(BaseMiddleware):
    """`api` va `storage` ni handler argumentlariga qo'shadi."""

    def __init__(self, api: FalconAPI, storage: OrderStorage) -> None:
        self._api = api
        self._storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["api"] = self._api
        data["storage"] = self._storage
        return await handler(event, data)
