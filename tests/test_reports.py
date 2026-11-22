"""Unit tests for inventory value, low-stock, expiry, and warranty reports."""

import unittest
from datetime import date

from models.product import ElectronicProduct, FoodProduct, Product
from services.inventory_manager import InventoryManager
from services.report_service import ReportService


class TestReportService(unittest.TestCase):
    def setUp(self):
        self.products = [
            Product("P1", "Pen", 10, 2, "Office"),
            FoodProduct("F1", "Milk", 30, 4, "Dairy", "2026-11-20"),
            FoodProduct("F2", "Yogurt", 20, 1, "Dairy", "2026-11-10"),
            FoodProduct("F3", "Rice", 50, 10, "Grain", "2026-12-30"),
            ElectronicProduct("E1", "Monitor", 200, 3, "Tech", 24),
        ]
        self.service = ReportService(InventoryManager(self.products), today=date(2026, 11, 19))

    def test_total_inventory_value_returns_dict_with_expiry_warning(self):
        result = self.service.get_total_inventory_value()
        self.assertIsInstance(result, dict)
        # Total = 10*2 + 30*4 + 20*1 + 50*10 + 200*3 = 20 + 120 + 20 + 500 + 600 = 1260
        self.assertEqual(result["total_value"], 1260.0)
        self.assertTrue(result["has_expired_food"])
        self.assertEqual(result["expired_food_count"], 1)
        self.assertEqual(result["expired_food_value"], 20.0)

    def test_low_stock_default_and_threshold(self):
        self.assertEqual({p.product_id for p in self.service.get_low_stock_products(2)}, {"P1", "F2"})
        self.assertEqual({p.product_id for p in self.service.get_low_stock_products(1)}, {"F2"})

    def test_low_stock_rejects_negative_threshold(self):
        with self.assertRaises(ValueError):
            self.service.get_low_stock_products(-1)
        with self.assertRaises(TypeError):
            self.service.get_low_stock_products("invalid")

    def test_expiring_food_includes_expired_and_upcoming(self):
        # F1 is 1 day away, F2 is expired (-9 days), F3 is 41 days away
        expiring = self.service.get_expiring_food_products(7)
        self.assertEqual({p.product_id for p in expiring}, {"F1", "F2"})

    def test_expiry_status_three_tier_classification(self):
        # F1 (1 day left) -> Gần hết hạn, F2 (-9 days) -> Đã hết hạn, F3 (41 days) -> Còn hạn
        items = self.service.check_food_expiry_status()
        statuses = {item["product_id"]: item["status"] for item in items}
        self.assertEqual(statuses, {
            "F1": "Gần hết hạn",
            "F2": "Đã hết hạn",
            "F3": "Còn hạn",
        })
        status_codes = {item["product_id"]: item["status_code"] for item in items}
        self.assertEqual(status_codes, {
            "F1": "near_expiry",
            "F2": "expired",
            "F3": "valid",
        })

    def test_expiry_status_can_filter_by_id(self):
        items = self.service.check_food_expiry_status("F1")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["product_id"], "F1")

    def test_expiring_rejects_negative_days(self):
        with self.assertRaises(ValueError):
            self.service.get_expiring_food_products(-1)
        with self.assertRaises(TypeError):
            self.service.get_expiring_food_products("invalid")

    def test_invalid_expiry_format_rejected_at_model_creation(self):
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            FoodProduct("F_BAD", "Bad date", 1, 1, "Dairy", "20/11/2026")

    def test_warranty_summary_and_filter(self):
        summary = self.service.get_warranty_summary()
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["product_id"], "E1")
        self.assertEqual(summary[0]["warranty_months"], 24)
        self.assertEqual(summary[0]["warranty_years"], 2.0)
        self.assertEqual(summary[0]["warranty_tier"], "Bảo hành mở rộng (2 năm)")

        # Filter by product with no warranty
        self.assertEqual(self.service.get_warranty_summary("P1"), [])


if __name__ == "__main__":
    unittest.main()
