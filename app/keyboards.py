"""Inline va reply klaviaturalar (menyu tugmalari)."""
from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.falcon_api import Service
from app.texts import PLATFORMS

# Har sahifada nechta xizmat ko'rsatiladi
SERVICES_PER_PAGE = 8


def main_menu() -> ReplyKeyboardMarkup:
    """Asosiy reply menyu (ekran ostidagi tugmalar)."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=PLATFORMS["instagram"]["title"]),
        KeyboardButton(text=PLATFORMS["telegram"]["title"]),
    )
    builder.row(KeyboardButton(text=PLATFORMS["youtube"]["title"]))
    builder.row(
        KeyboardButton(text="📜 Buyurtmalarim"),
        KeyboardButton(text="💰 Balans"),
    )
    builder.row(KeyboardButton(text="ℹ️ Yordam"))
    return builder.as_markup(resize_keyboard=True)


def services_list(
    services: list[Service],
    platform: str,
    page: int = 0,
) -> InlineKeyboardMarkup:
    """Xizmatlar ro'yxatini sahifalab ko'rsatuvchi inline klaviatura."""
    builder = InlineKeyboardBuilder()

    start = page * SERVICES_PER_PAGE
    end = start + SERVICES_PER_PAGE
    page_services = services[start:end]

    for svc in page_services:
        # Nom juda uzun bo'lsa qisqartiramiz
        label = svc.name if len(svc.name) <= 40 else svc.name[:37] + "..."
        builder.row(
            InlineKeyboardButton(
                text=f"🧾 {label}",
                callback_data=f"svc:{svc.service_id}",
            )
        )

    # Sahifalash tugmalari
    total_pages = max(1, (len(services) + SERVICES_PER_PAGE - 1) // SERVICES_PER_PAGE)
    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"page:{platform}:{page - 1}",
            )
        )
    nav.append(
        InlineKeyboardButton(
            text=f"{page + 1}/{total_pages}",
            callback_data="noop",
        )
    )
    if end < len(services):
        nav.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"page:{platform}:{page + 1}",
            )
        )
    if nav:
        builder.row(*nav)

    return builder.as_markup()


def service_card(service_id: int) -> InlineKeyboardMarkup:
    """Bitta xizmat kartasi uchun tugmalar: buyurtma berish / orqaga."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🛒 Buyurtma berish",
            callback_data=f"order:{service_id}",
        )
    )
    return builder.as_markup()


def confirm_order() -> InlineKeyboardMarkup:
    """Buyurtmani tasdiqlash / bekor qilish."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm:yes"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="confirm:no"),
    )
    return builder.as_markup()


def cancel_only() -> InlineKeyboardMarkup:
    """Faqat bekor qilish tugmasi (havola/miqdor kiritish paytida)."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="confirm:no")
    )
    return builder.as_markup()
