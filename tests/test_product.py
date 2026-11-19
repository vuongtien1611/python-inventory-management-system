"""Kiểm thử đơn vị cho các lớp mô hình sản phẩm và giao dịch kho.

Bảo đảm tính đóng gói (encapsulation), đa hình (polymorphism),
và xác thực dữ liệu theo Design Baseline v1.0 và 40 Quyết định Q01-Q40.
"""

import importlib
import unittest
from datetime import date, timedelta

from models.product import ElectronicProduct, FoodProduct, Product
from models.stock_transaction import StockTransaction


class TestProjectBootstrap(unittest.TestCase):
    """Đảm bảo các package và module bộ khung có thể import không lỗi."""

    def test_core_packages_importable(self) -> None:
        for module_name in (
            "models",
            "models.product",
            "models.supplier",
            "models.stock_transaction",
            "services",
            "services.inventory_manager",
            "services.stock_service",
            "services.report_service",
            "storage",
            "storage.storage",
            "cli",
            "cli.menu",
        ):
            module = importlib.import_module(module_name)
            self.assertIsNotNone(module)

    def test_cli_main_callable(self) -> None:
        from cli.menu import main
        self.assertTrue(callable(main))


class TestProductModels(unittest.TestCase):
    def test_product_rejects_empty_id(self):
        with self.assertRaises(ValueError):
            Product("", "Item", 1)

    def test_product_rejects_negative_price(self):
        with self.assertRaises(ValueError):
            Product("P1", "Item", -1)

    def test_product_rejects_negative_quantity(self):
        with self.assertRaises(ValueError):
            Product("P1", "Item", 1, -1)

    def test_product_rejects_boolean_quantity_in_init(self):
        with self.assertRaises(TypeError):
            Product("P1", "Item", 1, True)

    def test_quantity_is_read_only_no_setter(self):
        # Decision Q08: Không có public setter cho quantity
        p = Product("P1", "Item", 100, 5)
        self.assertEqual(p.quantity, 5)
        with self.assertRaises(AttributeError):
            p.quantity = 10

    def test_increase_stock_validation(self):
        p = Product("P1", "Item", 100, 5)
        p.increase_stock(3)
        self.assertEqual(p.quantity, 8)
        # Rejects 0 and negative
        with self.assertRaises(ValueError):
            p.increase_stock(0)
        with self.assertRaises(ValueError):
            p.increase_stock(-2)
        # Rejects bool and float
        with self.assertRaises(TypeError):
            p.increase_stock(True)
        with self.assertRaises(TypeError):
            p.increase_stock(2.5)

    def test_decrease_stock_validation(self):
        p = Product("P1", "Item", 100, 5)
        p.decrease_stock(3)
        self.assertEqual(p.quantity, 2)
        # Decrease to zero allowed
        p.decrease_stock(2)
        self.assertEqual(p.quantity, 0)
        # Rejects more than stock
        with self.assertRaises(ValueError):
            p.decrease_stock(1)
        # Rejects 0, negative, bool, float
        with self.assertRaises(ValueError):
            p.decrease_stock(0)
        with self.assertRaises(ValueError):
            p.decrease_stock(-1)
        with self.assertRaises(TypeError):
            p.decrease_stock(False)
        with self.assertRaises(TypeError):
            p.decrease_stock(1.5)

    def test_inventory_value_is_price_times_quantity(self):
        self.assertEqual(Product("P1", "Item", 25, 4).get_inventory_value(), 100.0)

    def test_product_serialization_includes_type(self):
        d = Product("P1", "Item", 25, 2, "SUP1").to_dict()
        self.assertEqual(d["type"], "Product")
        self.assertEqual(d["supplier_id"], "SUP1")

    def test_food_product_expiry_and_methods(self):
        today = date.today()
        food_exp = FoodProduct("F1", "Milk", 10, 2, "Dairy Co", today - timedelta(days=2))
        food_val = FoodProduct("F2", "Cheese", 20, 5, "Dairy Co", today + timedelta(days=5))

        self.assertTrue(food_exp.is_expired())
        self.assertFalse(food_val.is_expired())
        self.assertEqual(food_val.days_until_expiry(), 5)
        self.assertEqual(food_exp.to_dict()["type"], "FoodProduct")
        self.assertIn("HSD:", str(food_val))

    def test_electronic_product_warranty_and_methods(self):
        device = ElectronicProduct("E1", "Mouse", 20, 1, "Tech Co", 24)
        self.assertEqual(device.warranty_months, 24)
        self.assertEqual(device.to_dict()["warranty_months"], 24)
        self.assertEqual(device.to_dict()["type"], "ElectronicProduct")
        self.assertIn("24 tháng", str(device))

        # Test warranty setter validation
        with self.assertRaises(ValueError):
            device.warranty_months = -1
        with self.assertRaises(TypeError):
            device.warranty_months = "12"


class TestStockTransactionModel(unittest.TestCase):
    def test_transaction_auto_id_and_fields(self):
        tx = StockTransaction(product_id="P1", transaction_type="IMPORT", quantity=5, note="Nhập thêm hàng")
        self.assertTrue(tx.transaction_id)
        self.assertEqual(tx.product_id, "P1")
        self.assertEqual(tx.transaction_type, "IMPORT")
        self.assertEqual(tx.quantity, 5)
        self.assertEqual(tx.note, "Nhập thêm hàng")
        self.assertTrue(tx.timestamp)

    def test_transaction_read_only_properties(self):
        tx = StockTransaction(product_id="P1", transaction_type="EXPORT", quantity=2)
        with self.assertRaises(AttributeError):
            tx.quantity = 10
        with self.assertRaises(AttributeError):
            tx.transaction_type = "IMPORT"

    def test_transaction_invalid_type_rejected(self):
        with self.assertRaises(ValueError):
            StockTransaction(product_id="P1", transaction_type="INVALID_TYPE", quantity=2)

    def test_transaction_serialization(self):
        tx = StockTransaction(product_id="P1", transaction_type="IMPORT", quantity=3, note="Test")
        d = tx.to_dict()
        self.assertEqual(d["product_id"], "P1")
        self.assertEqual(d["transaction_type"], "IMPORT")
        self.assertEqual(d["quantity"], 3)
        self.assertIn("Nhập kho", str(tx))


if __name__ == "__main__":
    unittest.main()
