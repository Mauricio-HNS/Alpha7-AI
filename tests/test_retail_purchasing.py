from decimal import Decimal

import pytest

from app.retail.models import Product
from app.retail.purchasing import purchase_order, recommend_purchase


def product(stock: int = 7) -> Product:
    return Product(
        "SUT-2048", "Sutiã Rendado Preto", "Lingerie", "40", "Preto",
        "Fashion Supplier SL", Decimal("8.20"), Decimal("29.90"), stock, 15, 8
    )


def test_recommends_replenishment_when_stock_is_low():
    recommendation = recommend_purchase(product(), daily_sales=2.73, safety_days=7)
    assert recommendation is not None
    assert recommendation.quantity == 34
    assert recommendation.estimated_cost == Decimal("278.80")
    assert recommendation.urgency == "alta"


def test_does_not_recommend_when_stock_covers_target():
    assert recommend_purchase(product(stock=100), daily_sales=2.73) is None


def test_purchase_order_groups_items_by_supplier():
    first = recommend_purchase(product(), daily_sales=2.73)
    assert first is not None
    order = purchase_order([first])
    assert order["supplier"] == "Fashion Supplier SL"
    assert order["total"] == Decimal("278.80")


def test_purchase_order_rejects_multiple_suppliers():
    first = recommend_purchase(product(), daily_sales=2.73)
    assert first is not None
    other = Product("BODY-1", "Body", "Moda", "M", "Vinho", "Outro", Decimal("10"), Decimal("30"), 1, 5, 7)
    second = recommend_purchase(other, daily_sales=1.0)
    assert second is not None
    with pytest.raises(ValueError):
        purchase_order([first, second])
