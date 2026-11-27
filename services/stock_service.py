"""Service handling stock import/export and transaction history."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from models.stock_transaction import StockTransaction

from .inventory_manager import InventoryManager


class StockService:
    """Xử lý nghiệp vụ nhập kho, xuất kho và theo dõi lịch sử giao dịch."""

    def __init__(self, inventory: Optional[InventoryManager] = None, inventory_manager: Optional[InventoryManager] = None):
        self.inventory = inventory if inventory is not None else inventory_manager
        self._local_stock: Dict[str, int] = {}
        self._history: List[Dict[str, Any]] = []
        self.transactions: List[StockTransaction] = []

    @staticmethod
    def _validate_quantity(qty: int) -> None:
        if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
            raise ValueError("Số lượng giao dịch phải là số nguyên dương lớn hơn 0.")

    def _get_product_and_stock(self, product_id: str) -> tuple[Any, int]:
        if self.inventory is not None and hasattr(self.inventory, "get_product_by_id"):
            product = self.inventory.get_product_by_id(product_id)
            if product is None:
                raise ValueError(f"Không tìm thấy sản phẩm {product_id}.")
            current_qty = getattr(product, "quantity", 0)
            return product, current_qty
        return None, self._local_stock.get(product_id, 0)

    def _update_stock(self, product: Any, product_id: str, new_qty: int) -> None:
        if product is not None:
            product.quantity = new_qty
        else:
            self._local_stock[product_id] = new_qty

    def _record_transaction(
        self,
        product_id: str,
        qty: int,
        note: str,
        tx_type: str,
        transaction_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        tx_id = transaction_id or f"TX-{len(self._history) + 1:04d}"
        tx_model = StockTransaction(
            transaction_id=tx_id,
            product_id=product_id,
            transaction_type=tx_type,
            quantity=qty,
            note=note,
        )
        self.transactions.append(tx_model)

        record = {
            "transaction_id": tx_id,
            "product_id": product_id,
            "qty": qty,
            "quantity": qty,
            "note": note,
            "type": tx_type.lower(),
            "transaction_type": tx_type,
            "timestamp": tx_model.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self._history.append(record)
        return record

    def import_stock(
        self,
        product_id: str,
        qty: int,
        note: str = "",
        transaction_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Nhập kho sản phẩm và ghi nhận lịch sử giao dịch."""
        self._validate_quantity(qty)
        product, current_stock = self._get_product_and_stock(product_id)
        new_stock = current_stock + qty
        self._update_stock(product, product_id, new_stock)
        return self._record_transaction(product_id, qty, note, "IMPORT", transaction_id)

    def export_stock(
        self,
        product_id: str,
        qty: int,
        note: str = "",
        transaction_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Xuất kho sản phẩm, kiểm tra tồn kho và ghi nhận lịch sử giao dịch."""
        self._validate_quantity(qty)
        product, current_stock = self._get_product_and_stock(product_id)
        if qty > current_stock:
            raise ValueError(
                f"Không đủ tồn kho để xuất (yêu cầu: {qty}, tồn kho hiện tại: {current_stock})."
            )
        new_stock = current_stock - qty
        self._update_stock(product, product_id, new_stock)
        return self._record_transaction(product_id, qty, note, "EXPORT", transaction_id)

    def get_transaction_history(self, product_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lấy toàn bộ lịch sử giao dịch hoặc lọc theo mã sản phẩm."""
        if product_id is None:
            return list(self._history)
        return [item for item in self._history if item["product_id"] == product_id]