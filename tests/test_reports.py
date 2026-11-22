"""Unit tests for inventory value, low-stock, expiry, warranty reports, and suppliers."""

import unittest
from datetime import date

from models.product import ElectronicProduct, FoodProduct, Product
from models.supplier import Supplier
from services.inventory_manager import InventoryManager
from services.report_service import ReportService


class TestReportService(unittest.TestCase):
    def setUp(self):
        self.products = [
            Product("P1", "Pen", 10, 2, "Office"),
            FoodProduct("F1", "Milk", 30, 4, "Dairy", "2026-11-20"),
            FoodProduct("F2", "Yogurt", 20, 1, "Dairy", "2026-11-10"),
            ElectronicProduct("E1", "Monitor", 200, 3, "Tech", 24),
        ]
        self.manager = InventoryManager(self.products)
        self.service = ReportService(self.manager, today=date(2026, 11, 19))

    def test_total_inventory_value(self):
        self.assertEqual(self.service.get_total_inventory_value(), 760)

    def test_low_stock_default_and_threshold(self):
        self.assertEqual({p.product_id for p in self.service.get_low_stock_products()}, {"P1", "F1", "F2", "E1"})
        self.assertEqual({p.product_id for p in self.service.get_low_stock_products(1)}, {"F2"})

    def test_low_stock_rejects_negative_threshold(self):
        with self.assertRaises(ValueError):
            self.service.get_low_stock_products(-1)

    def test_expiring_food_includes_expired_and_upcoming(self):
        self.assertEqual({p.product_id for p in self.service.get_expiring_food_products(7)}, {"F1", "F2"})

    def test_expiry_status_marks_past_date_expired(self):
        statuses = {item["product_id"]: item["status"] for item in self.service.check_food_expiry_status()}
        self.assertEqual(statuses, {"F1": "valid", "F2": "expired"})

    def test_expiry_status_can_filter_by_id(self):
        items = self.service.check_food_expiry_status("F1")
        self.assertEqual([item["product_id"] for item in items], ["F1"])

    def test_expiring_rejects_negative_days(self):
        with self.assertRaises(ValueError):
            self.service.get_expiring_food_products(-1)

    def test_invalid_expiry_format_is_reported(self):
        inventory = InventoryManager([FoodProduct("F3", "Bad date", 1, 1, "Dairy", "20/11/2026")])
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            ReportService(inventory, today=date(2026, 11, 19)).check_food_expiry_status()

    def test_warranty_summary_and_filter(self):
        self.assertEqual(self.service.get_warranty_summary()[0]["warranty_months"], 24)
        self.assertEqual(self.service.get_warranty_summary("P1"), [])

    def test_supplier_crud(self):
        s1 = Supplier("SUP1", "Vinamilk", "0901234567", "HN", "vina@milk.vn")
        self.service.add_supplier(s1)
        self.assertEqual(self.service.get_supplier_by_id("SUP1"), s1)
        self.assertEqual(len(self.service.get_all_suppliers()), 1)

        # Duplicate ID
        with self.assertRaises(ValueError):
            self.service.add_supplier(s1)

        # Update
        self.service.update_supplier("SUP1", phone="0987654321")
        self.assertEqual(self.service.get_supplier_by_id("SUP1").phone, "0987654321")

        # Delete non-linked
        self.service.delete_supplier("SUP1")
        self.assertIsNone(self.service.get_supplier_by_id("SUP1"))

    def test_supplier_delete_prevented_if_linked(self):
        s2 = Supplier("Office", "Office Supplies Co", "0912345678", "HCM")
        self.service.add_supplier(s2)
        # P1 has supplier="Office"
        with self.assertRaises(ValueError):
            self.service.delete_supplier("Office")


if __name__ == "__main__":
    unittest.main()
