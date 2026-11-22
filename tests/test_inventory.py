"""Unit tests for JSON/CSV persistence and validation behavior."""

import csv
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from storage import storage
from models.product import Product, FoodProduct, ElectronicProduct
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


class TestInventoryManagerExtended(unittest.TestCase):
    """Bộ kiểm thử mở rộng cho InventoryManager (Thành viên 3 - Sơn)."""

    def setUp(self):
        self.manager = InventoryManager([
            Product("SP01", "Bút bi", 5000, 10, "Thiên Long"),
            Product("SP011", "Vở kẻ ngang", 12000, 0, "Hồng Hà"),
            FoodProduct("F1", "Sữa tươi", 15000, 3, "Vinamilk", "2026-12-01"),
            ElectronicProduct("E1", "Chuột không dây", 250000, 2, "Logitech", 12),
        ])

    # --- Thêm / Khởi tạo ---
    def test_add_valid_product(self):
        """Thêm sản phẩm hợp lệ thì get_product_by_id lấy lại được."""
        p = Product("SP99", "Bàn phím cơ", 800000, 5, "Akko")
        self.manager.add_product(p)
        self.assertEqual(self.manager.get_product_by_id("SP99").name, "Bàn phím cơ")

    def test_add_invalid_product_rejected(self):
        """Thêm sản phẩm có is_valid() trả False thì ném ValueError và kho không đổi."""
        class InvalidProduct(Product):
            def is_valid(self) -> bool:
                return False

        invalid_p = InvalidProduct("INV01", "Hỏng", 1000, 1, "NCC")
        count_before = len(self.manager.get_all_products())
        with self.assertRaises(ValueError):
            self.manager.add_product(invalid_p)
        self.assertEqual(len(self.manager.get_all_products()), count_before)

    def test_add_product_with_whitespace_id_rejected(self):
        """Thêm sản phẩm có mã chứa khoảng trắng thừa ở hai đầu bị từ chối."""
        with self.assertRaises(ValueError):
            self.manager.add_product(Product(" X1", "Sản phẩm lỗi mã", 1000, 1, "NCC"))

    def test_init_with_duplicate_id_rejected(self):
        """Khởi tạo InventoryManager với danh sách có mã trùng thì ném ValueError."""
        with self.assertRaises(ValueError):
            InventoryManager([
                Product("P01", "SP 1", 100, 1),
                Product("P01", "SP trùng", 200, 2),
            ])

    # --- Tra cứu ---
    def test_get_product_by_id_with_whitespace(self):
        """get_product_by_id với mã có khoảng trắng thừa vẫn tìm thấy."""
        self.assertIsNotNone(self.manager.get_product_by_id(" SP01 "))

    def test_get_product_by_id_returns_same_instance(self):
        """get_product_by_id trả đúng cùng một đối tượng (assertIs)."""
        p = self.manager.get_product_by_id("SP01")
        self.assertIs(self.manager.get_product_by_id("SP01"), p)

    def test_get_product_by_id_missing(self):
        """Mã không tồn tại trả None."""
        self.assertIsNone(self.manager.get_product_by_id("KHONG_CO"))

    def test_get_all_products_returns_new_list(self):
        """get_all_products() trả list mới, sửa bên ngoài không đổi kho."""
        lst = self.manager.get_all_products()
        lst.clear()
        self.assertEqual(len(self.manager.get_all_products()), 4)

    # --- Cập nhật ---
    def test_update_food_product_expiry_date(self):
        """Cập nhật expiry_date của FoodProduct thành công và vẫn giữ nguyên kiểu FoodProduct."""
        self.manager.update_product("F1", expiry_date="2027-01-01")
        p = self.manager.get_product_by_id("F1")
        self.assertIsInstance(p, FoodProduct)
        self.assertEqual(p.expiry_date, "2027-01-01")

    def test_update_electronic_product_warranty(self):
        """Cập nhật warranty_months của ElectronicProduct thành công và vẫn là ElectronicProduct."""
        self.manager.update_product("E1", warranty_months=24)
        p = self.manager.get_product_by_id("E1")
        self.assertIsInstance(p, ElectronicProduct)
        self.assertEqual(p.warranty_months, 24)

    def test_update_unsupported_field_on_base_product(self):
        """Cập nhật expiry_date trên Product thường bị từ chối bằng ValueError."""
        with self.assertRaises(ValueError):
            self.manager.update_product("SP01", expiry_date="2027-01-01")

    def test_update_unknown_field_rejected(self):
        """Cập nhật trường lạ (color='red') thì ném ValueError."""
        with self.assertRaises(ValueError):
            self.manager.update_product("SP01", color="red")

    def test_update_product_id_rejected(self):
        """Đổi product_id bị cấm bằng ValueError."""
        with self.assertRaises(ValueError):
            self.manager.update_product("SP01", product_id="NEW_ID")

    def test_update_without_fields_rejected(self):
        """Không truyền trường nào để cập nhật thì ném ValueError."""
        with self.assertRaises(ValueError):
            self.manager.update_product("SP01")

    def test_update_invalid_data_preserves_old_state(self):
        """Cập nhật giá âm bị từ chối và dữ liệu cũ không bị thay đổi."""
        with self.assertRaises(ValueError):
            self.manager.update_product("SP01", price=-5)
        self.assertEqual(self.manager.get_product_by_id("SP01").price, 5000)

    def test_update_with_whitespace_id(self):
        """Cập nhật với mã có khoảng trắng thừa vẫn tìm đúng sản phẩm."""
        self.manager.update_product(" SP01 ", price=6000)
        self.assertEqual(self.manager.get_product_by_id("SP01").price, 6000)

    # --- Xóa ---
    def test_delete_missing_id_raises_key_error(self):
        """Xóa mã không tồn tại thì ném KeyError."""
        with self.assertRaises(KeyError):
            self.manager.delete_product("MISSING_ID")

    def test_delete_product_with_whitespace_id(self):
        """Xóa với mã có khoảng trắng thừa và tồn kho 0 thì xóa được."""
        self.manager.delete_product(" SP011 ")
        self.assertIsNone(self.manager.get_product_by_id("SP011"))

    # --- Tìm kiếm ---
    def test_search_by_id_exact_match(self):
        """Tìm theo id phải khớp chính xác toàn bộ mã, không trả về mã chứa nó."""
        results = self.manager.search_product("SP01", by="id")
        self.assertEqual([p.product_id for p in results], ["SP01"])

    def test_search_by_id_case_insensitive_and_stripped(self):
        """Tìm theo id bỏ qua hoa/thường và khoảng trắng thừa."""
        results = self.manager.search_product("  sp01 ", by="id")
        self.assertEqual([p.product_id for p in results], ["SP01"])

    def test_search_by_name_vietnamese_accent(self):
        """Tìm theo tên hỗ trợ tiếng Việt có dấu và không phân biệt hoa thường."""
        results = self.manager.search_product("sữa", by="name")
        self.assertEqual([p.product_id for p in results], ["F1"])

    def test_search_by_supplier_partial(self):
        """Tìm theo nhà cung cấp khớp một phần."""
        results = self.manager.search_product("vina", by="supplier")
        self.assertEqual([p.product_id for p in results], ["F1"])

    def test_search_empty_keyword_raises_value_error(self):
        """Từ khóa rỗng hoặc chỉ khoảng trắng đều ném ValueError."""
        with self.assertRaises(ValueError):
            self.manager.search_product("", by="name")
        with self.assertRaises(ValueError):
            self.manager.search_product("   ", by="name")

    def test_search_no_match_returns_empty_list(self):
        """Không tìm thấy kết quả thì trả về list rỗng []."""
        self.assertEqual(self.manager.search_product("XYZ_NOT_FOUND", by="name"), [])

    def test_search_empty_inventory_returns_empty_list(self):
        """Kho rỗng khi tìm kiếm trả về list rỗng []."""
        empty_mgr = InventoryManager()
        self.assertEqual(empty_mgr.search_product("laptop", by="name"), [])

    # --- Sắp xếp ---
    def test_sort_by_price_asc_and_desc(self):
        """Sắp xếp theo giá tăng dần và giảm dần đúng thứ tự."""
        asc = [p.product_id for p in self.manager.sort_products("price", reverse=False)]
        desc = [p.product_id for p in self.manager.sort_products("price", reverse=True)]
        self.assertEqual(asc, ["SP01", "SP011", "F1", "E1"])
        self.assertEqual(desc, ["E1", "F1", "SP011", "SP01"])

    def test_sort_by_quantity_asc_and_desc(self):
        """Sắp xếp theo số lượng tăng dần và giảm dần đúng thứ tự."""
        asc = [p.product_id for p in self.manager.sort_products("quantity", reverse=False)]
        desc = [p.product_id for p in self.manager.sort_products("quantity", reverse=True)]
        self.assertEqual(asc, ["SP011", "E1", "F1", "SP01"])
        self.assertEqual(desc, ["SP01", "F1", "E1", "SP011"])

    def test_sort_does_not_mutate_internal_order(self):
        """Sắp xếp không làm thay đổi thứ tự lưu trữ ban đầu trong kho."""
        self.manager.sort_products("price")
        original_ids = [p.product_id for p in self.manager.get_all_products()]
        self.assertEqual(original_ids, ["SP01", "SP011", "F1", "E1"])

    def test_sort_empty_inventory(self):
        """Kho rỗng sắp xếp trả về []."""
        empty_mgr = InventoryManager()
        self.assertEqual(empty_mgr.sort_products("price"), [])

    # --- Thay thế danh sách ---
    def test_replace_products_valid(self):
        """Thay bằng danh sách hợp lệ thì kho đúng danh sách mới."""
        new_list = [Product("NEW1", "Hàng mới", 50, 1)]
        self.manager.replace_products(new_list)
        self.assertEqual([p.product_id for p in self.manager.get_all_products()], ["NEW1"])

    def test_replace_products_invalid_preserves_old_state(self):
        """Thay bằng danh sách có mã trùng thì ném ValueError và kho cũ giữ nguyên."""
        invalid_list = [Product("DUP", "A", 10, 1), Product("DUP", "B", 20, 2)]
        with self.assertRaises(ValueError):
            self.manager.replace_products(invalid_list)
        self.assertEqual(len(self.manager.get_all_products()), 4)

    def test_replace_products_empty(self):
        """Thay bằng [] thì kho thành rỗng."""
        self.manager.replace_products([])
        self.assertEqual(self.manager.get_all_products(), [])


if __name__ == "__main__":
    unittest.main()
