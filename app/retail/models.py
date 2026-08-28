"""Modelos de domínio para compras de varejo de moda/lingerie."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    category: str
    size: str
    color: str
    supplier: str
    unit_cost: Decimal
    unit_price: Decimal
    stock: int
    minimum_stock: int
    lead_time_days: int = 7


@dataclass(frozen=True)
class PurchaseRecommendation:
    product: Product
    quantity: int
    estimated_cost: Decimal
    reason: str
    urgency: str

    @property
    def supplier(self) -> str:
        return self.product.supplier
