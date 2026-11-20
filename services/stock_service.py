"""Service handling stock import/export and transaction history.

Implemented to satisfy integration tests (run_integration_tests.py).
"""
from models.stock_transaction import StockTransaction

<<<<<<< HEAD
class StockService:
    """Module xử lý nghiệp vụ nhập kho, xuất kho và theo dõi lịch sử giao dịch."""
    
    def __init__(self, inventory_manager=None):
        """
        :param inventory_manager: Đối tượng quản lý kho/sản phẩm (InventoryManager hoặc tương đương)
        """
        self.inventory_manager = inventory_manager
        # Từ điển lưu kho nội bộ dự phòng nếu chưa có InventoryManager: { product_id: quantity }
        self._local_stock = {}
        self.transaction_history = []

    def _get_current_stock(self, product_id: str) -> int:
        """Lấy số lượng tồn kho hiện tại của sản phẩm."""
        if self.inventory_manager and hasattr(self.inventory_manager, 'get_stock'):
            return self.inventory_manager.get_stock(product_id)
        return self._local_stock.get(product_id, 0)

    def _set_current_stock(self, product_id: str, new_quantity: int):
        """Cập nhật số lượng tồn kho mới."""
        if self.inventory_manager and hasattr(self.inventory_manager, 'update_stock'):
            self.inventory_manager.update_stock(product_id, new_quantity)
        else:
            self._local_stock[product_id] = new_quantity

    def import_stock(self, transaction_id: str, product_id: str, quantity: int, note: str = "") -> StockTransaction:
        """
        Thực hiện nghiệp vụ nhập kho:
        - Kiểm tra số lượng hợp lệ (> 0).
        - Tăng số lượng tồn kho.
        - Ghi nhận lịch sử StockTransaction.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Số lượng nhập kho không hợp lệ (phải là số nguyên > 0).")

        current_stock = self._get_current_stock(product_id)
        new_stock = current_stock + quantity
        self._set_current_stock(product_id, new_stock)

        # Tạo và ghi nhận giao dịch
        transaction = StockTransaction(transaction_id, product_id, "IMPORT", quantity, note)
        self.transaction_history.append(transaction)
        
        print(f"[SUCCESS] Nhập kho thành công: +{quantity} cho sản phẩm {product_id}. Tồn kho mới: {new_stock}")
        return transaction

    def export_stock(self, transaction_id: str, product_id: str, quantity: int, note: str = "") -> StockTransaction:
        """
        Thực hiện nghiệp vụ xuất kho:
        - Kiểm tra số lượng hợp lệ (> 0).
        - Kiểm tra tồn kho có đủ không (từ chối nếu vượt quá tồn kho hiện tại).
        - Giảm số lượng tồn kho.
        - Ghi nhận lịch sử StockTransaction.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Số lượng xuất kho không hợp lệ (phải là số nguyên > 0).")

        current_stock = self._get_current_stock(product_id)
        if quantity > current_stock:
            raise ValueError(f"Từ chối xuất kho! Số lượng yêu cầu ({quantity}) vượt quá số lượng tồn kho hiện tại ({current_stock}).")

        new_stock = current_stock - quantity
        self._set_current_stock(product_id, new_stock)

        # Tạo và ghi nhận giao dịch
        transaction = StockTransaction(transaction_id, product_id, "EXPORT", quantity, note)
        self.transaction_history.append(transaction)
        
        print(f"[SUCCESS] Xuất kho thành công: -{quantity} cho sản phẩm {product_id}. Tồn kho mới: {new_stock}")
        return transaction

    def get_transaction_history(self, product_id: str = None):
        """Truy vấn toàn bộ hoặc lọc lịch sử giao dịch theo mã sản phẩm."""
        if product_id:
            return [tx for tx in self.transaction_history if tx.product_id == product_id]
        return self.transaction_history
=======
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
>>>>>>> origin/main
