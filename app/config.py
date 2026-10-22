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


def _clean(value: str | None) -> str:
    """Qiymatdan ortiqcha bo'sh joy va tasodifan qo'yilgan qo'shtirnoqlarni olib tashlaydi."""
    if value is None:
        return ""
    value = value.strip()
    # .env da "abc" yoki 'abc' deb yozilgan bo'lsa, qo'shtirnoqlarni olib tashlaymiz
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1].strip()
    return value


# .env.example dagi namuna (placeholder) qiymatlar — bular qolib ketsa xato beramiz
_PLACEHOLDERS = {
    "123456789:ABCdefGhIjKlmNoPqRsTuVwXyZ",
    "sizning_api_kalitingiz",
    "sizning_bot_tokeningiz",
}


def load_config() -> Config:
    bot_token = _clean(os.getenv("BOT_TOKEN"))
    api_key = _clean(os.getenv("FALCON_API_KEY"))
    api_url = _clean(os.getenv("FALCON_API_URL")) or (
        "https://smmsapi.safobuilder.uz/FalconSeenv2bot/api/v2"
    )

    if not bot_token:
        raise RuntimeError(
            "BOT_TOKEN topilmadi. .env faylida BOT_TOKEN ni to'ldiring "
            "(.env.example faylidan nusxa oling: cp .env.example .env)."
        )
    if bot_token in _PLACEHOLDERS:
        raise RuntimeError(
            "BOT_TOKEN hali namuna qiymatda turibdi. .env faylida uni o'zingizning "
            "haqiqiy bot tokeningizga almashtiring."
        )
    if ":" not in bot_token:
        raise RuntimeError(
            "BOT_TOKEN noto'g'ri formatda ko'rinadi (BotFather tokeni "
            "'123456789:AA...' ko'rinishida bo'ladi). .env faylini tekshiring."
        )
    if not api_key:
        raise RuntimeError(
            "FALCON_API_KEY topilmadi. .env faylida FALCON_API_KEY ni to'ldiring."
        )
    if api_key in _PLACEHOLDERS:
        raise RuntimeError(
            "FALCON_API_KEY hali namuna qiymatda turibdi. .env faylida uni "
            "o'zingizning haqiqiy API kalitingizga almashtiring."
        )

    return Config(
        bot_token=bot_token,
        api_key=api_key,
        api_url=api_url,
        admins=_parse_admins(os.getenv("ADMINS")),
    )
