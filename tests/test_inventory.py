"""Unit tests for InventoryManager and Storage persistence layer.

Covers:
- InventoryManager CRUD, validation, search, sorting (Q06, Q08, Q17-Q22).
- Storage JSON persistence (3 entities, atomic replace Q34).
- Storage CSV export (7 columns, Excel friendly utf-8-sig Q35).
"""

import csv
import json
import tempfile
import unittest
from pathlib import Path

from models.product import ElectronicProduct, FoodProduct, Product
from models.stock_transaction import StockTransaction
from models.supplier import Supplier
from services.inventory_manager import InventoryManager
from services.stock_service import StockService
from services.supplier_service import SupplierService
from storage import storage


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.json_path = Path(self.temp_dir.name) / "nested" / "inventory.json"
        self.csv_path = Path(self.temp_dir.name) / "inventory.csv"

        self.products = [
            Product("P1", "Cà phê", 12.5, 4, "SUP1"),
            FoodProduct("P2", "Sữa tươi", 8.0, 3, "SUP2", "2026-12-01"),
            ElectronicProduct("P3", "Chuột không dây", 20.0, 2, "SUP1", 24),
        ]
        self.suppliers = [
            Supplier("SUP1", "Công ty Cà phê", "0912345678", "Hà Nội", "cafe@gmail.com"),
            Supplier("SUP2", "Công ty Sữa", "0987654321", "TP.HCM", "milk@gmail.com"),
        ]
        self.transactions = [
            StockTransaction("TX1", "P1", "IMPORT", 4, "2026-11-19T10:00:00+07:00", "Nhập ban đầu"),
        ]

    def test_save_to_json_creates_directories_and_atomic_replace(self):
        # Decision Q34: Lưu 3 thực thể nguyên tử
        data = {
            "products": self.products,
            "suppliers": self.suppliers,
            "transactions": self.transactions,
        }
        res = storage.save_to_json(data, str(self.json_path))
        self.assertTrue(res)
        self.assertTrue(self.json_path.is_file())
        # Đảm bảo file .tmp không còn tồn tại sau khi hoàn tất atomic replace
        tmp_file = self.json_path.with_name(self.json_path.name + ".tmp")
        self.assertFalse(tmp_file.exists())

    def test_save_preserves_unicode_and_structure(self):
        data = {
            "products": self.products,
            "suppliers": self.suppliers,
            "transactions": self.transactions,
        }
        storage.save_to_json(data, str(self.json_path))
        content = self.json_path.read_text(encoding="utf-8")
        self.assertIn("Cà phê", content)
        self.assertIn("Sữa tươi", content)
        self.assertIn("Chuột không dây", content)

        parsed = json.loads(content)
        self.assertIn("products", parsed)
        self.assertIn("suppliers", parsed)
        self.assertIn("transactions", parsed)
        self.assertEqual(len(parsed["products"]), 3)
        self.assertEqual(len(parsed["suppliers"]), 2)
        self.assertEqual(len(parsed["transactions"]), 1)

    def test_round_trip_restores_concrete_subclasses(self):
        data = {
            "products": self.products,
            "suppliers": self.suppliers,
            "transactions": self.transactions,
        }
        storage.save_to_json(data, str(self.json_path))

        loaded = storage.load_from_json(str(self.json_path))
        loaded_products = loaded["products"]
        self.assertEqual(len(loaded_products), 3)
        self.assertIs(type(loaded_products[0]), Product)
        self.assertIs(type(loaded_products[1]), FoodProduct)
        self.assertIs(type(loaded_products[2]), ElectronicProduct)

        self.assertEqual(loaded_products[1].expiry_date.isoformat(), "2026-12-01")
        self.assertEqual(loaded_products[2].warranty_months, 24)
        self.assertEqual(len(loaded["suppliers"]), 2)
        self.assertEqual(len(loaded["transactions"]), 1)

    def test_missing_file_returns_empty_structure(self):
        loaded = storage.load_from_json(str(Path(self.temp_dir.name) / "nonexistent.json"))
        self.assertEqual(loaded, {"products": [], "suppliers": [], "transactions": []})

    def test_empty_file_returns_empty_structure(self):
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text("   \n", encoding="utf-8")
        loaded = storage.load_from_json(str(self.json_path))
        self.assertEqual(loaded, {"products": [], "suppliers": [], "transactions": []})

    def test_malformed_json_raises_value_error(self):
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text("{malformed json", encoding="utf-8")
        with self.assertRaises(ValueError):
            storage.load_from_json(str(self.json_path))

    def test_csv_export_7_columns_utf8_sig(self):
        # Decision Q35: Xuất CSV 7 cột định dạng chuẩn Excel với utf-8-sig
        storage.export_to_csv(self.products, str(self.csv_path))
        raw_bytes = self.csv_path.read_bytes()
        self.assertTrue(raw_bytes.startswith(b"\xef\xbb\xbf"))  # BOM header

        with self.csv_path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            headers = reader.fieldnames
            expected_headers = [
                "product_id", "name", "product_type", "price", "quantity",
                "inventory_value", "supplier"
            ]
            self.assertEqual(headers, expected_headers)
            rows = list(reader)
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0]["product_id"], "P1")
            self.assertEqual(rows[0]["product_type"], "Product")

    def test_csv_empty_products_still_has_headers(self):
        storage.export_to_csv([], str(self.csv_path))
        with self.csv_path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            self.assertEqual(len(reader.fieldnames), 7)
            self.assertEqual(list(reader), [])


