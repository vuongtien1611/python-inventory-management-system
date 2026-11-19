"""CRUD, tìm kiếm và sắp xếp danh sách sản phẩm."""

from __future__ import annotations

from models.product import Product


class InventoryManager:
    def __init__(self, products: list[Product] | None = None) -> None:
        self._products: dict[str, Product] = {}
        for product in products or []:
            self.add_product(product)

    def add_product(self, product: Product) -> None:
        if not isinstance(product, Product):
            raise TypeError("Thêm phải là đối tượng Product")
        if product.product_id in self._products:
            raise ValueError(f"Mã sản phẩm đã tồn tại: {product.product_id}")
        if not product.is_valid():
            raise ValueError("Sản phẩm không hợp lệ")
        self._products[product.product_id] = product

    def update_product(self, product_id: str, **fields: object) -> None:
        product = self._products.get(product_id)
        if product is None:
            raise KeyError(f"Không tìm thấy sản phẩm: {product_id}")
        allowed = {"name", "price", "quantity", "supplier"}
        unknown = fields.keys() - allowed
        if unknown:
            raise ValueError(f"Trường không được hỗ trợ: {', '.join(sorted(unknown))}")
        values = product.to_dict()
        values.pop("type", None)
        values.update(fields)
        candidate = type(product)(**values)
        if not candidate.is_valid():
            raise ValueError("Sản phẩm cập nhật không hợp lệ")
        self._products[product_id] = candidate

    def delete_product(self, product_id: str) -> None:
        product = self._products.get(product_id)
        if product is None:
            raise KeyError(f"Không tìm thấy sản phẩm: {product_id}")
        if product.quantity > 0:
            raise ValueError("Không thể xóa sản phẩm còn tồn kho")
        del self._products[product_id]

    def get_product_by_id(self, product_id: str) -> Product | None:
        return self._products.get(product_id)

    def get_all_products(self) -> list[Product]:
        return list(self._products.values())

    def replace_products(self, products: list[Product]) -> None:
        replacement = InventoryManager(products)
        self._products = replacement._products

    def search_product(self, keyword: str, by: str = "name") -> list[Product]:
        fields = {"id": "product_id", "name": "name", "supplier": "supplier"}
        field = fields.get(by)
        if field is None:
            raise ValueError("Tìm kiếm theo id, name hoặc supplier")
        needle = keyword.strip().casefold()
        return [p for p in self._products.values() if needle in str(getattr(p, field)).casefold()]

    def sort_products(self, by: str = "price", reverse: bool = False) -> list[Product]:
        if by not in {"price", "quantity"}:
            raise ValueError("Chỉ hỗ trợ sắp xếp theo price hoặc quantity")
        return sorted(self._products.values(), key=lambda p: getattr(p, by), reverse=reverse)
