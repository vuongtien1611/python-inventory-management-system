"""Module thống kê, báo cáo kho hàng và quản lý nghiệp vụ nhà cung cấp.

Người phụ trách: Thành viên 5 - Minh (nhánh `feature/supplier-reports`).

Lớp triển khai:
- ReportService: Cung cấp các chức năng:
  * Quản lý danh sách nhà cung cấp (CRUD Supplier).
  * Tính tổng giá trị hàng tồn kho.
  * Thống kê sản phẩm sắp hết hàng (theo ngưỡng tồn kho).
  * Thống kê thực phẩm (FoodProduct) gần hết hạn / đã hết hạn.
  * Thống kê thông tin bảo hành của thiết bị điện tử (ElectronicProduct).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from models.product import ElectronicProduct, FoodProduct, Product
from models.supplier import Supplier
from services.inventory_manager import InventoryManager


class ReportService:
    """Lớp cung cấp dịch vụ thống kê, báo cáo kho hàng
    và quản lý danh sách nhà cung cấp.
    """

    def __init__(
        self,
        inventory_manager: Any,
        suppliers: list[Supplier] | None = None,
        today: date | None = None,
    ) -> None:
        """Khởi tạo ReportService.

        Args:
            inventory_manager: Đối tượng InventoryManager cung cấp
                get_all_products() và get_product_by_id().
            suppliers: Danh sách Supplier ban đầu (tùy chọn).
            today: Ngày tham chiếu cho báo cáo (mặc định hôm nay).
        """
        if inventory_manager is None:
            raise TypeError(
                "inventory_manager không được là None. "
                "Hãy truyền đối tượng InventoryManager hợp lệ."
            )
        self.inventory_manager = inventory_manager
        self._inventory_manager = inventory_manager
        self._today = today or date.today()
        self._suppliers: dict[str, Supplier] = {}
        if suppliers:
            for s in suppliers:
                if isinstance(s, Supplier) and s.is_valid():
                    self._suppliers[s.supplier_id] = s

    # ================================================================== #
    #  PHẦN 1: QUẢN LÝ NHÀ CUNG CẤP (CRUD - Menu 2)
    # ================================================================== #

    def add_supplier(self, supplier: Supplier) -> None:
        """Thêm một nhà cung cấp vào danh sách.

        Args:
            supplier: Đối tượng Supplier cần thêm.

        Raises:
            TypeError: Nếu supplier không phải là instance của Supplier.
            ValueError: Nếu supplier không hợp lệ hoặc supplier_id đã tồn tại.
        """
        if not isinstance(supplier, Supplier):
            raise TypeError("Đối tượng truyền vào phải là instance của lớp Supplier.")
        if not supplier.is_valid():
            raise ValueError(
                "Thông tin nhà cung cấp không hợp lệ. Vui lòng kiểm tra lại dữ liệu."
            )
        if supplier.supplier_id in self._suppliers:
            raise ValueError(
                f"Mã nhà cung cấp '{supplier.supplier_id}' đã tồn tại. "
                "Không thể thêm trùng mã."
            )
        self._suppliers[supplier.supplier_id] = supplier

    def update_supplier(self, supplier_id: str, **fields: Any) -> None:
        """Cập nhật thông tin nhà cung cấp theo supplier_id.

        Hỗ trợ cập nhật: name, phone, address, email.
        Trường supplier_id không được phép thay đổi.
        """
        if supplier_id not in self._suppliers:
            raise KeyError(f"Không tìm thấy nhà cung cấp với mã '{supplier_id}'.")
        if "supplier_id" in fields:
            raise ValueError("Không được phép thay đổi mã nhà cung cấp.")

        supplier = self._suppliers[supplier_id]
        allowed_fields = {"name", "phone", "address", "email"}
        invalid_fields = set(fields.keys()) - allowed_fields
        if invalid_fields:
            raise ValueError(
                f"Trường không hợp lệ: {', '.join(invalid_fields)}. "
                f"Các trường được phép: {', '.join(sorted(allowed_fields))}."
            )

        old_values: dict[str, Any] = {}
        for key in fields:
            old_values[key] = getattr(supplier, key)

        try:
            for key, value in fields.items():
                setattr(supplier, key, value)
        except (TypeError, ValueError) as err:
            for key, old_val in old_values.items():
                try:
                    setattr(supplier, key, old_val)
                except Exception:
                    pass
            raise ValueError(f"Cập nhật nhà cung cấp thất bại: {err}") from err

    def delete_supplier(self, supplier_id: str) -> None:
        """Xóa nhà cung cấp khỏi danh sách.

        Kiểm tra xem có sản phẩm nào trong kho đang tham chiếu đến
        nhà cung cấp này không. Nếu có, từ chối xóa.
        """
        if supplier_id not in self._suppliers:
            raise KeyError(f"Không tìm thấy nhà cung cấp với mã '{supplier_id}'.")

        try:
            all_products = self.inventory_manager.get_all_products()
        except Exception:
            all_products = []

        linked_products = []
        for product in all_products:
            product_supplier = getattr(product, "supplier", "") or ""
            product_supplier_id = getattr(product, "supplier_id", "") or ""
            if supplier_id in (product_supplier, product_supplier_id):
                linked_products.append(product)

        if linked_products:
            product_names = ", ".join(
                getattr(p, "name", getattr(p, "product_id", "?"))
                for p in linked_products
            )
            raise ValueError(
                f"Không thể xóa nhà cung cấp '{supplier_id}' vì đang có "
                f"{len(linked_products)} sản phẩm liên kết: {product_names}. "
                "Hãy xóa hoặc chuyển đổi nhà cung cấp trước khi xóa."
            )

        del self._suppliers[supplier_id]

    def get_all_suppliers(self) -> list[Supplier]:
        """Trả về danh sách tất cả nhà cung cấp."""
        return list(self._suppliers.values())

    def get_supplier_by_id(self, supplier_id: str) -> Supplier | None:
        """Tìm nhà cung cấp theo mã."""
        return self._suppliers.get(supplier_id)

    # ================================================================== #
    #  PHẦN 2: THỐNG KÊ & BÁO CÁO (Menu 5 & Menu 6)
    # ================================================================== #

    def get_total_inventory_value(self) -> float:
        """Tính tổng giá trị hàng tồn kho toàn bộ."""
        return sum(
            product.get_inventory_value()
            for product in self.inventory_manager.get_all_products()
        )

    def get_low_stock_products(self, threshold: int = 5) -> list[Any]:
        """Trả về danh sách sản phẩm có tồn kho thấp (sắp hết hàng)."""
        if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 0:
            raise ValueError("Ngưỡng tồn kho phải là số nguyên không âm")
        return [
            p for p in self.inventory_manager.get_all_products()
            if p.quantity <= threshold
        ]

    def get_expiring_food_products(self, days: int = 7) -> list[FoodProduct]:
        """Trả về danh sách thực phẩm sắp hết hạn trong days ngày tới hoặc đã hết hạn."""
        if isinstance(days, bool) or not isinstance(days, int) or days < 0:
            raise ValueError("Số ngày phải là số nguyên không âm")
        deadline = self._today + timedelta(days=days)
        result = []
        for product in self.inventory_manager.get_all_products():
            if isinstance(product, FoodProduct) and self._expiry_date(product) <= deadline:
                result.append(product)
        return result

    def check_food_expiry_status(
        self, product_id: str | None = None
    ) -> list[dict[str, Any]]:
        """Kiểm tra và phân loại trạng thái hạn sử dụng của thực phẩm."""
        products = self.inventory_manager.get_all_products()
        result = []
        for product in products:
            if not isinstance(product, FoodProduct) or (product_id and product.product_id != product_id):
                continue
            expiry = self._expiry_date(product)
            result.append({
                "product_id": product.product_id,
                "name": product.name,
                "expiry_date": expiry.isoformat(),
                "status": "expired" if expiry < self._today else "valid",
                "days_remaining": (expiry - self._today).days,
            })
        return result

    def get_warranty_summary(
        self, product_id: str | None = None
    ) -> list[dict[str, Any]]:
        """Thống kê thông tin bảo hành của thiết bị điện tử."""
        result = []
        for product in self.inventory_manager.get_all_products():
            if isinstance(product, ElectronicProduct) and (product_id is None or product.product_id == product_id):
                result.append({
                    "product_id": product.product_id,
                    "name": product.name,
                    "warranty_months": product.warranty_months,
                })
        return result

    @staticmethod
    def _expiry_date(product: Any) -> date:
        """Chuyển đổi expiry_date của sản phẩm thành đối tượng date."""
        value = getattr(product, "expiry_date", None)
        if isinstance(value, date):
            return value
        try:
            return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Ngày hết hạn của {getattr(product, 'product_id', '')} phải theo YYYY-MM-DD"
            ) from exc
