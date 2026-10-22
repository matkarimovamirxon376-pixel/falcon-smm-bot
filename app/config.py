"""Loyiha sozlamalari.

TOKEN va API kaliti .env faylidan o'qiladi. Ularni kodga yozib qo'ymang!
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

# .env faylini yuklaymiz
load_dotenv()


@dataclass
class Config:
    bot_token: str
    api_key: str
    api_url: str
    admins: list[int] = field(default_factory=list)


def _parse_admins(raw: str | None) -> list[int]:
    if not raw:
        return []
    result: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            result.append(int(part))
    return result


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    api_key = os.getenv("FALCON_API_KEY", "").strip()
    api_url = os.getenv(
        "FALCON_API_URL",
        "https://smmsapi.safobuilder.uz/FalconSeenv2bot/api/v2",
    ).strip()

    if not bot_token:
        raise RuntimeError(
            "BOT_TOKEN topilmadi. .env faylida BOT_TOKEN ni to'ldiring "
            "(.env.example faylidan nusxa oling)."
        )
    if not api_key:
        raise RuntimeError(
            "FALCON_API_KEY topilmadi. .env faylida FALCON_API_KEY ni to'ldiring."
        )

    return Config(
        bot_token=bot_token,
        api_key=api_key,
        api_url=api_url,
        admins=_parse_admins(os.getenv("ADMINS")),
    )
