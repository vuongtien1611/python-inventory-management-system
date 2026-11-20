"""Module định nghĩa mô hình Giao dịch kho (StockTransaction).

Người phụ trách: Thành viên 4 - Chi (nhánh `feature/stock-transactions`).

Lớp dự kiến triển khai:
- `StockTransaction`: Lưu trữ thông tin một giao dịch nhập kho hoặc xuất kho.

TODO (Chi):
- [ ] Thiết kế và cài đặt lớp `StockTransaction` (mã giao dịch, mã sản phẩm, loại giao dịch nhập/xuất, số lượng, thời gian, ghi chú, ...).
- [ ] Áp dụng đóng gói và kiểm tra dữ liệu giao dịch hợp lệ (số lượng > 0, loại giao dịch hợp lệ).
- [ ] Cài đặt `__str__()` để hiển thị lịch sử giao dịch rõ ràng trên Console.
"""

from datetime import datetime


class StockTransaction:
    """Mô hình lưu trữ thông tin một giao dịch nhập/xuất kho."""

    def __init__(
        self,
        transaction_id: str,
        product_id: str,
        transaction_type: str,
        quantity: int,
        note: str = "",
    ):
        self.transaction_id = transaction_id
        self.product_id = product_id

        trans_type_upper = transaction_type.upper()
        if trans_type_upper not in ("IMPORT", "EXPORT"):
            raise ValueError("Loại giao dịch phải là 'IMPORT' hoặc 'EXPORT'.")
        self.transaction_type = trans_type_upper

        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Số lượng giao dịch phải là số nguyên lớn hơn 0.")
        self.quantity = quantity

        self.timestamp = datetime.now()
        self.note = note

    def to_dict(self) -> dict:
        """Chuyển thông tin giao dịch thành dictionary."""
        return {
            "transaction_id": self.transaction_id,
            "product_id": self.product_id,
            "transaction_type": self.transaction_type,
            "quantity": self.quantity,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "note": self.note,
        }

    def __str__(self) -> str:
        """Hiển thị thông tin giao dịch rõ ràng trên Console."""
        type_label = "Nhập kho" if self.transaction_type == "IMPORT" else "Xuất kho"
        time_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        note_part = f" | Ghi chú: {self.note}" if self.note else ""
        return (
            f"[{time_str}] Mã GD: {self.transaction_id} | {type_label} | "
            f"SP: {self.product_id} | SL: {self.quantity}{note_part}"
        )