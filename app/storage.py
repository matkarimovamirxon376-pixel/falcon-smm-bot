"""Buyurtmalar tarixi uchun oddiy in-memory saqlagich.

Bu — buyurtmalar tarixini ko'rsatish uchun ASOS (foundation).
Keyinchalik uni SQLite/PostgreSQL bilan almashtirish oson:
faqat shu klassning metodlarini bazaga yozadigan qilib qayta yozing.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OrderRecord:
    order_id: int
    service_id: int
    service_name: str
    link: str
    quantity: int
    price: float


class OrderStorage:
    """Foydalanuvchi -> buyurtmalar ro'yxati."""

    def __init__(self) -> None:
        self._data: dict[int, list[OrderRecord]] = {}

    def add(self, user_id: int, record: OrderRecord) -> None:
        self._data.setdefault(user_id, []).append(record)

    def get(self, user_id: int) -> list[OrderRecord]:
        return list(self._data.get(user_id, []))

    def all_order_ids(self, user_id: int) -> list[int]:
        return [r.order_id for r in self._data.get(user_id, [])]
