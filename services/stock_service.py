"""Module xử lý nghiệp vụ nhập kho, xuất kho và theo dõi lịch sử giao dịch.

Người phụ trách: Thành viên 4 - Chi (nhánh `feature/stock-transactions`).

Lớp dự kiến triển khai:
- `StockService`

Các phương thức dự kiến:
- `import_stock()`
- `export_stock()`
- `get_transaction_history()`

Yêu cầu nghiệp vụ:
- Nhập kho làm tăng số lượng tồn kho của sản phẩm tương ứng.
- Xuất kho làm giảm số lượng tồn kho của sản phẩm tương ứng.
- Không cho phép xuất kho vượt quá số lượng tồn hiện tại.
- Không chấp nhận số lượng giao dịch không hợp lệ (<= 0 hoặc sai kiểu dữ liệu).
- Lưu đầy đủ thông tin mỗi giao dịch nhập/xuất thông qua `StockTransaction`.

TODO (Chi):
- [ ] Cài đặt lớp `StockService` liên kết với danh sách sản phẩm / `InventoryManager`.
- [ ] Cài đặt `import_stock()` kiểm tra số lượng hợp lệ, tăng tồn kho và ghi nhận `StockTransaction`.
- [ ] Cài đặt `export_stock()` kiểm tra tồn kho đủ trước khi trừ số lượng và ghi nhận giao dịch.
- [ ] Cài đặt `get_transaction_history()` để truy vấn toàn bộ hoặc lọc lịch sử giao dịch.
"""
from models.stock_transaction import StockTransaction

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
