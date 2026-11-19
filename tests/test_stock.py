"""Unit tests for import/export inventory rules, constraints and transaction history."""

import unittest
from datetime import date, timedelta
from unittest.mock import patch

from models.product import FoodProduct, Product
from models.stock_transaction import StockTransaction
from services.inventory_manager import InventoryManager
from services.stock_service import StockService


class TestStockService(unittest.TestCase):
    def setUp(self):
        self.product = Product("P1", "Keyboard", 100, 5, "Vendor")
        today = date.today()
        self.expired_food = FoodProduct(
            "F_EXP", "Expired Milk", 20, 0, "Dairy", today - timedelta(days=5)
        )
        self.valid_food = FoodProduct(
            "F_VAL", "Fresh Milk", 20, 2, "Dairy", today + timedelta(days=10)
        )
        self.inventory = InventoryManager([self.product, self.expired_food, self.valid_food])
        self.service = StockService(self.inventory)

    def test_import_increases_stock_and_records_transaction(self):
        tx = self.service.import_stock("P1", 3, "restock")
        self.assertEqual(self.product.quantity, 8)
        self.assertIsInstance(tx, StockTransaction)
        self.assertEqual(tx.transaction_type, "IMPORT")
        self.assertEqual(tx.quantity, 3)
        self.assertEqual(tx.note, "restock")
        self.assertTrue(tx.transaction_id)

    def test_export_decreases_stock_and_records_transaction(self):
        tx = self.service.export_stock("P1", 2, "sale")
        self.assertEqual(self.product.quantity, 3)
        self.assertIsInstance(tx, StockTransaction)
        self.assertEqual(tx.transaction_type, "EXPORT")
        self.assertEqual(tx.quantity, 2)
        self.assertEqual(tx.note, "sale")

    def test_export_to_zero_is_permitted(self):
        # Decision Q24: Cho phép xuất hết tồn kho về đúng 0
        tx = self.service.export_stock("P1", 5, "clearance")
        self.assertEqual(self.product.quantity, 0)
        self.assertEqual(tx.quantity, 5)

    def test_export_cannot_exceed_stock(self):
        with self.assertRaises(ValueError):
            self.service.export_stock("P1", 6)
        self.assertEqual(self.product.quantity, 5)
        self.assertEqual(self.service.get_transaction_history(), [])

    def test_zero_quantity_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.import_stock("P1", 0)

    def test_negative_quantity_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.export_stock("P1", -1)

    def test_non_integer_quantity_is_rejected(self):
        with self.assertRaises(TypeError):
            self.service.import_stock("P1", 1.5)

    def test_boolean_quantity_is_rejected(self):
        with self.assertRaises(TypeError):
            self.service.import_stock("P1", True)

    def test_unknown_product_is_rejected(self):
        with self.assertRaises(KeyError):
            self.service.export_stock("MISSING", 1)

    def test_history_can_be_filtered_by_product(self):
        self.service.import_stock("P1", 1)
        self.assertEqual(len(self.service.get_transaction_history("P1")), 1)
        self.assertEqual(self.service.get_transaction_history("OTHER"), [])

    def test_has_product_transactions_check(self):
        # Decision Q20: kiểm tra lịch sử trước khi xóa sản phẩm
        self.assertFalse(self.service.has_product_transactions("P1"))
        self.service.import_stock("P1", 2)
        self.assertTrue(self.service.has_product_transactions("P1"))
        self.assertFalse(self.service.has_product_transactions("P2"))

    def test_import_expired_food_is_rejected(self):
        # Decision Q10: Từ chối nhập kho thực phẩm đã hết hạn sử dụng
        with self.assertRaises(ValueError) as ctx:
            self.service.import_stock("F_EXP", 10)
        self.assertIn("đã hết hạn", str(ctx.exception))
        self.assertEqual(self.expired_food.quantity, 0)

    def test_import_valid_food_succeeds(self):
        tx = self.service.import_stock("F_VAL", 5)
        self.assertEqual(self.valid_food.quantity, 7)
        self.assertEqual(tx.quantity, 5)

    def test_atomic_rollback_on_transaction_failure(self):
        # Giả lập lỗi khi khởi tạo StockTransaction để kiểm tra rollback số lượng
        with patch("services.stock_service.StockTransaction", side_effect=RuntimeError("Simulated write error")):
            with self.assertRaises(RuntimeError):
                self.service.import_stock("P1", 4)
            # Tồn kho phải được khôi phục về ban đầu (5)
            self.assertEqual(self.product.quantity, 5)


if __name__ == "__main__":
    unittest.main()
