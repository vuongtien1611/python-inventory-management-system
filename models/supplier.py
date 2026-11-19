"""Module định nghĩa mô hình Nhà cung cấp (Supplier).

Người phụ trách: Thành viên 5 - Minh (nhánh `feature/supplier-reports`).

Lớp triển khai:
- `Supplier`: Đại diện cho thông tin nhà cung cấp sản phẩm trong kho.
  Áp dụng đóng gói dữ liệu (`@property`), kiểm tra dữ liệu đầu vào
  và cung cấp phương thức `is_valid()`, `__str__()` theo chuẩn OOP.
"""

from __future__ import annotations

import re


class Supplier:
    """Lớp đại diện cho một nhà cung cấp sản phẩm.

    Attributes:
        supplier_id (str): Mã nhà cung cấp (không rỗng).
        name (str): Tên nhà cung cấp (không rỗng).
        phone (str): Số điện thoại (định dạng số cơ bản).
        address (str): Địa chỉ nhà cung cấp.
        email (str): Địa chỉ email (tùy chọn, kiểm tra định dạng nếu có).
    """

    def __init__(
        self,
        supplier_id: str,
        name: str,
        phone: str,
        address: str,
        email: str = "",
    ) -> None:
        """Khởi tạo đối tượng Supplier.

        Args:
            supplier_id: Mã nhà cung cấp (không rỗng sau `.strip()`).
            name: Tên nhà cung cấp (không rỗng sau `.strip()`).
            phone: Số điện thoại liên hệ (chỉ chứa chữ số, dấu ``+``,
                   dấu ``-``, khoảng trắng và dấu chấm; tối thiểu 7 ký tự số).
            address: Địa chỉ nhà cung cấp.
            email: Địa chỉ email (mặc định ``""``). Nếu cung cấp sẽ được
                   kiểm tra định dạng cơ bản ``...@...``

        Raises:
            TypeError: Nếu bất kỳ tham số nào không phải kiểu ``str``.
            ValueError: Nếu ``supplier_id``, ``name`` rỗng; ``phone`` sai
                        định dạng; hoặc ``email`` không hợp lệ khi được
                        cung cấp.
        """
        self.supplier_id = supplier_id
        self.name = name
        self.phone = phone
        self.address = address
        self.email = email

    # ------------------------------------------------------------------ #
    #  supplier_id
    # ------------------------------------------------------------------ #
    @property
    def supplier_id(self) -> str:
        """Mã nhà cung cấp."""
        return self._supplier_id

    @supplier_id.setter
    def supplier_id(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Mã nhà cung cấp phải là chuỗi (str).")
        value = value.strip()
        if not value:
            raise ValueError("Mã nhà cung cấp không được để trống.")
        self._supplier_id = value

    # ------------------------------------------------------------------ #
    #  name
    # ------------------------------------------------------------------ #
    @property
    def name(self) -> str:
        """Tên nhà cung cấp."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Tên nhà cung cấp phải là chuỗi (str).")
        value = value.strip()
        if not value:
            raise ValueError("Tên nhà cung cấp không được để trống.")
        self._name = value

    # ------------------------------------------------------------------ #
    #  phone
    # ------------------------------------------------------------------ #
    @property
    def phone(self) -> str:
        """Số điện thoại liên hệ."""
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Số điện thoại phải là chuỗi (str).")
        value = value.strip()
        if not value:
            raise ValueError("Số điện thoại không được để trống.")
        # Cho phép: chữ số, dấu +, -, khoảng trắng, dấu chấm
        if not re.fullmatch(r"[0-9+\-.\s]+", value):
            raise ValueError(
                f"Số điện thoại '{value}' chứa ký tự không hợp lệ. "
                "Chỉ chấp nhận chữ số, dấu +, -, dấu chấm và khoảng trắng."
            )
        # Kiểm tra có ít nhất 7 chữ số
        digits = re.sub(r"\D", "", value)
        if len(digits) < 7:
            raise ValueError(
                f"Số điện thoại '{value}' phải có ít nhất 7 chữ số."
            )
        self._phone = value

    # ------------------------------------------------------------------ #
    #  address
    # ------------------------------------------------------------------ #
    @property
    def address(self) -> str:
        """Địa chỉ nhà cung cấp."""
        return self._address

    @address.setter
    def address(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Địa chỉ phải là chuỗi (str).")
        self._address = value.strip()

    # ------------------------------------------------------------------ #
    #  email
    # ------------------------------------------------------------------ #
    @property
    def email(self) -> str:
        """Địa chỉ email liên hệ (có thể rỗng)."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Email phải là chuỗi (str).")
        value = value.strip()
        if value:
            # Kiểm tra định dạng email cơ bản: xxx@xxx.xxx
            pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
            if not re.fullmatch(pattern, value):
                raise ValueError(
                    f"Email '{value}' không đúng định dạng (ví dụ: abc@gmail.com)."
                )
        self._email = value

    # ------------------------------------------------------------------ #
    #  Phương thức nghiệp vụ
    # ------------------------------------------------------------------ #
    def is_valid(self) -> bool:
        """Kiểm tra dữ liệu nhà cung cấp có hợp lệ không.

        Returns:
            ``True`` nếu ``supplier_id``, ``name``, ``phone`` đều hợp lệ
            (đã vượt qua validation trong setter); ``False`` trong trường
            hợp dữ liệu bị gán trực tiếp vào thuộc tính private và không
            thỏa ràng buộc.
        """
        try:
            if not self._supplier_id or not self._supplier_id.strip():
                return False
            if not self._name or not self._name.strip():
                return False
            if not self._phone or not self._phone.strip():
                return False
            digits = re.sub(r"\D", "", self._phone)
            if len(digits) < 7:
                return False
            if self._email:
                pattern = (
                    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
                )
                if not re.fullmatch(pattern, self._email):
                    return False
            return True
        except (AttributeError, TypeError):
            return False

    def __str__(self) -> str:
        """Trả về chuỗi mô tả nhà cung cấp hiển thị trên Console.

        Returns:
            Chuỗi chứa thông tin chi tiết nhà cung cấp.
        """
        email_display = self._email if self._email else "(không có)"
        address_display = self._address if self._address else "(không có)"
        return (
            f"[NCC: {self._supplier_id}] {self._name} | "
            f"ĐT: {self._phone} | "
            f"Địa chỉ: {address_display} | "
            f"Email: {email_display}"
        )

    def __repr__(self) -> str:
        """Biểu diễn chính thức của đối tượng Supplier."""
        return (
            f"Supplier(supplier_id={self._supplier_id!r}, "
            f"name={self._name!r}, phone={self._phone!r}, "
            f"address={self._address!r}, email={self._email!r})"
        )

    def __eq__(self, other: object) -> bool:
        """So sánh hai nhà cung cấp dựa trên ``supplier_id``."""
        if not isinstance(other, Supplier):
            return NotImplemented
        return self._supplier_id == other._supplier_id
