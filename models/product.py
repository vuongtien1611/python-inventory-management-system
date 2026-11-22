"""Module định nghĩa các lớp mô hình sản phẩm trong kho hàng (Design Baseline v1.0)."""

from __future__ import annotations

from datetime import date, datetime
import math
from typing import Any


class Product:
    """Lớp cơ sở đại diện cho một sản phẩm trong kho."""

    def __init__(
        self,
        product_id: str,
        name: str,
        price: float,
        quantity: int = 0,
        supplier_id: str = "",
        supplier: str | None = None,
    ) -> None:
        self.product_id = product_id
        self.name = name
        self.price = price

        # Khởi tạo số lượng nội bộ qua validation (chỉ đọc từ bên ngoài, không có public setter)
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise TypeError("Số lượng phải là số nguyên.")
        if quantity < 0:
            raise ValueError("Số lượng không được âm.")
        self._quantity = quantity

        actual_supplier = supplier if (supplier is not None and not supplier_id) else supplier_id
        self.supplier_id = actual_supplier

    # ---------- PRODUCT ID ----------
    @property
    def product_id(self) -> str:
        return self._product_id

    @product_id.setter
    def product_id(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Mã sản phẩm phải là chuỗi.")
        value = value.strip()
        if not value:
            raise ValueError("Mã sản phẩm không được để trống.")
        self._product_id = value

    # ---------- NAME ----------
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Tên sản phẩm phải là chuỗi.")
        value = value.strip()
        if not value:
            raise ValueError("Tên sản phẩm không được để trống.")
        self._name = value

    # ---------- PRICE ----------
    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Giá sản phẩm phải là số.")
        if not math.isfinite(value):
            raise ValueError("Giá sản phẩm phải là số hữu hạn.")
        if value < 0:
            raise ValueError("Giá sản phẩm không được âm.")
        self._price = float(value)

    # ---------- QUANTITY (READ-ONLY PROPERTY - Q08) ----------
    @property
    def quantity(self) -> int:
        """Số lượng tồn kho (chỉ đọc, cấm sửa trực tiếp qua setter)."""
        return self._quantity

    # ---------- SUPPLIER ID (Q13) ----------
    @property
    def supplier_id(self) -> str:
        return self._supplier_id

    @supplier_id.setter
    def supplier_id(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Mã nhà cung cấp phải là chuỗi.")
        self._supplier_id = value.strip()

    # Thuộc tính tương thích ngược cho các đoạn mã cũ dùng .supplier
    @property
    def supplier(self) -> str:
        return self._supplier_id

    @supplier.setter
    def supplier(self, value: str) -> None:
        self.supplier_id = value

    # ---------- STOCK MUTATION METHODS (CHỈ DÀNH CHO STOCKSERVICE - Q08) ----------
    def increase_stock(self, amount: int) -> None:
        """Tăng số lượng tồn kho thêm amount (amount nguyên dương, từ chối bool)."""
        if isinstance(amount, bool) or not isinstance(amount, int):
            raise TypeError("Số lượng tăng phải là số nguyên.")
        if amount <= 0:
            raise ValueError("Số lượng tăng phải là số nguyên dương (> 0).")
        self._quantity += amount

    def decrease_stock(self, amount: int) -> None:
        """Giảm số lượng tồn kho đi amount (amount nguyên dương, không vượt quá tồn hiện tại)."""
        if isinstance(amount, bool) or not isinstance(amount, int):
            raise TypeError("Số lượng giảm phải là số nguyên.")
        if amount <= 0:
            raise ValueError("Số lượng giảm phải là số nguyên dương (> 0).")
        if amount > self._quantity:
            raise ValueError(
                f"Số lượng giảm ({amount}) vượt quá tồn kho hiện tại ({self._quantity})."
            )
        self._quantity -= amount

    # ---------- VALIDATION ----------
    def is_valid(self) -> bool:
        """Kiểm tra tính hợp lệ dữ liệu của sản phẩm."""
        return (
            isinstance(getattr(self, "_product_id", None), str)
            and bool(self._product_id.strip())
            and isinstance(getattr(self, "_name", None), str)
            and bool(self._name.strip())
            and isinstance(getattr(self, "_price", None), float)
            and math.isfinite(self._price)
            and self._price >= 0
            and isinstance(getattr(self, "_quantity", None), int)
            and not isinstance(self._quantity, bool)
            and self._quantity >= 0
            and isinstance(getattr(self, "_supplier_id", None), str)
        )

    # ---------- INVENTORY VALUE (Q07, Q32) ----------
    def get_inventory_value(self) -> float:
        """Tính tổng giá trị tồn kho của sản phẩm (làm tròn 2 chữ số)."""
        return round(self.price * self.quantity, 2)

    # ---------- STRING REPRESENTATION ----------
    def __str__(self) -> str:
        return (
            f"Mã SP: {self.product_id} | "
            f"Tên: {self.name} | "
            f"Giá: {self.price:,.0f} đ | "
            f"Tồn kho: {self.quantity} | "
            f"NCC: {self.supplier_id or '(chưa gán)'}"
        )

    # ---------- CONVERT TO DICTIONARY (Q33) ----------
    def to_dict(self) -> dict[str, Any]:
        """Chuyển đối tượng thành dictionary để lưu JSON."""
        return {
            "type": "Product",
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "supplier_id": self.supplier_id,
            "supplier": self.supplier_id,  # Tương thích trường cũ
        }


class FoodProduct(Product):
    """Lớp sản phẩm thực phẩm có hạn sử dụng (kế thừa từ Product)."""

    def __init__(
        self,
        product_id: str,
        name: str,
        price: float,
        quantity: int = 0,
        supplier_id: str = "",
        expiry_date: str | date = "",
        supplier: str | None = None,
    ) -> None:
        super().__init__(product_id, name, price, quantity, supplier_id, supplier=supplier)
        self.expiry_date = expiry_date

    @property
    def expiry_date(self) -> date:
        return self._expiry_date

    @expiry_date.setter
    def expiry_date(self, value: str | date) -> None:
        if isinstance(value, date):
            self._expiry_date = value
            return
        if not isinstance(value, str):
            raise TypeError("Hạn sử dụng phải có dạng chuỗi YYYY-MM-DD hoặc datetime.date.")

        value = value.strip()
        if not value:
            raise ValueError("Ngày hết hạn không được để trống.")

        try:
            parsed = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Ngày hết hạn không hợp lệ. Hãy nhập theo dạng YYYY-MM-DD.")

        if parsed.isoformat() != value:
            raise ValueError("Ngày hết hạn phải có dạng YYYY-MM-DD.")
        self._expiry_date = parsed

    def is_expired(self, current_date: date | None = None) -> bool:
        """Trả về True nếu sản phẩm đã quá hạn tính đến current_date (mặc định hôm nay)."""
        ref_date = current_date if current_date is not None else date.today()
        return self.expiry_date < ref_date

    def days_until_expiry(self, current_date: date | None = None) -> int:
        """Số ngày còn lại đến hạn sử dụng tính từ current_date (mặc định hôm nay)."""
        ref_date = current_date if current_date is not None else date.today()
        return (self.expiry_date - ref_date).days

    def is_valid(self) -> bool:
        """Kiểm tra thông tin sản phẩm thực phẩm."""
        return super().is_valid() and isinstance(getattr(self, "_expiry_date", None), date)

    def __str__(self) -> str:
        expiry_str = self.expiry_date.isoformat()
        status = " (ĐÃ HẾT HẠN)" if self.is_expired() else ""
        return (
            f"{super().__str__()} | "
            f"HSD: {expiry_str}{status}"
        )

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["type"] = "FoodProduct"
        data["expiry_date"] = self.expiry_date.isoformat()
        return data


class ElectronicProduct(Product):
    """Lớp sản phẩm điện tử có thời gian bảo hành (kế thừa từ Product)."""

    def __init__(
        self,
        product_id: str,
        name: str,
        price: float,
        quantity: int = 0,
        supplier_id: str = "",
        warranty_months: int = 0,
        supplier: str | None = None,
    ) -> None:
        super().__init__(product_id, name, price, quantity, supplier_id, supplier=supplier)
        self.warranty_months = warranty_months

    @property
    def warranty_months(self) -> int:
        return self._warranty_months

    @warranty_months.setter
    def warranty_months(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("Thời gian bảo hành phải là số nguyên.")
        if value < 0:
            raise ValueError("Thời gian bảo hành không được âm.")
        self._warranty_months = value

    def is_valid(self) -> bool:
        """Kiểm tra thông tin sản phẩm điện tử."""
        return (
            super().is_valid()
            and isinstance(getattr(self, "_warranty_months", None), int)
            and not isinstance(self._warranty_months, bool)
            and self._warranty_months >= 0
        )

    def __str__(self) -> str:
        return (
            f"{super().__str__()} | "
            f"Bảo hành: {self.warranty_months} tháng"
        )

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["type"] = "ElectronicProduct"
        data["warranty_months"] = self.warranty_months
        return data
