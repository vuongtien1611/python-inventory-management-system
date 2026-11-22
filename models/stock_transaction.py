"""Module định nghĩa mô hình Giao dịch kho (StockTransaction) – Design Baseline v1.0."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import uuid


class StockTransaction:
    """Lớp đại diện cho một bản ghi giao dịch nhập hoặc xuất kho (bất biến sau khi tạo - Q28)."""

    def __init__(
        self,
        transaction_id: str = "",
        product_id: str = "",
        transaction_type: str = "IMPORT",
        quantity: int = 1,
        timestamp: str = "",
        note: str = "",
    ) -> None:
        # Tự sinh UUID nếu chưa có (Q25)
        self._transaction_id = str(transaction_id).strip() or str(uuid.uuid4())

        p_id = str(product_id).strip()
        if not p_id:
            raise ValueError("Mã sản phẩm trong giao dịch không được để trống.")
        self._product_id = p_id

        t_type = str(transaction_type).strip().upper()
        if t_type not in {"IMPORT", "EXPORT"}:
            raise ValueError("Loại giao dịch phải là 'IMPORT' hoặc 'EXPORT'.")
        self._transaction_type = t_type

        # Kiểm tra số lượng giao dịch: số nguyên dương, từ chối bool (Q23)
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise TypeError("Số lượng giao dịch phải là số nguyên.")
        if quantity <= 0:
            raise ValueError("Số lượng giao dịch phải là số nguyên dương (> 0).")
        self._quantity = quantity

        # Thời gian giao dịch ISO 8601 có timezone (Q26)
        if timestamp and str(timestamp).strip():
            self._timestamp = str(timestamp).strip()
        else:
            self._timestamp = datetime.now().astimezone().isoformat()

        self._note = str(note).strip()

    # ---------- READ-ONLY PROPERTIES (Q28) ----------
    @property
    def transaction_id(self) -> str:
        return self._transaction_id

    @property
    def product_id(self) -> str:
        return self._product_id

    @property
    def transaction_type(self) -> str:
        return self._transaction_type

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def timestamp(self) -> str:
        return self._timestamp

    @property
    def note(self) -> str:
        return self._note

    # ---------- SERIALIZATION & STRING ----------
    def to_dict(self) -> dict[str, Any]:
        """Xuất dictionary để lưu trữ JSON (Q33)."""
        return {
            "transaction_id": self.transaction_id,
            "product_id": self.product_id,
            "transaction_type": self.transaction_type,
            "quantity": self.quantity,
            "timestamp": self.timestamp,
            "note": self.note,
        }

    def __str__(self) -> str:
        type_str = "Nhập kho" if self.transaction_type == "IMPORT" else "Xuất kho"
        note_str = f" | Ghi chú: {self.note}" if self.note else ""
        return (
            f"[{self.timestamp}] Mã GD: {self.transaction_id} | "
            f"{type_str} | Mã SP: {self.product_id} | "
            f"SL: {self.quantity}{note_str}"
        )

    def __repr__(self) -> str:
        return (
            f"StockTransaction(transaction_id={self.transaction_id!r}, "
            f"product_id={self.product_id!r}, transaction_type={self.transaction_type!r}, "
            f"quantity={self.quantity!r}, timestamp={self.timestamp!r})"
        )
