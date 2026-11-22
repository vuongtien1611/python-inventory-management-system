"""Module xử lý nghiệp vụ nhập kho, xuất kho và lịch sử giao dịch (Design Baseline v1.0)."""

from __future__ import annotations

from typing import Any
import uuid

from models.product import FoodProduct
from models.stock_transaction import StockTransaction


class StockService:
    """Dịch vụ xử lý giao dịch kho hàng đảm bảo tính nguyên tử và bảo vệ tồn kho."""

    def __init__(
        self,
        inventory_manager: Any = None,
        transactions: list[StockTransaction] | None = None,
    ) -> None:
        self.inventory_manager = inventory_manager
        self._transactions: list[StockTransaction] = []
        if transactions:
            for tx in transactions:
                if isinstance(tx, StockTransaction):
                    self._transactions.append(tx)

    def import_stock(
        self,
        product_id: str,
        quantity: int,
        note: str = "",
    ) -> StockTransaction:
        """Thực hiện nhập kho sản phẩm (Q23, Q25, Q27, Q10).

        - Tự động sinh transaction_id qua UUID4.
        - Từ chối số lượng âm, 0 hoặc kiểu bool.
        - Từ chối nhập thực phẩm đã hết hạn (Q10).
        - Thực hiện atomic rollback nếu ghi nhận giao dịch thất bại (Q27).
        """
        # Kiểm tra kiểu và giá trị số lượng (Q23)
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise TypeError("Số lượng nhập kho phải là số nguyên.")
        if quantity <= 0:
            raise ValueError("Số lượng nhập kho phải là số nguyên dương (> 0).")

        if self.inventory_manager is None:
            raise RuntimeError("InventoryManager chưa được khởi tạo trong StockService.")

        product = self.inventory_manager.get_product_by_id(product_id)

        # Ràng buộc Q10: Không cho phép nhập thực phẩm đã hết hạn
        if isinstance(product, FoodProduct) and product.is_expired():
            raise ValueError(
                f"Cảnh báo! Không cho phép nhập thêm thực phẩm '{product_id}' đã hết hạn vào kho (Q10)."
            )

        # Cập nhật số lượng qua phương thức đóng gói của Product
        product.increase_stock(quantity)

        # Tạo và lưu giao dịch có bảo vệ Rollback (Q27)
        try:
            tx = StockTransaction(
                transaction_id=str(uuid.uuid4()),
                product_id=product_id,
                transaction_type="IMPORT",
                quantity=quantity,
                note=note,
            )
            self._transactions.append(tx)
            return tx
        except Exception as exc:
            # Atomic Rollback
            try:
                product.decrease_stock(quantity)
            except Exception as rollback_err:
                raise RuntimeError(
                    f"Sự cố nghiêm trọng: Không thể ghi nhận giao dịch nhập kho ({exc}) "
                    f"VÀ hoàn tác tồn kho thất bại ({rollback_err})! Dữ liệu kho có thể mất nhất quán."
                ) from exc
            raise RuntimeError(
                f"Ghi nhận giao dịch nhập kho thất bại ({exc}). Đã hoàn tác số lượng tồn kho an toàn."
            ) from exc

    def export_stock(
        self,
        product_id: str,
        quantity: int,
        note: str = "",
    ) -> StockTransaction:
        """Thực hiện xuất kho sản phẩm (Q23, Q24, Q25, Q27).

        - Tự động sinh transaction_id qua UUID4.
        - Kiểm tra tồn kho đủ xuất, cho phép xuất hết toàn bộ về 0 (Q24).
        - Thực hiện atomic rollback nếu ghi nhận giao dịch thất bại (Q27).
        """
        # Kiểm tra kiểu và giá trị số lượng (Q23)
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise TypeError("Số lượng xuất kho phải là số nguyên.")
        if quantity <= 0:
            raise ValueError("Số lượng xuất kho phải là số nguyên dương (> 0).")

        if self.inventory_manager is None:
            raise RuntimeError("InventoryManager chưa được khởi tạo trong StockService.")

        product = self.inventory_manager.get_product_by_id(product_id)

        # Kiểm tra tồn kho đủ (Q23, Q24)
        if quantity > product.quantity:
            raise ValueError(
                f"Không đủ tồn kho để xuất! Yêu cầu: {quantity}, Tồn hiện tại: {product.quantity}."
            )

        # Cập nhật số lượng qua phương thức đóng gói của Product
        product.decrease_stock(quantity)

        # Tạo và lưu giao dịch có bảo vệ Rollback (Q27)
        try:
            tx = StockTransaction(
                transaction_id=str(uuid.uuid4()),
                product_id=product_id,
                transaction_type="EXPORT",
                quantity=quantity,
                note=note,
            )
            self._transactions.append(tx)
            return tx
        except Exception as exc:
            # Atomic Rollback
            try:
                product.increase_stock(quantity)
            except Exception as rollback_err:
                raise RuntimeError(
                    f"Sự cố nghiêm trọng: Không thể ghi nhận giao dịch xuất kho ({exc}) "
                    f"VÀ hoàn tác tồn kho thất bại ({rollback_err})! Dữ liệu kho có thể mất nhất quán."
                ) from exc
            raise RuntimeError(
                f"Ghi nhận giao dịch xuất kho thất bại ({exc}). Đã hoàn tác số lượng tồn kho an toàn."
            ) from exc

    def get_transaction_history(
        self, product_id: str | None = None
    ) -> list[StockTransaction]:
        """Truy vấn danh sách lịch sử giao dịch (toàn bộ hoặc lọc theo mã sản phẩm - Q28)."""
        if product_id is not None:
            clean_id = str(product_id).strip()
            return [tx for tx in self._transactions if tx.product_id == clean_id]
        return list(self._transactions)

    def has_product_transactions(self, product_id: str) -> bool:
        """Kiểm tra sản phẩm đã từng phát sinh bất kỳ giao dịch kho nào chưa (Q20)."""
        clean_id = str(product_id).strip()
        return any(tx.product_id == clean_id for tx in self._transactions)

    def replace_transactions(self, transactions: list[StockTransaction]) -> None:
        """Thay thế toàn bộ lịch sử giao dịch (phục vụ nạp dữ liệu từ Storage)."""
        new_list: list[StockTransaction] = []
        for tx in transactions:
            if isinstance(tx, StockTransaction):
                new_list.append(tx)
        self._transactions = new_list
