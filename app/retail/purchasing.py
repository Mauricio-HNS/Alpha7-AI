"""Motor determinístico de reposição para o Alpha7 Retail MVP."""
from __future__ import annotations

from decimal import Decimal

from .models import Product, PurchaseRecommendation


def recommend_purchase(product: Product, daily_sales: float, safety_days: int = 7) -> PurchaseRecommendation | None:
    """Calcula uma compra sugerida usando vendas, lead time e estoque de segurança.

    O cálculo é deliberadamente determinístico: a IA pode explicar a decisão,
    mas não substitui a regra de negócio responsável pela quantidade.
    """
    if daily_sales <= 0:
        return None

    target_stock = daily_sales * (product.lead_time_days + safety_days)
    if product.stock >= target_stock and product.stock >= product.minimum_stock:
        return None

    quantity = max(
        product.minimum_stock - product.stock,
        int(target_stock - product.stock + 0.9999),
    )
    quantity = max(quantity, 1)
    estimated_cost = Decimal(quantity) * product.unit_cost

    if product.stock <= product.minimum_stock:
        urgency = "alta"
    elif product.stock < daily_sales * product.lead_time_days:
        urgency = "crítica"
    else:
        urgency = "normal"

    reason = (
        f"Estoque atual {product.stock}; vendas médias de {daily_sales:.2f}/dia; "
        f"lead time de {product.lead_time_days} dias; estoque de segurança de {safety_days} dias."
    )
    return PurchaseRecommendation(product, quantity, estimated_cost, reason, urgency)


def purchase_order(recommendations: list[PurchaseRecommendation]) -> dict[str, object]:
    """Agrupa recomendações em um pedido de compra pronto para aprovação."""
    if not recommendations:
        return {"supplier": None, "items": [], "total": Decimal("0")}

    suppliers = {item.supplier for item in recommendations}
    if len(suppliers) != 1:
        raise ValueError("Todas as recomendações do pedido devem pertencer ao mesmo fornecedor.")

    return {
        "supplier": recommendations[0].supplier,
        "items": [
            {
                "sku": item.product.sku,
                "name": item.product.name,
                "size": item.product.size,
                "color": item.product.color,
                "quantity": item.quantity,
                "unit_cost": item.product.unit_cost,
                "total": item.estimated_cost,
                "urgency": item.urgency,
                "reason": item.reason,
            }
            for item in recommendations
        ],
        "total": sum((item.estimated_cost for item in recommendations), Decimal("0")),
    }
