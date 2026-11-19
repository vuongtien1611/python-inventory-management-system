"""Module quản lý danh mục sản phẩm trong kho (CRUD, tìm kiếm, sắp xếp) – Design Baseline v1.0."""

from __future__ import annotations

from typing import Any
from models.product import ElectronicProduct, FoodProduct, Product


class InventoryManager:
    """Lớp quản lý tập trung danh mục sản phẩm trong kho."""

    def __init__(self, products: list[Product] | None = None) -> None:
        self._products: dict[str, Product] = {}
        for product in products or []:
            if isinstance(product, Product):
                self.add_product(product)

    def add_product(self, product: Product, supplier_service: Any = None) -> None:
        """Thêm sản phẩm mới vào kho.

        Kiểm tra: tính hợp lệ, chống trùng mã (Q06), kiểm tra nhà cung cấp tồn tại (Q14).
        """
        if not isinstance(product, Product):
            raise TypeError("Đối tượng thêm phải là instance của Product.")
        if not product.is_valid():
            raise ValueError("Dữ liệu sản phẩm không hợp lệ.")
        if product.product_id in self._products:
            raise ValueError(f"Mã sản phẩm '{product.product_id}' đã tồn tại trong kho.")

        # Xác thực nhà cung cấp tồn tại (Q14)
        if supplier_service is not None and hasattr(supplier_service, "has_supplier"):
            sup_id = getattr(product, "supplier_id", "") or getattr(product, "supplier", "")
            if sup_id and not supplier_service.has_supplier(sup_id):
                raise ValueError(
                    f"Mã nhà cung cấp '{sup_id}' không tồn tại trong hệ thống. "
                    "Vui lòng tạo nhà cung cấp trước khi gán sản phẩm."
                )

        self._products[product.product_id] = product

    def update_product(self, product_id: str, **fields: Any) -> None:
        """Cập nhật thông tin mô tả sản phẩm.

        Tuyệt đối cấm sửa đổi trực tiếp số lượng tồn kho quantity (Q08).
        """
        product = self._products.get(product_id)
        if product is None:
            raise KeyError(f"Không tìm thấy sản phẩm có mã: {product_id}")

        # Ràng buộc Q08: Cấm sửa quantity qua CRUD
        if "quantity" in fields:
            raise ValueError(
                "Tuyệt đối cấm cập nhật số lượng tồn kho (quantity) qua chức năng cập nhật sản phẩm! "
                "Số lượng tồn kho chỉ được phép thay đổi thông qua nghiệp vụ Nhập/Xuất kho của StockService."
            )

        if "product_id" in fields and fields["product_id"] != product_id:
            raise ValueError("Không được phép thay đổi mã sản phẩm.")

        allowed = {"name", "price", "supplier_id", "supplier", "expiry_date", "warranty_months"}
        unknown = set(fields.keys()) - allowed - {"product_id"}
        if unknown:
            raise ValueError(f"Trường cập nhật không được hỗ trợ: {', '.join(sorted(unknown))}")

        # Chuẩn bị dữ liệu cập nhật
        data = product.to_dict()
        data.pop("type", None)
        data.pop("supplier", None)

        if "supplier" in fields and "supplier_id" not in fields:
            data["supplier_id"] = fields["supplier"]
        for k, v in fields.items():
            if k in allowed and v is not None:
                if k == "supplier":
                    data["supplier_id"] = v
                else:
                    data[k] = v

        # Tạo đối tượng mới cùng kiểu để kiểm tra validation
        prod_cls = type(product)
        # Giữ nguyên số lượng hiện tại
        data["quantity"] = product.quantity
        candidate = prod_cls(**data)
        if not candidate.is_valid():
            raise ValueError("Dữ liệu cập nhật sản phẩm không hợp lệ.")

        self._products[product_id] = candidate

    def delete_product(self, product_id: str, stock_service: Any = None) -> None:
        """Xóa sản phẩm khỏi kho hàng.

        Ràng buộc: Tồn kho phải bằng 0 (Q19) VÀ chưa từng phát sinh bất kỳ giao dịch kho nào (Q20).
        """
        product = self._products.get(product_id)
        if product is None:
            raise KeyError(f"Không tìm thấy sản phẩm có mã: {product_id}")

        # Ràng buộc Q19: Tồn kho phải bằng 0
        if product.quantity > 0:
            raise ValueError(
                f"Không thể xóa sản phẩm '{product_id}' khi tồn kho vẫn còn ({product.quantity} > 0). "
                "Vui lòng xuất hết tồn kho về 0 trước khi xóa."
            )

        # Ràng buộc Q20: Không có lịch sử giao dịch
        if stock_service is not None and hasattr(stock_service, "has_product_transactions"):
            if stock_service.has_product_transactions(product_id):
                raise ValueError(
                    f"Không thể xóa sản phẩm '{product_id}' vì đã phát sinh lịch sử giao dịch trong quá khứ. "
                    "Hệ thống yêu cầu bảo toàn dữ liệu lịch sử kế toán kho."
                )

        del self._products[product_id]

    def get_product_by_id(self, product_id: str) -> Product:
        """Tìm sản phẩm theo mã. Ném KeyError nếu không tìm thấy (Q18, không trả về None)."""
        product = self._products.get(product_id)
        if product is None:
            raise KeyError(f"Không tìm thấy sản phẩm có mã: {product_id}")
        return product

    def get_all_products(self) -> list[Product]:
        """Trả về danh sách bản sao tất cả sản phẩm."""
        return list(self._products.values())

    def replace_products(self, products: list[Product]) -> None:
        """Thay thế toàn bộ danh mục sản phẩm (phục vụ nạp dữ liệu từ Storage)."""
        new_dict: dict[str, Product] = {}
        for p in products:
            if isinstance(p, Product) and p.is_valid():
                new_dict[p.product_id] = p
        self._products = new_dict

    def search_product(self, keyword: str, by: str = "name") -> list[Product]:
        """Tìm kiếm sản phẩm theo id, name hoặc supplier (Q21: không phân biệt hoa/thường, giữ dấu tiếng Việt)."""
        by_clean = str(by).strip().lower()
        key_clean = str(keyword).strip().casefold()
        if not key_clean:
            return self.get_all_products()

        field_map = {
            "id": "product_id",
            "product_id": "product_id",
            "name": "name",
            "supplier": "supplier_id",
            "supplier_id": "supplier_id",
        }
        attr_name = field_map.get(by_clean)
        if attr_name is None:
            raise ValueError("Tiêu chí tìm kiếm phải là 'id', 'name' hoặc 'supplier'.")

        result: list[Product] = []
        for p in self._products.values():
            val = str(getattr(p, attr_name, "")).casefold()
            if key_clean in val:
                result.append(p)
        return result

    def sort_products(self, by: str = "price", reverse: bool = False) -> list[Product]:
        """Sắp xếp danh sách sản phẩm theo giá hoặc số lượng, hỗ trợ tăng/giảm dần (Q22)."""
        by_clean = str(by).strip().lower()
        if by_clean not in {"price", "quantity"}:
            raise ValueError("Chỉ hỗ trợ sắp xếp theo 'price' hoặc 'quantity'.")

        return sorted(self._products.values(), key=lambda p: getattr(p, by_clean), reverse=reverse)
