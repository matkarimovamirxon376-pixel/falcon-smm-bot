"""Xizmatlar, platformalar va buyurtma oqimi (FSM)."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app import texts
from app.falcon_api import FalconAPI, FalconAPIError, Service
from app.keyboards import (
    cancel_only,
    confirm_order,
    main_menu,
    service_card,
    services_list,
)
from app.storage import OrderRecord, OrderStorage
from app.texts import PLATFORMS, detect_platform

router = Router()


# --------------------------------------------------------------------------- #
# Buyurtma berish uchun holatlar (FSM)
# --------------------------------------------------------------------------- #
class OrderStates(StatesGroup):
    waiting_link = State()
    waiting_quantity = State()
    confirming = State()


# --------------------------------------------------------------------------- #
# Yordamchi: platformaga tegishli xizmatlarni olish (filtrlangan)
# --------------------------------------------------------------------------- #
async def _get_services_for(api: FalconAPI, platform: str) -> list[Service]:
    services = await api.services()
    result: list[Service] = []
    for svc in services:
        text = f"{svc.name} {svc.category} {svc.service_type}"
        if detect_platform(text) == platform:
            result.append(svc)
    return result


def _format_price(rate: float, quantity: int, currency: str = "USD") -> str:
    """Narxni (rate — 1000 dona uchun) miqdorga ko'ra hisoblaydi."""
    price = rate * quantity / 1000
    # Keraksiz nollarni olib tashlaymiz: 1.5000 -> 1.5, 2.0000 -> 2
    formatted = f"{price:.4f}".rstrip("0").rstrip(".")
    return f"{formatted} {currency}"


# --------------------------------------------------------------------------- #
# Platforma tanlash (reply tugmalari orqali)
# --------------------------------------------------------------------------- #
async def _show_platform(message: Message, api: FalconAPI, platform: str) -> None:
    try:
        services = await _get_services_for(api, platform)
    except FalconAPIError as exc:
        await message.answer(texts.API_ERROR.format(error=exc))
        return

    title = PLATFORMS[platform]["title"]
    if not services:
        await message.answer(texts.NO_SERVICES, reply_markup=main_menu())
        return

    await message.answer(
        texts.CHOOSE_CATEGORY.format(platform=title),
        reply_markup=services_list(services, platform, page=0),
    )


@router.message(F.text == PLATFORMS["instagram"]["title"])
async def platform_instagram(message: Message, api: FalconAPI) -> None:
    await _show_platform(message, api, "instagram")


@router.message(F.text == PLATFORMS["telegram"]["title"])
async def platform_telegram(message: Message, api: FalconAPI) -> None:
    await _show_platform(message, api, "telegram")


@router.message(F.text == PLATFORMS["youtube"]["title"])
async def platform_youtube(message: Message, api: FalconAPI) -> None:
    await _show_platform(message, api, "youtube")


# --------------------------------------------------------------------------- #
# Sahifalash
# --------------------------------------------------------------------------- #
@router.callback_query(F.data.startswith("page:"))
async def paginate(callback: CallbackQuery, api: FalconAPI) -> None:
    _, platform, page_str = callback.data.split(":")
    page = int(page_str)
    try:
        services = await _get_services_for(api, platform)
    except FalconAPIError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

    if callback.message is None:
        await callback.answer()
        return

    await callback.message.edit_reply_markup(
        reply_markup=services_list(services, platform, page=page)
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery) -> None:
    await callback.answer()


# --------------------------------------------------------------------------- #
# Xizmat kartasi (narx, min/max ko'rsatish)
# --------------------------------------------------------------------------- #
async def _find_service(api: FalconAPI, service_id: int) -> Service | None:
    services = await api.services()
    for svc in services:
        if svc.service_id == service_id:
            return svc
    return None


@router.callback_query(F.data.startswith("svc:"))
async def show_service(callback: CallbackQuery, api: FalconAPI) -> None:
    service_id = int(callback.data.split(":")[1])
    try:
        svc = await _find_service(api, service_id)
    except FalconAPIError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

    if svc is None:
        await callback.answer("Xizmat topilmadi.", show_alert=True)
        return

    refill_line = texts.REFILL_YES if svc.refill else texts.REFILL_NO
    text = texts.SERVICE_CARD.format(
        name=svc.name,
        service_id=svc.service_id,
        category=svc.category or "—",
        rate=f"{svc.rate} {svc.currency}",
        min=svc.min,
        max=svc.max,
        refill=refill_line,
    )
    await callback.message.answer(text, reply_markup=service_card(svc.service_id))
    await callback.answer()


