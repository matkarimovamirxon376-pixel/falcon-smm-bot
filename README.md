# 🦅 FALCON SMM Telegram Bot

Mavjud Telegram botingizni **FALCON SMM API** bilan ulab ishlatish uchun to'liq loyiha.
O'zbek tilidagi menyu bilan Instagram, Telegram va YouTube xizmatlarini ko'rsatadi,
narx hamda minimal/maksimal buyurtma miqdorini chiqaradi va buyurtma qabul qiladi.

> ⚠️ Bu loyiha **yangi bot yoki yangi API kaliti yaratmaydi**. Siz allaqachon
> yaratgan bot tokeni va API kalitingizdan foydalanadi.

## 🛠 Texnologiyalar

- **Python 3.10+**
- **aiogram 3** — Telegram bot framework
- **aiohttp** — FALCON SMM API ga asinxron so'rovlar
- **python-dotenv** — maxfiy sozlamalarni `.env` dan o'qish

## 📁 Loyiha tuzilishi

```
falcon-smm-bot/
├── bot.py                 # Kirish nuqtasi (botni ishga tushiradi)
├── requirements.txt
├── .env.example           # Sozlama namunasi
├── .gitignore
└── app/
    ├── config.py          # TOKEN va API kalitni o'qish
    ├── falcon_api.py      # FALCON SMM API client (aiohttp)
    ├── keyboards.py       # Menyu va inline tugmalar
    ├── texts.py           # Barcha o'zbekcha matnlar + platforma aniqlash
    ├── storage.py         # Buyurtmalar tarixi uchun ASOS (in-memory)
    ├── middleware.py      # api/storage ni handlerlarga uzatish
    └── handlers/
        ├── common.py      # /start, /help, /menu, balans
        └── services.py    # Instagram/Telegram/YouTube, buyurtma oqimi
```

## 🚀 Ishga tushirish

**1. Bog'liqliklarni o'rnating:**

```bash
pip install -r requirements.txt
```

**2. Sozlamalarni to'ldiring.** `.env.example` dan nusxa oling:

```bash
cp .env.example .env
```

So'ng `.env` faylida quyidagilarni to'ldiring:

```env
BOT_TOKEN=sizning_bot_tokeningiz
FALCON_API_KEY=sizning_api_kalitingiz
FALCON_API_URL=https://smmsapi.safobuilder.uz/FalconSeenv2bot/api/v2
```

**3. Botni ishga tushiring:**

```bash
python bot.py
```

Telegramda botingizga `/start` yuboring.

## ✨ Funksiyalar

| Funksiya | Holat |
|----------|-------|
| 1. O'zbek tilidagi menyu | ✅ |
| 2. Instagram xizmatlari | ✅ |
| 3. Telegram xizmatlari | ✅ |
| 4. YouTube xizmatlari | ✅ |
| 5. API orqali xizmatlarni olish (`action=services`) | ✅ |
| 6. Narx + minimal/maksimal miqdor | ✅ |
| 7. Buyurtmalar tarixi uchun asos | ✅ |

Qo'shimcha: buyurtma berish oqimi (havola → miqdor → tasdiqlash), balansni ko'rish,
xizmatlar ro'yxatini sahifalash.

## 🔌 FALCON SMM API

Bot sanoat standartidagi **API v2** formatidan foydalanadi (bitta endpoint, `POST`, JSON javob):

| Action | Vazifa | Kod metodi |
|--------|--------|------------|
| `services` | Barcha xizmatlar | `api.services()` |
| `balance` | Hisob balansi | `api.balance()` |
| `add` | Yangi buyurtma | `api.add_order(service, link, quantity)` |
| `status` | Bitta buyurtma holati | `api.order_status(order_id)` |
| `orders` | Bir nechta buyurtma holati | `api.orders_status([...])` |
| `refill` | Qayta to'ldirish | `api.refill(order_id)` |

Platformalar xizmat nomi va kategoriyasidagi kalit so'zlar bo'yicha avtomatik
ajratiladi (`app/texts.py` dagi `PLATFORMS`). API javobidagi maydon nomlari sizning
panelingizda farq qilsa, `app/falcon_api.py` dagi `Service.from_dict` ni moslang.

## 🗄 Buyurtmalar tarixi — ASOS

Hozirgi tarix `app/storage.py` da **in-memory** (dastur qayta ishga tushsa o'chadi).
Doimiy saqlash uchun `OrderStorage` metodlarini SQLite/PostgreSQL bazasiga yozadigan
qilib qayta yozing — qolgan kodga tegmasdan.

## 🔒 Xavfsizlik

- `.env` fayli `.gitignore` ga kiritilgan — **TOKEN va API kalitni hech qachon commit qilmang**.
- Maxfiy ma'lumotlar faqat muhit o'zgaruvchilaridan o'qiladi.
