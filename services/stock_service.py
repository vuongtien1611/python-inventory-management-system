"""Service handling stock import/export and transaction history.

Implemented to satisfy integration tests (run_integration_tests.py).
"""

from __future__ import annotations

from typing import List, Dict, Any

from .inventory_manager import InventoryManager
from models.product import Product


class StockService:
    """Manage stock movements for products.

    Attributes:
        inventory: InventoryManager instance used to locate products.
        _history: List of transaction dicts.
    """

    def __init__(self, inventory: InventoryManager):
        self.inventory = inventory
        self._history: List[Dict[str, Any]] = []

    # ---- Helper ----
    def _record(self, product_id: str, qty: int, note: str, kind: str) -> Dict[str, Any]:
        transaction = {
            "product_id": product_id,
            "qty": qty,
            "note": note,
            "type": kind,
        }
        self._history.append(transaction)
        return transaction

    # ---- API required by integration test ----
    def import_stock(self, product_id: str, qty: int, note: str = "") -> Dict[str, Any]:
        self._validate_quantity(qty)
        product = self.inventory.get_product_by_id(product_id)
        if product is None:
            raise ValueError(f"Không tìm thấy sản phẩm {product_id}")
        # increase quantity
        product.quantity += qty
        return self._record(product_id, qty, note, "import")

    def export_stock(self, product_id: str, qty: int, note: str = "") -> Dict[str, Any]:
        self._validate_quantity(qty)
        product = self.inventory.get_product_by_id(product_id)
        if product is None:
            raise ValueError(f"Không tìm thấy sản phẩm {product_id}")
        if qty > product.quantity:
            raise ValueError("Không đủ tồn kho để xuất")
        product.quantity -= qty
        return self._record(product_id, qty, note, "export")

    @staticmethod
    def _validate_quantity(qty: int) -> None:
        if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
            raise ValueError("Số lượng giao dịch phải là số nguyên dương")

    def get_transaction_history(self, product_id: str | None = None) -> List[Dict[str, Any]]:
        if product_id is None:
            return list(self._history)
        return [h for h in self._history if h["product_id"] == product_id]
