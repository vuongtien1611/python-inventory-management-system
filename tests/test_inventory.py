"""Unit tests for JSON/CSV persistence and validation behavior."""

import csv
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from storage import storage
from models.product import Product
from services.inventory_manager import InventoryManager


class FakeProduct:
    def __init__(self, product_id, name, price, quantity, supplier=""):
        self.product_id, self.name = product_id, name
        self.price, self.quantity, self.supplier = price, quantity, supplier


class FakeFoodProduct(FakeProduct):
    def __init__(self, product_id, name, price, quantity, supplier="", expiry_date=""):
        super().__init__(product_id, name, price, quantity, supplier)
        self.expiry_date = expiry_date


class FakeElectronicProduct(FakeProduct):
    def __init__(self, product_id, name, price, quantity, supplier="", warranty_months=0):
        super().__init__(product_id, name, price, quantity, supplier)
        self.warranty_months = warranty_months


@patch.object(storage, "_product_types", return_value={
    "Product": FakeProduct,
    "FoodProduct": FakeFoodProduct,
    "ElectronicProduct": FakeElectronicProduct,
})
class TestStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.path = Path(self.temp_dir.name) / "nested" / "products.json"

    def products(self):
        return [
            FakeProduct("P1", "Cà phê", 12.5, 4, "NCC1"),
            FakeFoodProduct("P2", "Sữa", 8, 3, "NCC2", "2026-12-01"),
            FakeElectronicProduct("P3", "Chuột", 20, 2, "NCC3", 24),
        ]

    def test_save_creates_parent_directories(self, _types):
        storage.save_to_json(self.products(), self.path)
        self.assertTrue(self.path.is_file())

    def test_save_preserves_unicode(self, _types):
        storage.save_to_json(self.products(), self.path)
        self.assertIn("Cà phê", self.path.read_text(encoding="utf-8"))

    def test_json_contains_subclass_type_tags(self, _types):
        storage.save_to_json(self.products(), self.path)
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual([p["type"] for p in payload], ["Product", "FoodProduct", "ElectronicProduct"])

    def test_round_trip_restores_concrete_subclasses(self, _types):
        storage.save_to_json(self.products(), self.path)
        result = storage.load_from_json(self.path)
        self.assertEqual([type(p) for p in result], [FakeProduct, FakeFoodProduct, FakeElectronicProduct])

    def test_round_trip_preserves_subclass_fields(self, _types):
        storage.save_to_json(self.products(), self.path)
        result = storage.load_from_json(self.path)
        self.assertEqual(result[1].expiry_date, "2026-12-01")
        self.assertEqual(result[2].warranty_months, 24)

    def test_missing_file_returns_empty_inventory(self, _types):
        self.assertEqual(storage.load_from_json(self.path), [])

    def test_empty_file_returns_empty_inventory(self, _types):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("  \n", encoding="utf-8")
        self.assertEqual(storage.load_from_json(self.path), [])

    def test_malformed_json_raises_value_error(self, _types):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{broken", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "JSON không hợp lệ"):
            storage.load_from_json(self.path)

    def test_non_list_json_raises_value_error(self, _types):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "danh sách"):
            storage.load_from_json(self.path)

    def test_unknown_product_type_raises_value_error(self, _types):
        self.path.parent.mkdir(parents=True)
        self.path.write_text('[{"type":"Unknown"}]', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "không được hỗ trợ"):
            storage.load_from_json(self.path)

    def test_csv_is_excel_friendly_and_contains_rows(self, _types):
        csv_path = self.path.with_suffix(".csv")
        storage.export_to_csv(self.products(), csv_path)
        raw = csv_path.read_bytes()
        self.assertTrue(raw.startswith(b"\xef\xbb\xbf"))
        with csv_path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1]["expiry_date"], "2026-12-01")

    def test_csv_empty_inventory_still_has_headers(self, _types):
        csv_path = self.path.with_suffix(".csv")
        storage.export_to_csv([], csv_path)
        with csv_path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            self.assertIn("product_id", reader.fieldnames)
            self.assertEqual(list(reader), [])

    def test_unsupported_object_is_rejected(self, _types):
        with self.assertRaises(TypeError):
            storage.save_to_json([SimpleNamespace(foo="bar")], self.path)


class TestInventoryManager(unittest.TestCase):
    def setUp(self):
        self.manager = InventoryManager([
            Product("P1", "Laptop", 1000, 2, "North Vendor"),
            Product("P2", "Mouse", 20, 0, "South Vendor"),
        ])

    def test_get_all_returns_products(self):
        self.assertEqual(len(self.manager.get_all_products()), 2)

    def test_duplicate_id_is_rejected(self):
        with self.assertRaises(ValueError):
            self.manager.add_product(Product("P1", "Duplicate", 2))

    def test_non_product_is_rejected(self):
        with self.assertRaises(TypeError):
            self.manager.add_product(object())

    def test_update_replaces_product_with_valid_values(self):
        self.manager.update_product("P1", price=900)
        self.assertEqual(self.manager.get_product_by_id("P1").price, 900)

    def test_invalid_update_does_not_change_product(self):
        with self.assertRaises(ValueError):
            self.manager.update_product("P1", quantity=-1)
        self.assertEqual(self.manager.get_product_by_id("P1").quantity, 2)

    def test_update_missing_product_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.manager.update_product("MISSING", price=1)

    def test_delete_empty_product(self):
        self.manager.delete_product("P2")
        self.assertIsNone(self.manager.get_product_by_id("P2"))

    def test_delete_product_with_stock_is_rejected(self):
        with self.assertRaises(ValueError):
            self.manager.delete_product("P1")
        self.assertIsNotNone(self.manager.get_product_by_id("P1"))

    def test_search_is_case_insensitive(self):
        self.assertEqual([p.product_id for p in self.manager.search_product("LAP", by="name")], ["P1"])

    def test_search_by_supplier(self):
        self.assertEqual([p.product_id for p in self.manager.search_product("south", by="supplier")], ["P2"])

    def test_sort_by_price_and_quantity(self):
        self.assertEqual([p.product_id for p in self.manager.sort_products("price")], ["P2", "P1"])
        self.assertEqual([p.product_id for p in self.manager.sort_products("quantity", reverse=True)], ["P1", "P2"])

    def test_invalid_search_or_sort_field_is_rejected(self):
        with self.assertRaises(ValueError):
            self.manager.search_product("a", by="invalid")
        with self.assertRaises(ValueError):
            self.manager.sort_products("supplier")


if __name__ == "__main__":
    unittest.main()