# --------------------------------------------------------------------------- #
# Buyurtma oqimi (FSM)
# --------------------------------------------------------------------------- #
@router.callback_query(F.data.startswith("order:"))
async def start_order(callback: CallbackQuery, state: FSMContext, api: FalconAPI) -> None:
    service_id = int(callback.data.split(":")[1])
    try:
        svc = await _find_service(api, service_id)
    except FalconAPIError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

    if svc is None:
        await callback.answer("Xizmat topilmadi.", show_alert=True)
        return

    await state.update_data(
        service_id=svc.service_id,
        service_name=svc.name,
        rate=svc.rate,
        currency=svc.currency,
        min=svc.min,
        max=svc.max,
    )
    await state.set_state(OrderStates.waiting_link)
    await callback.message.answer(
        texts.ORDER_ASK_LINK.format(name=svc.name),
        reply_markup=cancel_only(),
    )
    await callback.answer()


@router.message(OrderStates.waiting_link)
async def order_link(message: Message, state: FSMContext) -> None:
    link = (message.text or "").strip()
    if not link or " " in link:
        await message.answer("⚠️ Iltimos, to'g'ri havola yuboring.")
        return

    data = await state.get_data()
    await state.update_data(link=link)
    await state.set_state(OrderStates.waiting_quantity)

    # Minimal miqdor uchun taxminiy narx
    price = _format_price(data["rate"], data["min"], data["currency"])
    await message.answer(
        texts.ORDER_ASK_QUANTITY.format(
            min=data["min"], max=data["max"], price=f"(min uchun) {price}"
        ),
        reply_markup=cancel_only(),
    )


@router.message(OrderStates.waiting_quantity)
async def order_quantity(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    raw = (message.text or "").strip()
    if not raw.isdigit():
        await message.answer(
            texts.ORDER_QUANTITY_INVALID.format(min=data["min"], max=data["max"])
        )
        return

    quantity = int(raw)
    if quantity < data["min"] or quantity > data["max"]:
        await message.answer(
            texts.ORDER_QUANTITY_INVALID.format(min=data["min"], max=data["max"])
        )
        return

    price = _format_price(data["rate"], quantity, data["currency"])
    await state.update_data(quantity=quantity, price=price)
    await state.set_state(OrderStates.confirming)

    await message.answer(
        texts.ORDER_CONFIRM.format(
            name=data["service_name"],
            link=data["link"],
            quantity=quantity,
            price=price,
        ),
        reply_markup=confirm_order(),
    )


@router.callback_query(F.data == "confirm:no")
async def order_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer(texts.ORDER_CANCELLED, reply_markup=main_menu())
    await callback.answer()


@router.callback_query(F.data == "confirm:yes", OrderStates.confirming)
async def order_confirm(
    callback: CallbackQuery,
    state: FSMContext,
    api: FalconAPI,
    storage: OrderStorage,
) -> None:
    data = await state.get_data()
    try:
        result = await api.add_order(
            service_id=data["service_id"],
            link=data["link"],
            quantity=data["quantity"],
        )
    except FalconAPIError as exc:
        await state.clear()
        await callback.message.answer(texts.API_ERROR.format(error=exc))
        await callback.answer()
        return

    order_id = result.get("order")
    if order_id is None:
        await state.clear()
        await callback.message.answer(
            texts.API_ERROR.format(error="API buyurtma raqamini qaytarmadi.")
        )
        await callback.answer()
        return

    # Buyurtmani tarixga saqlaymiz
    storage.add(
        callback.from_user.id,
        OrderRecord(
            order_id=int(order_id),
            service_id=data["service_id"],
            service_name=data["service_name"],
            link=data["link"],
            quantity=data["quantity"],
            price=data["rate"] * data["quantity"] / 1000,
        ),
    )

    await state.clear()
    await callback.message.answer(
        texts.ORDER_SUCCESS.format(order_id=order_id),
        reply_markup=main_menu(),
    )
    await callback.answer("✅ Buyurtma yuborildi!")


# --------------------------------------------------------------------------- #
# Buyurtmalar tarixi
# --------------------------------------------------------------------------- #
@router.message(F.text == "📜 Buyurtmalarim")
async def order_history(message: Message, api: FalconAPI, storage: OrderStorage) -> None:
    records = storage.get(message.from_user.id)
    if not records:
        await message.answer(texts.HISTORY_EMPTY, reply_markup=main_menu())
        return

    # API'dan dolzarb holatlarni olishga harakat qilamiz.
    # Javob formati: {"<order_id>": {"status": "...", ...}, ...}
    statuses: dict[str, dict] = {}
    try:
        order_ids = [r.order_id for r in records]
        raw = await api.orders_status(order_ids)
        if isinstance(raw, dict):
            statuses = {str(k): v for k, v in raw.items()}
    except FalconAPIError:
        statuses = {}

    text = texts.HISTORY_TITLE
    for idx, rec in enumerate(records, start=1):
        status_info = statuses.get(str(rec.order_id), {})
        if isinstance(status_info, dict):
            status = status_info.get("status", "noma'lum")
        else:
            status = "noma'lum"
        text += texts.HISTORY_ITEM.format(
            idx=idx,
            order_id=rec.order_id,
            name=rec.service_name,
            quantity=rec.quantity,
            status=status,
        )

    await message.answer(text, reply_markup=main_menu())
