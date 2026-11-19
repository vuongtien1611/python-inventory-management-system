"""Thống kê tồn kho, thực phẩm và bảo hành thiết bị."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from models.product import ElectronicProduct, FoodProduct
from services.inventory_manager import InventoryManager


class ReportService:
    def __init__(self, inventory_manager: InventoryManager, today: date | None = None) -> None:
        self.inventory_manager = inventory_manager
        self._today = today or date.today()

    def get_total_inventory_value(self) -> float:
        return sum(product.get_inventory_value() for product in self.inventory_manager.get_all_products())

    def get_low_stock_products(self, threshold: int = 5):
        if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 0:
            raise ValueError("Ngưỡng tồn kho phải là số nguyên không âm")
        return [p for p in self.inventory_manager.get_all_products() if p.quantity <= threshold]

    def get_expiring_food_products(self, days: int = 7) -> list[FoodProduct]:
        if isinstance(days, bool) or not isinstance(days, int) or days < 0:
            raise ValueError("Số ngày phải là số nguyên không âm")
        deadline = self._today + timedelta(days=days)
        result = []
        for product in self.inventory_manager.get_all_products():
            if isinstance(product, FoodProduct) and self._expiry_date(product) <= deadline:
                result.append(product)
        return result

    def check_food_expiry_status(self, product_id: str | None = None) -> list[dict[str, Any]]:
        products = self.inventory_manager.get_all_products()
        result = []
        for product in products:
            if not isinstance(product, FoodProduct) or (product_id and product.product_id != product_id):
                continue
            expiry = self._expiry_date(product)
            result.append({
                "product_id": product.product_id,
                "name": product.name,
                "expiry_date": expiry.isoformat(),
                "status": "expired" if expiry < self._today else "valid",
                "days_remaining": (expiry - self._today).days,
            })
        return result

    def get_warranty_summary(self, product_id: str | None = None) -> list[dict[str, Any]]:
        result = []
        for product in self.inventory_manager.get_all_products():
            if isinstance(product, ElectronicProduct) and (product_id is None or product.product_id == product_id):
                result.append({
                    "product_id": product.product_id,
                    "name": product.name,
                    "warranty_months": product.warranty_months,
                })
        return result

    @staticmethod
    def _expiry_date(product: FoodProduct) -> date:
        value = product.expiry_date
        if isinstance(value, date):
            return value
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Ngày hết hạn của {product.product_id} phải theo YYYY-MM-DD") from exc
