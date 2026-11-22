"""CRUD, tìm kiếm và sắp xếp danh sách sản phẩm trong kho.

Người phụ trách: Thành viên 3 - Sơn (nhánh feature/product-management).
Lớp: InventoryManager.
"""

from __future__ import annotations

from models.product import Product


class InventoryManager:
    """Quản lý danh mục sản phẩm trong kho: CRUD, tìm kiếm, sắp xếp."""

    def __init__(self, products: list[Product] | None = None) -> None:
        """Khởi tạo kho hàng với danh sách sản phẩm ban đầu (nếu có)."""
        self._products: dict[str, Product] = {}
        for product in products or []:
            self.add_product(product)

    def add_product(self, product: Product) -> None:
        """Thêm một sản phẩm mới vào kho.

        Thứ tự kiểm tra:
        1. Phải là instance của Product (hoặc lớp con).
        2. Mã sản phẩm phải hợp lệ và không có khoảng trắng thừa ở hai đầu.
        3. Sản phẩm phải thỏa mãn is_valid().
        4. Mã sản phẩm không được trùng với sản phẩm đã có.
        """
        if not isinstance(product, Product):
            raise TypeError("Chỉ được thêm đối tượng Product")
        if not isinstance(product.product_id, str) or not product.product_id.strip():
            raise ValueError("Mã sản phẩm không hợp lệ")
        if product.product_id != product.product_id.strip():
            raise ValueError("Mã sản phẩm không được có khoảng trắng thừa ở đầu hoặc cuối")
        if not product.is_valid():
            raise ValueError("Sản phẩm không hợp lệ")
        if product.product_id in self._products:
            raise ValueError(f"Mã sản phẩm đã tồn tại: {product.product_id}")
        self._products[product.product_id] = product

    def get_product_by_id(self, product_id: str) -> Product | None:
        """Tra cứu sản phẩm theo mã định danh (loại bỏ khoảng trắng thừa).

        Trả về chính đối tượng đang lưu trong kho, hoặc None nếu không tìm thấy.
        """
        if not isinstance(product_id, str):
            return None
        return self._products.get(product_id.strip())

    def update_product(self, product_id: str, /, **fields: object) -> None:
        """Cập nhật thông tin của một sản phẩm trong kho."""
        clean_id = product_id.strip() if isinstance(product_id, str) else str(product_id)
        product = self._products.get(clean_id)
        if product is None:
            raise KeyError(f"Không tìm thấy sản phẩm: {product_id}")
        if not fields:
            raise ValueError("Không có trường nào để cập nhật")
        if "product_id" in fields:
            raise ValueError("Không được đổi mã sản phẩm")

        values = product.to_dict()
        values.pop("type", None)
        values.pop("product_id", None)
        allowed = set(values.keys())
        unknown = fields.keys() - allowed
        if unknown:
            raise ValueError(f"Trường không được hỗ trợ: {', '.join(sorted(unknown))}")

        values["product_id"] = product.product_id
        values.update(fields)
        candidate = type(product)(**values)
        if not candidate.is_valid():
            raise ValueError("Sản phẩm cập nhật không hợp lệ")
        self._products[clean_id] = candidate

    def delete_product(self, product_id: str) -> None:
        """Xóa sản phẩm khỏi kho (chỉ xóa khi tồn kho quantity == 0)."""
        clean_id = product_id.strip() if isinstance(product_id, str) else str(product_id)
        product = self._products.get(clean_id)
        if product is None:
            raise KeyError(f"Không tìm thấy sản phẩm: {product_id}")
        if product.quantity > 0:
            raise ValueError("Không thể xóa sản phẩm còn tồn kho")
        del self._products[clean_id]

    def get_all_products(self) -> list[Product]:
        """Trả về bản sao danh sách tất cả sản phẩm trong kho."""
        return list(self._products.values())

    def replace_products(self, products: list[Product]) -> None:
        """Thay thế toàn bộ sản phẩm trong kho bằng danh sách mới an toàn."""
        temp_manager = InventoryManager()
        for p in products:
            temp_manager.add_product(p)
        self._products = temp_manager._products

    def search_product(self, keyword: str, by: str = "name") -> list[Product]:
        """Tìm kiếm sản phẩm theo id (chính xác), name hoặc supplier (gần đúng)."""
        if by not in {"id", "name", "supplier"}:
            raise ValueError("Tìm kiếm theo id, name hoặc supplier")
        if not keyword or not keyword.strip():
            raise ValueError("Từ khóa tìm kiếm không được để trống")

        needle = keyword.strip().casefold()
        if by == "id":
            return [p for p in self._products.values() if p.product_id.strip().casefold() == needle]
        return [p for p in self._products.values() if needle in str(getattr(p, by)).casefold()]

    def sort_products(self, by: str = "price", reverse: bool = False) -> list[Product]:
        """Sắp xếp sản phẩm theo price hoặc quantity."""
        if by not in {"price", "quantity"}:
            raise ValueError("Chỉ hỗ trợ sắp xếp theo price hoặc quantity")
        return sorted(self._products.values(), key=lambda p: getattr(p, by), reverse=reverse)
