"""Module định nghĩa mô hình Nhà cung cấp (Supplier) – Design Baseline v1.0."""

from __future__ import annotations

import re
from typing import Any


class Supplier:
    """Lớp đại diện cho một nhà cung cấp sản phẩm."""

    def __init__(
        self,
        supplier_id: str,
        name: str,
        phone: str = "",
        address: str = "",
        email: str = "",
    ) -> None:
        self.supplier_id = supplier_id
        self.name = name
        self.phone = phone
        self.address = address
        self.email = email

    # ---------- SUPPLIER ID ----------
    @property
    def supplier_id(self) -> str:
        return self._supplier_id

    @supplier_id.setter
    def supplier_id(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Mã nhà cung cấp phải là chuỗi (str).")
        value = value.strip()
        if not value:
            raise ValueError("Mã nhà cung cấp không được để trống.")
        self._supplier_id = value

    # ---------- NAME ----------
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Tên nhà cung cấp phải là chuỗi (str).")
        value = value.strip()
        if not value:
            raise ValueError("Tên nhà cung cấp không được để trống.")
        self._name = value

    # ---------- PHONE ----------
    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Số điện thoại phải là chuỗi (str).")
        value = value.strip()
        if value:
            # Cho phép: chữ số, dấu +, -, khoảng trắng, dấu chấm
            if not re.fullmatch(r"[0-9+\-.\s]+", value):
                raise ValueError(
                    f"Số điện thoại '{value}' chứa ký tự không hợp lệ. "
                    "Chỉ chấp nhận chữ số, dấu +, -, dấu chấm và khoảng trắng."
                )
            digits = re.sub(r"\D", "", value)
            if len(digits) < 7:
                raise ValueError(f"Số điện thoại '{value}' phải có ít nhất 7 chữ số.")
        self._phone = value

    # ---------- ADDRESS ----------
    @property
    def address(self) -> str:
        return self._address

    @address.setter
    def address(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Địa chỉ phải là chuỗi (str).")
        self._address = value.strip()

    # ---------- EMAIL ----------
    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Email phải là chuỗi (str).")
        value = value.strip()
        if value:
            pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
            if not re.fullmatch(pattern, value):
                raise ValueError(
                    f"Email '{value}' không đúng định dạng (ví dụ: abc@gmail.com)."
                )
        self._email = value

    # ---------- BUSINESS & SERIALIZATION METHODS ----------
    def is_valid(self) -> bool:
        """Kiểm tra dữ liệu nhà cung cấp có hợp lệ không."""
        try:
            if not getattr(self, "_supplier_id", None) or not self._supplier_id.strip():
                return False
            if not getattr(self, "_name", None) or not self._name.strip():
                return False
            if self._phone:
                digits = re.sub(r"\D", "", self._phone)
                if len(digits) < 7:
                    return False
            if self._email:
                pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
                if not re.fullmatch(pattern, self._email):
                    return False
            return True
        except (AttributeError, TypeError):
            return False

    def to_dict(self) -> dict[str, Any]:
        """Xuất dictionary để lưu trữ JSON (Q33)."""
        return {
            "supplier_id": self.supplier_id,
            "name": self.name,
            "phone": self.phone,
            "address": self.address,
            "email": self.email,
        }

    def __str__(self) -> str:
        email_str = self.email if self.email else "(không có)"
        address_str = self.address if self.address else "(không có)"
        phone_str = self.phone if self.phone else "(không có)"
        return (
            f"[Mã NCC: {self.supplier_id}] {self.name} | "
            f"ĐT: {phone_str} | "
            f"Địa chỉ: {address_str} | "
            f"Email: {email_str}"
        )

    def __repr__(self) -> str:
        return (
            f"Supplier(supplier_id={self.supplier_id!r}, name={self.name!r}, "
            f"phone={self.phone!r}, address={self.address!r}, email={self.email!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Supplier):
            return NotImplemented
        return self.supplier_id == other.supplier_id
