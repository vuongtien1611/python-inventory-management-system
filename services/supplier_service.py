"""Module quản lý thông tin nhà cung cấp (CRUD Supplier) – Design Baseline v1.0 (Q16)."""

from __future__ import annotations

from typing import Any
from models.supplier import Supplier


class SupplierService:
    """Dịch vụ quản lý danh mục nhà cung cấp độc lập (tách khỏi ReportService theo Q16)."""

    def __init__(self, suppliers: list[Supplier] | None = None) -> None:
        self._suppliers: dict[str, Supplier] = {}
        for s in suppliers or []:
            if isinstance(s, Supplier) and s.is_valid():
                self._suppliers[s.supplier_id] = s

    def add_supplier(self, supplier: Supplier) -> None:
        """Thêm mới nhà cung cấp, chống trùng supplier_id (Q16)."""
        if not isinstance(supplier, Supplier):
            raise TypeError("Đối tượng thêm phải là instance của Supplier.")
        if not supplier.is_valid():
            raise ValueError("Thông tin nhà cung cấp không hợp lệ.")
        if supplier.supplier_id in self._suppliers:
            raise ValueError(f"Mã nhà cung cấp '{supplier.supplier_id}' đã tồn tại.")
        self._suppliers[supplier.supplier_id] = supplier

    def update_supplier(self, supplier_id: str, **fields: Any) -> None:
        """Cập nhật thông tin nhà cung cấp (cấm đổi supplier_id)."""
        supplier = self._suppliers.get(supplier_id)
        if supplier is None:
            raise KeyError(f"Không tìm thấy nhà cung cấp có mã: {supplier_id}")

        if "supplier_id" in fields and fields["supplier_id"] != supplier_id:
            raise ValueError("Không được phép thay đổi mã nhà cung cấp.")

        allowed = {"name", "phone", "address", "email"}
        unknown = set(fields.keys()) - allowed - {"supplier_id"}
        if unknown:
            raise ValueError(f"Trường cập nhật không hỗ trợ: {', '.join(sorted(unknown))}")

        # Tạo bản sao cập nhật thử nghiệm để đảm bảo validation
        current = supplier.to_dict()
        for k, v in fields.items():
            if k in allowed and v is not None:
                current[k] = v

        candidate = Supplier(**current)
        if not candidate.is_valid():
            raise ValueError("Dữ liệu cập nhật nhà cung cấp không hợp lệ.")
        self._suppliers[supplier_id] = candidate

    def delete_supplier(self, supplier_id: str, inventory_manager: Any = None) -> None:
        """Xóa nhà cung cấp, kiểm tra ràng buộc không có sản phẩm tham chiếu (Q15)."""
        if supplier_id not in self._suppliers:
            raise KeyError(f"Không tìm thấy nhà cung cấp có mã: {supplier_id}")

        if inventory_manager is not None and hasattr(inventory_manager, "get_all_products"):
            all_products = inventory_manager.get_all_products()
            referenced = [
                p for p in all_products
                if getattr(p, "supplier_id", "") == supplier_id or getattr(p, "supplier", "") == supplier_id
            ]
            if referenced:
                ref_names = ", ".join(p.product_id for p in referenced[:3])
                raise ValueError(
                    f"Không thể xóa nhà cung cấp '{supplier_id}' vì vẫn còn sản phẩm liên kết: {ref_names}."
                )

        del self._suppliers[supplier_id]

    def get_supplier_by_id(self, supplier_id: str) -> Supplier:
        """Lấy thông tin nhà cung cấp theo mã, ném KeyError nếu không tìm thấy."""
        if supplier_id not in self._suppliers:
            raise KeyError(f"Không tìm thấy nhà cung cấp có mã: {supplier_id}")
        return self._suppliers[supplier_id]

    def get_all_suppliers(self) -> list[Supplier]:
        """Trả về danh sách bản sao tất cả nhà cung cấp."""
        return list(self._suppliers.values())

    def has_supplier(self, supplier_id: str) -> bool:
        """Kiểm tra nhanh sự tồn tại của nhà cung cấp."""
        return str(supplier_id).strip() in self._suppliers

