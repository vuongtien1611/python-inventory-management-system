"""Unit tests for import/export inventory rules and transaction history."""

import unittest

from models.product import Product
from services.inventory_manager import InventoryManager
from services.stock_service import StockService


class TestStockService(unittest.TestCase):
    def setUp(self):
        self.product = Product("P1", "Keyboard", 100, 5, "Vendor")
        self.inventory = InventoryManager([self.product])
        self.service = StockService(self.inventory)

    def test_import_increases_stock_and_records_transaction(self):
        transaction = self.service.import_stock("P1", 3, "restock")
        self.assertEqual(self.product.quantity, 8)
        self.assertEqual(transaction["type"], "import")

    def test_export_decreases_stock_and_records_transaction(self):
        transaction = self.service.export_stock("P1", 2, "sale")
        self.assertEqual(self.product.quantity, 3)
        self.assertEqual(transaction["qty"], 2)

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
        with self.assertRaises(ValueError):
            self.service.import_stock("P1", 1.5)

    def test_boolean_quantity_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.import_stock("P1", True)

    def test_unknown_product_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.export_stock("MISSING", 1)

    def test_history_can_be_filtered_by_product(self):
        self.service.import_stock("P1", 1)
        self.assertEqual(len(self.service.get_transaction_history("P1")), 1)
        self.assertEqual(self.service.get_transaction_history("OTHER"), [])


if __name__ == "__main__":
    unittest.main()
