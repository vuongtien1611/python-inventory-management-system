"""Module định nghĩa các lớp mô hình sản phẩm trong kho hàng."""

from datetime import date, datetime
import math


def _is_iso_date(value: object) -> bool:
    if not isinstance(value, str):
        return False

    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


class Product:
    """Lớp cơ sở đại diện cho một sản phẩm trong kho."""

    def __init__(
        self,
        product_id: str,
        name: str,
        price: float,
        quantity: int = 0,
        supplier: str = ""
    ) -> None:
        # Gán thông qua setter để kiểm tra dữ liệu ngay khi khởi tạo
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.supplier = supplier

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

    # ---------- QUANTITY ----------
    @property
    def quantity(self) -> int:
        return self._quantity

    @quantity.setter
    def quantity(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("Số lượng phải là số nguyên.")

        if value < 0:
            raise ValueError("Số lượng không được âm.")

        self._quantity = value

    # ---------- SUPPLIER ----------
    @property
    def supplier(self) -> str:
        return self._supplier

    @supplier.setter
    def supplier(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Nhà cung cấp phải là chuỗi.")

        self._supplier = value.strip()

    # ---------- VALIDATION ----------
    def is_valid(self) -> bool:
        """Kiểm tra dữ liệu hiện tại của sản phẩm."""
        return (
            isinstance(self._product_id, str)
            and bool(self._product_id.strip())
            and isinstance(self._name, str)
            and bool(self._name.strip())
            and isinstance(self._price, float)
            and math.isfinite(self._price)
            and self._price >= 0
            and isinstance(self._quantity, int)
            and not isinstance(self._quantity, bool)
            and self._quantity >= 0
            and isinstance(self._supplier, str)
        )

    # ---------- INVENTORY VALUE ----------
    def get_inventory_value(self) -> float:
        """Tính tổng giá trị tồn kho của sản phẩm."""
        return self.price * self.quantity

    # ---------- STRING ----------
    def __str__(self) -> str:
        return (
            f"{self.product_id}: {self.name} "
            f"(price={self.price}, qty={self.quantity}, supplier={self.supplier})"
        )

    # ---------- CONVERT TO DICTIONARY ----------
    def to_dict(self) -> dict:
        """Chuyển đối tượng thành dictionary để lưu JSON."""
        return {
            "type": "Product",
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "supplier": self.supplier
        }


class FoodProduct(Product):
    """Lớp sản phẩm thực phẩm, kế thừa từ Product."""

    def __init__(
        self,
        product_id: str,
        name: str,
        price: float,
        quantity: int,
        supplier: str,
        expiry_date: str
    ) -> None:
        if _is_iso_date(supplier) and not _is_iso_date(expiry_date):
            supplier, expiry_date = expiry_date, supplier

        super().__init__(product_id, name, price, quantity, supplier)
        self.expiry_date = expiry_date

    @property
    def expiry_date(self) -> str:
        return self._expiry_date

    @expiry_date.setter
    def expiry_date(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Hạn sử dụng phải có dạng chuỗi YYYY-MM-DD.")

        try:
            parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(
                "Ngày hết hạn không hợp lệ. Hãy nhập theo dạng YYYY-MM-DD."
            )

        # Đảm bảo ngày được nhập đúng định dạng ISO
        if parsed_date.isoformat() != value:
            raise ValueError("Ngày hết hạn phải có dạng YYYY-MM-DD.")

        self._expiry_date = value

    def is_expired(self) -> bool:
        """Trả về True nếu sản phẩm đã quá hạn."""
        expiry = date.fromisoformat(self.expiry_date)
        return expiry < date.today()

    def is_valid(self) -> bool:
        """Kiểm tra thông tin sản phẩm thực phẩm."""
        if not super().is_valid():
            return False

        try:
            datetime.strptime(self.expiry_date, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def __str__(self) -> str:
        return (
            f"{super().__str__()} | "
            f"Hạn sử dụng: {self.expiry_date}"
        )

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["type"] = "FoodProduct"
        data["expiry_date"] = self.expiry_date
        return data


class ElectronicProduct(Product):
    """Lớp sản phẩm điện tử, kế thừa từ Product."""

    def __init__(
        self,
        product_id: str,
        name: str,
        price: float,
        quantity: int,
        supplier: str | int,
        warranty_months: int | str
    ) -> None:
        if (
            isinstance(supplier, int)
            and not isinstance(supplier, bool)
            and isinstance(warranty_months, str)
        ):
            supplier, warranty_months = warranty_months, supplier

        if not isinstance(supplier, str) or not isinstance(warranty_months, int):
            raise TypeError("Nhà cung cấp phải là chuỗi và thời gian bảo hành phải là số nguyên.")

        super().__init__(product_id, name, price, quantity, supplier)
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
            and isinstance(self.warranty_months, int)
            and not isinstance(self.warranty_months, bool)
            and self.warranty_months >= 0
        )

    def __str__(self) -> str:
        return (
            f"{super().__str__()} | "
            f"Bảo hành: {self.warranty_months} tháng"
        )

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["type"] = "ElectronicProduct"
        data["warranty_months"] = self.warranty_months
        return data