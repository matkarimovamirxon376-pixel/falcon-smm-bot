"""FALCON SMM API bilan ishlash uchun aiohttp asosidagi client.

FALCON SMM API sanoat standartidagi "API v2" formatida ishlaydi:
  - Bitta endpoint (POST)
  - `key` + `action` parametrlari
  - JSON javob

Qo'llab-quvvatlanadigan action'lar:
  - services : barcha xizmatlar ro'yxati
  - add      : yangi buyurtma
  - status   : buyurtma holati (bitta ID)
  - orders   : bir nechta buyurtma holati (vergul bilan ajratilgan ID'lar)
  - balance  : hisob balansi
  - refill   : qayta to'ldirish so'rovi
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import aiohttp


class FalconAPIError(Exception):
    """FALCON SMM API xatosi."""


@dataclass
class Service:
    """Bitta SMM xizmati."""

    service_id: int
    name: str
    category: str
    rate: float          # 1000 dona uchun narx
    min: int
    max: int
    service_type: str = ""
    refill: bool = False
    cancel: bool = False
    dripfeed: bool = False
    currency: str = "USD"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Service":
        def _to_float(value: Any, default: float = 0.0) -> float:
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        def _to_int(value: Any, default: int = 0) -> int:
            try:
                return int(float(value))
            except (TypeError, ValueError):
                return default

        return cls(
            service_id=_to_int(data.get("service")),
            name=str(data.get("name", "")),
            category=str(data.get("category", "")),
            rate=_to_float(data.get("rate")),
            min=_to_int(data.get("min")),
            max=_to_int(data.get("max")),
            service_type=str(data.get("type", "")),
            refill=bool(data.get("refill", False)),
            cancel=bool(data.get("cancel", False)),
            dripfeed=bool(data.get("dripfeed", False)),
            currency=str(data.get("currency", "USD")),
        )


class FalconAPI:
    """FALCON SMM API client.

    Foydalanish:
        api = FalconAPI(api_url, api_key)
        services = await api.services()
        ...
        await api.close()
    """

    def __init__(self, api_url: str, api_key: str, timeout: int = 30) -> None:
        self._api_url = api_url
        self._api_key = api_key
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(self, payload: dict[str, Any]) -> Any:
        """API ga POST so'rov yuboradi va JSON javobni qaytaradi.

        Diqqat: SMM panellar ko'pincha xato bo'lganda ham HTTP 200 qaytaradi
        va xatoni javob tanasidagi `error` maydoniga joylaydi. Shuning uchun
        biz faqat status kodiga emas, balki javob tanasiga ham tayanamiz.
        """
        # Barcha qiymatlarni string'ga aylantiramiz (aiohttp form-data faqat
        # str/bytes qabul qiladi; int yuborilsa "quantity must be str" xatosi chiqadi).
        data = {"key": self._api_key}
        for key, value in payload.items():
            data[key] = str(value)

        session = await self._get_session()
        try:
            async with session.post(self._api_url, data=data) as resp:
                text = await resp.text()
                status = resp.status
                try:
                    result = await resp.json(content_type=None)
                except Exception:  # noqa: BLE001
                    # JSON emas — ehtimol HTML xato sahifasi yoki bo'sh javob
                    snippet = (text or "").strip()[:200]
                    if status != 200:
                        raise FalconAPIError(
                            f"API HTTP {status} xatosi qaytardi"
                            + (f": {snippet}" if snippet else ".")
                        )
                    if not snippet:
                        raise FalconAPIError(
                            "API bo'sh javob qaytardi. API manzili yoki kalitni "
                            "tekshiring."
                        )
                    raise FalconAPIError(
                        f"API javobini JSON sifatida o'qib bo'lmadi: {snippet}"
                    )
        except aiohttp.ClientError as exc:
            raise FalconAPIError(f"Tarmoq xatosi: {exc}") from exc

        # SMM panellar xatoni {"error": "..."} ko'rinishida qaytaradi
        # (odatda HTTP 200 bilan birga).
        if isinstance(result, dict):
            err = result.get("error")
            if err:
                raise FalconAPIError(self._humanize_error(str(err)))

        # HTTP status xato, lekin JSON'da error maydoni yo'q bo'lsa
        if status != 200:
            raise FalconAPIError(f"API HTTP {status} xatosi qaytardi.")

        return result

    @staticmethod
    def _humanize_error(err: str) -> str:
        """API ning inglizcha xatolarini foydalanuvchiga tushunarli qiladi."""
        low = err.lower()
        if "key" in low and ("incorrect" in low or "invalid" in low or "wrong" in low):
            return (
                "API kaliti noto'g'ri. .env faylidagi FALCON_API_KEY ni tekshiring "
                f"(API javobi: {err})."
            )
        if "action" in low:
            return f"API noto'g'ri so'rov deb hisobladi (action): {err}"
        if "balance" in low or "funds" in low:
            return f"Hisobda mablag' yetarli emas: {err}"
        return err

    # ------------------------------------------------------------------ #
    # Umumiy API metodlari
    # ------------------------------------------------------------------ #
    async def services(self) -> list[Service]:
        """Barcha xizmatlar ro'yxatini qaytaradi."""
        result = await self._request({"action": "services"})
        if not isinstance(result, list):
            raise FalconAPIError(
                "API xizmatlar ro'yxatini qaytarmadi. API kaliti yoki manzili "
                "noto'g'ri bo'lishi mumkin."
            )
        return [Service.from_dict(item) for item in result if isinstance(item, dict)]

    async def balance(self) -> dict[str, Any]:
        """Hisob balansini qaytaradi: {'balance': '...', 'currency': '...'}."""
        result = await self._request({"action": "balance"})
        if not isinstance(result, dict):
            raise FalconAPIError("Balans javobi kutilgan formatda emas.")
        # Ba'zi panellar error maydonisiz, lekin balance ham bermasligi mumkin
        if "balance" not in result:
            raise FalconAPIError(
                "API balansni qaytarmadi. API kaliti yoki manzili noto'g'ri "
                "bo'lishi mumkin."
            )
        return result

    async def add_order(
        self,
        service_id: int,
        link: str,
        quantity: int,
        **extra: Any,
    ) -> dict[str, Any]:
        """Yangi buyurtma qo'shadi. Javob: {'order': <id>}."""
        payload: dict[str, Any] = {
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity,
        }
        payload.update(extra)
        result = await self._request(payload)
        if not isinstance(result, dict):
            raise FalconAPIError("Buyurtma javobi kutilgan formatda emas.")
        return result

    async def order_status(self, order_id: int) -> dict[str, Any]:
        """Bitta buyurtma holatini qaytaradi."""
        result = await self._request({"action": "status", "order": order_id})
        if not isinstance(result, dict):
            raise FalconAPIError("Buyurtma holati kutilgan formatda emas.")
        return result

    async def orders_status(self, order_ids: list[int]) -> dict[str, Any]:
        """Bir nechta buyurtma holatini qaytaradi."""
        ids = ",".join(str(i) for i in order_ids)
        result = await self._request({"action": "orders", "orders": ids})
        if not isinstance(result, dict):
            raise FalconAPIError("Buyurtmalar holati kutilgan formatda emas.")
        return result

    async def refill(self, order_id: int) -> dict[str, Any]:
        """Buyurtma uchun qayta to'ldirish (refill) so'rovi."""
        result = await self._request({"action": "refill", "order": order_id})
        if not isinstance(result, dict):
            raise FalconAPIError("Refill javobi kutilgan formatda emas.")
        return result