class TestInventoryManager(unittest.TestCase):
    def setUp(self):
        self.p1 = Product("P1", "Laptop Gaming", 1000, 2, "SUP1")
        self.p2 = Product("P2", "Chuột quang", 20, 0, "SUP2")
        self.manager = InventoryManager([self.p1, self.p2])

    def test_get_all_returns_products(self):
        self.assertEqual(len(self.manager.get_all_products()), 2)

    def test_get_product_by_id_success_and_keyerror(self):
        # Decision Q18: ném KeyError khi không tìm thấy mã
        p = self.manager.get_product_by_id("P1")
        self.assertEqual(p.name, "Laptop Gaming")
        with self.assertRaises(KeyError):
            self.manager.get_product_by_id("MISSING")

    def test_duplicate_id_is_rejected(self):
        # Decision Q06: từ chối trùng mã sản phẩm
        with self.assertRaises(ValueError):
            self.manager.add_product(Product("P1", "Trùng lặp", 100))

    def test_add_product_checks_supplier_existence(self):
        # Decision Q14: kiểm tra nhà cung cấp hợp lệ
        sup_service = SupplierService([Supplier("SUP1", "Công ty A", "0912345678")])
        valid_p = Product("P3", "Bàn phím", 50, 1, "SUP1")
        self.manager.add_product(valid_p, supplier_service=sup_service)
        self.assertEqual(len(self.manager.get_all_products()), 3)

        invalid_sup_p = Product("P4", "Tai nghe", 30, 1, "SUP_KHONG_TON_TAI")
        with self.assertRaises(ValueError) as ctx:
            self.manager.add_product(invalid_sup_p, supplier_service=sup_service)
        self.assertIn("không tồn tại", str(ctx.exception))

    def test_non_product_is_rejected(self):
        with self.assertRaises(TypeError):
            self.manager.add_product(object())

    def test_update_product_rejects_quantity(self):
        # Decision Q08: update_product tuyệt đối không nhận trường quantity
        with self.assertRaises(ValueError) as ctx:
            self.manager.update_product("P1", quantity=10)
        self.assertIn("số lượng tồn kho", str(ctx.exception))

    def test_update_product_replaces_valid_fields(self):
        self.manager.update_product("P1", name="Laptop Pro", price=1200)
        updated = self.manager.get_product_by_id("P1")
        self.assertEqual(updated.name, "Laptop Pro")
        self.assertEqual(updated.price, 1200)
        # Số lượng giữ nguyên
        self.assertEqual(updated.quantity, 2)

    def test_update_missing_product_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.manager.update_product("MISSING", price=50)

    def test_delete_product_with_stock_is_rejected(self):
        # Decision Q19: Không cho xóa sản phẩm khi quantity > 0
        with self.assertRaises(ValueError) as ctx:
            self.manager.delete_product("P1")
        self.assertIn("khi tồn kho vẫn còn", str(ctx.exception))
        self.assertIsNotNone(self.manager.get_product_by_id("P1"))

    def test_delete_product_with_transaction_history_rejected(self):
        # Decision Q20: Không cho xóa nếu đã từng có lịch sử giao dịch
        stock_service = StockService(self.manager)
        # Giả lập P2 từng phát sinh giao dịch
        stock_service.replace_transactions([
            StockTransaction(product_id="P2", transaction_type="IMPORT", quantity=5, note="Nhập cũ")
        ])
        self.assertEqual(self.p2.quantity, 0)

        with self.assertRaises(ValueError) as ctx:
            self.manager.delete_product("P2", stock_service=stock_service)
        self.assertIn("lịch sử giao dịch", str(ctx.exception))
        self.assertIsNotNone(self.manager.get_product_by_id("P2"))

    def test_delete_empty_product_without_history_succeeds(self):
        # Xóa thành công khi quantity == 0 và chưa có giao dịch
        stock_service = StockService(self.manager)
        self.manager.delete_product("P2", stock_service=stock_service)
        with self.assertRaises(KeyError):
            self.manager.get_product_by_id("P2")

    def test_search_is_case_insensitive_and_preserves_vietnamese(self):
        # Decision Q21: Tìm kiếm không phân biệt hoa thường nhưng bảo toàn dấu
        res = self.manager.search_product("LAPTOP", by="name")
        self.assertEqual([p.product_id for p in res], ["P1"])

        res2 = self.manager.search_product("quang", by="name")
        self.assertEqual([p.product_id for p in res2], ["P2"])

    def test_search_by_supplier(self):
        res = self.manager.search_product("SUP1", by="supplier")
        self.assertEqual([p.product_id for p in res], ["P1"])

    def test_sort_by_price_and_quantity(self):
        # Decision Q22: Sắp xếp theo giá và số lượng với reverse=True/False
        by_price = self.manager.sort_products("price")
        self.assertEqual([p.product_id for p in by_price], ["P2", "P1"])

        by_price_desc = self.manager.sort_products("price", reverse=True)
        self.assertEqual([p.product_id for p in by_price_desc], ["P1", "P2"])

        by_qty_desc = self.manager.sort_products("quantity", reverse=True)
        self.assertEqual([p.product_id for p in by_qty_desc], ["P1", "P2"])

    def test_invalid_search_or_sort_field_is_rejected(self):
        with self.assertRaises(ValueError):
            self.manager.search_product("a", by="invalid_field")
        with self.assertRaises(ValueError):
            self.manager.sort_products("unsupported_field")


if __name__ == "__main__":
    unittest.main()
