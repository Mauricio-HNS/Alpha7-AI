"""Demo comercial do Alpha7 Retail: estoque -> previsão -> compra -> aprovação."""
from __future__ import annotations

from decimal import Decimal

from .models import Product
from .purchasing import purchase_order, recommend_purchase


def run_demo() -> dict[str, object]:
    products = [
        Product("SUT-2048", "Sutiã Rendado Preto", "Lingerie", "40", "Preto", "Fashion Supplier SL", Decimal("8.20"), Decimal("29.90"), 7, 15, 8),
        Product("CAL-1032", "Calcinha Renda", "Lingerie", "M", "Preto", "Fashion Supplier SL", Decimal("3.40"), Decimal("14.90"), 18, 12, 6),
        Product("BODY-778", "Body Básico", "Moda", "M", "Vinho", "Moda Iberia", Decimal("11.00"), Decimal("39.90"), 4, 10, 10),
    ]
    daily_sales = {"SUT-2048": 2.73, "CAL-1032": 0.40, "BODY-778": 1.10}

    recommendations = [
        recommendation
        for product in products
        for recommendation in [recommend_purchase(product, daily_sales[product.sku])]
        if recommendation is not None
    ]

    by_supplier: dict[str, list] = {}
    for recommendation in recommendations:
        by_supplier.setdefault(recommendation.supplier, []).append(recommendation)

    return {
        "recommendations": recommendations,
        "orders": [purchase_order(items) for items in by_supplier.values()],
    }


if __name__ == "__main__":
    result = run_demo()
    for order in result["orders"]:
        print(f"Fornecedor: {order['supplier']}")
        print(f"Total recomendado: €{order['total']}")
        for item in order["items"]:
            print(f"  {item['sku']} | {item['name']} | comprar {item['quantity']} | €{item['total']}")
