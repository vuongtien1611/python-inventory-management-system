"""Module thống kê, báo cáo kho hàng và cảnh báo tồn kho – Design Baseline v1.0."""

from __future__ import annotations

from datetime import date
from typing import Any
from models.product import ElectronicProduct, FoodProduct, Product


class ReportService:
    """Dịch vụ thống kê, báo cáo và cảnh báo kho hàng (thuần túy truy vấn - Q16)."""

    def __init__(self, inventory_manager: Any = None, today: date | None = None) -> None:
        if inventory_manager is None:
            raise TypeError("inventory_manager không được là None.")
        self._inventory_manager = inventory_manager
        self._today = today

    def get_total_inventory_value(self, current_date: date | None = None) -> dict[str, Any]:
        """Tính tổng giá trị hàng tồn kho và cảnh báo giá trị thực phẩm hết hạn (Q07, Q32)."""
        ref_date = current_date or self._today or date.today()
        all_products: list[Product] = self._inventory_manager.get_all_products()
        total_value = 0.0
        expired_food_count = 0
        expired_food_value = 0.0

        for p in all_products:
            val = p.get_inventory_value()
            total_value += val
            if isinstance(p, FoodProduct) and p.is_expired(ref_date):
                expired_food_count += 1
                expired_food_value += val

        return {
            "total_value": round(total_value, 2),
            "has_expired_food": expired_food_count > 0,
            "expired_food_count": expired_food_count,
            "expired_food_value": round(expired_food_value, 2),
        }

    def get_low_stock_products(self, threshold: int = 5) -> list[Product]:
        """Lọc các sản phẩm có số lượng tồn kho <= threshold (ngưỡng mặc định là 5 - Q29)."""
        if isinstance(threshold, bool) or not isinstance(threshold, int):
            raise TypeError("Ngưỡng tồn kho phải là số nguyên.")
        if threshold < 0:
            raise ValueError(f"Ngưỡng tồn kho không được âm ({threshold}).")

        all_products: list[Product] = self._inventory_manager.get_all_products()
        return [p for p in all_products if p.quantity <= threshold]

    def get_expiring_food_products(self, days: int = 7, current_date: date | None = None) -> list[FoodProduct]:
        """Lấy danh sách thực phẩm sắp hết hạn trong vòng `days` ngày tới hoặc đã hết hạn (Q30)."""
        if isinstance(days, bool) or not isinstance(days, int):
            raise TypeError("Số ngày phải là số nguyên.")
        if days < 0:
            raise ValueError(f"Số ngày không được âm ({days}).")

        ref_date = current_date or self._today or date.today()
        all_products: list[Product] = self._inventory_manager.get_all_products()
        result: list[FoodProduct] = []
        for p in all_products:
            if isinstance(p, FoodProduct):
                if p.days_until_expiry(ref_date) <= days:
                    result.append(p)
        return result

    def check_food_expiry_status(
        self, product_id: str | None = None, current_date: date | None = None
    ) -> list[dict[str, Any]]:
        """Phân loại chi tiết trạng thái hạn sử dụng thực phẩm thành 3 nhóm (Q31):

        1. "Đã hết hạn" (số ngày còn lại < 0)
        2. "Gần hết hạn" (0 <= số ngày còn lại <= 7)
        3. "Còn hạn" (số ngày còn lại > 7)
        """
        ref_date = current_date or self._today or date.today()
        all_products: list[Product] = self._inventory_manager.get_all_products()
        result: list[dict[str, Any]] = []

        for p in all_products:
            if not isinstance(p, FoodProduct):
                continue
            if product_id is not None and p.product_id != str(product_id).strip():
                continue

            days_left = p.days_until_expiry(ref_date)
            if days_left < 0:
                status = "Đã hết hạn"
                status_code = "expired"
            elif days_left <= 7:
                status = "Gần hết hạn"
                status_code = "near_expiry"
            else:
                status = "Còn hạn"
                status_code = "valid"

            result.append({
                "product_id": p.product_id,
                "name": p.name,
                "expiry_date": p.expiry_date.isoformat(),
                "days_remaining": days_left,
                "status": status,
                "status_code": status_code,
                "quantity": p.quantity,
            })
        return result

    def get_warranty_summary(
        self, product_id: str | None = None
    ) -> list[dict[str, Any]]:
        """Thống kê thông tin bảo hành danh nghĩa theo tháng của thiết bị điện tử (Q11)."""
        all_products: list[Product] = self._inventory_manager.get_all_products()
        result: list[dict[str, Any]] = []

        for p in all_products:
            if not isinstance(p, ElectronicProduct):
                continue
            if product_id is not None and p.product_id != str(product_id).strip():
                continue

            months = p.warranty_months
            if months <= 0:
                tier = "Không có bảo hành"
            elif months <= 6:
                tier = "Bảo hành ngắn hạn (≤ 6 tháng)"
            elif months <= 12:
                tier = "Bảo hành tiêu chuẩn (1 năm)"
            elif months <= 24:
                tier = "Bảo hành mở rộng (2 năm)"
            else:
                tier = f"Bảo hành dài hạn ({months} tháng)"

            result.append({
                "product_id": p.product_id,
                "name": p.name,
                "warranty_months": months,
                "warranty_years": round(months / 12, 1),
                "warranty_tier": tier,
                "quantity": p.quantity,
            })
        return result
