"""O'zbek tilidagi barcha matnlar va platforma aniqlash yordamchilari."""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Asosiy matnlar
# ---------------------------------------------------------------------------
WELCOME = (
    "👋 Assalomu alaykum, <b>{name}</b>!\n\n"
    "🦅 <b>FALCON SMM</b> botiga xush kelibsiz.\n\n"
    "Bu yerda siz ijtimoiy tarmoqlar uchun xizmatlarni ko'rishingiz "
    "va buyurtma berishingiz mumkin.\n\n"
    "Quyidagi menyudan kerakli bo'limni tanlang 👇"
)

MAIN_MENU_TITLE = "📋 <b>Asosiy menyu</b>\n\nKerakli bo'limni tanlang:"

CHOOSE_CATEGORY = "📂 <b>{platform}</b> xizmatlari\n\nKerakli xizmatni tanlang:"

NO_SERVICES = (
    "⚠️ Hozircha bu platforma uchun xizmatlar topilmadi.\n"
    "Keyinroq urinib ko'ring."
)

API_ERROR = (
    "❌ API bilan bog'lanishda xatolik yuz berdi:\n<code>{error}</code>\n\n"
    "Iltimos, birozdan so'ng qayta urinib ko'ring."
)

SERVICE_CARD = (
    "🧾 <b>{name}</b>\n\n"
    "🆔 Xizmat ID: <code>{service_id}</code>\n"
    "📂 Kategoriya: {category}\n"
    "💵 Narxi: <b>{rate}</b> (1000 dona uchun)\n"
    "⬇️ Minimal: <b>{min}</b>\n"
    "⬆️ Maksimal: <b>{max}</b>\n"
    "{refill}"
)

ORDER_ASK_LINK = (
    "🔗 <b>{name}</b>\n\n"
    "Buyurtma uchun <b>havolani</b> yuboring\n"
    "(masalan: profil, post yoki kanal havolasi):"
)

ORDER_ASK_QUANTITY = (
    "🔢 Endi <b>miqdorni</b> kiriting.\n\n"
    "Ruxsat etilgan oraliq: <b>{min}</b> — <b>{max}</b>\n"
    "Taxminiy narx: <b>{price}</b>"
)

ORDER_QUANTITY_INVALID = (
    "⚠️ Noto'g'ri miqdor. Iltimos, <b>{min}</b> dan <b>{max}</b> gacha "
    "bo'lgan son kiriting."
)

ORDER_CONFIRM = (
    "✅ <b>Buyurtmani tasdiqlang</b>\n\n"
    "🧾 Xizmat: {name}\n"
    "🔗 Havola: {link}\n"
    "🔢 Miqdor: {quantity}\n"
    "💵 Narx: <b>{price}</b>\n\n"
    "Tasdiqlaysizmi?"
)

ORDER_SUCCESS = (
    "🎉 <b>Buyurtma qabul qilindi!</b>\n\n"
    "🆔 Buyurtma raqami: <code>{order_id}</code>\n\n"
    "Holatni «📜 Buyurtmalarim» bo'limidan kuzatishingiz mumkin."
)

ORDER_CANCELLED = "❌ Buyurtma bekor qilindi."

HISTORY_EMPTY = (
    "📭 Sizda hali buyurtmalar yo'q.\n\n"
    "Yangi buyurtma berish uchun asosiy menyudan platformani tanlang."
)

HISTORY_TITLE = "📜 <b>Buyurtmalar tarixi</b>\n"

HISTORY_ITEM = (
    "\n#{idx} — 🆔 <code>{order_id}</code>\n"
    "   🧾 {name}\n"
    "   🔢 {quantity} | 📊 {status}\n"
)

HELP_TEXT = (
    "ℹ️ <b>Yordam</b>\n\n"
    "🦅 <b>FALCON SMM</b> boti orqali siz:\n"
    "• Instagram, Telegram, YouTube xizmatlarini ko'rasiz\n"
    "• Narx, minimal va maksimal miqdorni bilib olasiz\n"
    "• Buyurtma berasiz\n"
    "• Buyurtmalaringiz tarixini kuzatasiz\n\n"
    "Boshlash uchun /start buyrug'ini bosing."
)

BALANCE_TEXT = "💰 <b>Hisob balansi:</b> {balance} {currency}"

REFILL_YES = "♻️ Qayta to'ldirish (refill) mavjud"
REFILL_NO = ""

# ---------------------------------------------------------------------------
# Platformalar va ularni aniqlash uchun kalit so'zlar
# ---------------------------------------------------------------------------
PLATFORMS = {
    "instagram": {
        "title": "📸 Instagram",
        "keywords": ["instagram", "insta", "ig "],
    },
    "telegram": {
        "title": "✈️ Telegram",
        "keywords": ["telegram", "tg ", "tg_"],
    },
    "youtube": {
        "title": "▶️ YouTube",
        "keywords": ["youtube", "you tube", "yt "],
    },
}


def detect_platform(text: str) -> str | None:
    """Xizmat nomi/kategoriyasi bo'yicha platformani aniqlaydi."""
    lowered = f" {text.lower()} "
    for key, info in PLATFORMS.items():
        for kw in info["keywords"]:
            if kw in lowered or key in lowered:
                return key
    return None
