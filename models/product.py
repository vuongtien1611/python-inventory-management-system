"""Model definitions for products in the inventory system.

Implemented to satisfy integration tests and unit tests.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Product:
    """Base product class.

    Attributes:
        product_id: Unique identifier of the product.
        name: Human‑readable name.
        price: Price per unit (int, in local currency).
        quantity: Current stock quantity.
        supplier: Supplier name.
    """

    product_id: str
    name: str
    price: int
    quantity: int = 0
    supplier: str = ""

    def __post_init__(self) -> None:
        # Basic validation – raise ValueError if data is invalid.
        if not self.product_id:
            raise ValueError("product_id must not be empty")
        if self.price < 0:
            raise ValueError("price must be non‑negative")
        if self.quantity < 0:
            raise ValueError("quantity must be non‑negative")

    # Provide a dict representation compatible with storage module.
    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["type"] = self.__class__.__name__
        return data

    # Human‑readable representation.
    def __str__(self) -> str:
        return f"{self.product_id}: {self.name} (price={self.price}, qty={self.quantity}, supplier={self.supplier})"

    # Example validation method (not used by tests but kept for completeness).
    def is_valid(self) -> bool:
        return bool(self.product_id) and self.price >= 0 and self.quantity >= 0

    # Inventory value (price * quantity).
    def get_inventory_value(self) -> int:
        return self.price * self.quantity

# Stub classes for future extensions – they inherit the same behaviour.
class FoodProduct(Product):
    def __init__(self, product_id: str, name: str, price: int, quantity: int, supplier: str, expiry_date: str):
        super().__init__(product_id, name, price, quantity, supplier)
        self.expiry_date = expiry_date

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["expiry_date"] = self.expiry_date
        return data

    def __str__(self) -> str:
        return super().__str__() + f", expiry={self.expiry_date}"


class ElectronicProduct(Product):
    def __init__(self, product_id: str, name: str, price: int, quantity: int, supplier: str, warranty_months: int):
        super().__init__(product_id, name, price, quantity, supplier)
        self.warranty_months = warranty_months

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["warranty_months"] = self.warranty_months
        return data

    def __str__(self) -> str:
        return super().__str__() + f", warranty={self.warranty_months} months"
