"""Unit tests for Supplier model and SupplierService."""

import unittest

from models.product import Product
from models.supplier import Supplier
from services.inventory_manager import InventoryManager
from services.supplier_service import SupplierService


class TestSupplierModel(unittest.TestCase):
    def test_valid_supplier_creation(self):
        sup = Supplier("SUP01", "Vinamilk", "0901234567", "Hà Nội", "contact@vinamilk.com")
        self.assertEqual(sup.supplier_id, "SUP01")
        self.assertEqual(sup.name, "Vinamilk")
        self.assertEqual(sup.phone, "0901234567")
        self.assertEqual(sup.address, "Hà Nội")
        self.assertEqual(sup.email, "contact@vinamilk.com")
        self.assertTrue(sup.is_valid())
        self.assertEqual(sup.to_dict()["supplier_id"], "SUP01")

    def test_supplier_rejects_empty_id_or_name(self):
        with self.assertRaises(ValueError):
            Supplier("", "Name", "0901234567", "Hà Nội", "a@b.com")
        with self.assertRaises(ValueError):
            Supplier("SUP01", "", "0901234567", "Hà Nội", "a@b.com")

    def test_supplier_phone_validation(self):
        # Chứa ký tự chữ hoặc ít hơn 7 chữ số
        with self.assertRaises(ValueError):
            Supplier("SUP01", "Name", "090abc1234", "Hà Nội", "a@b.com")
        with self.assertRaises(ValueError):
            Supplier("SUP01", "Name", "12345", "Hà Nội", "a@b.com")

    def test_supplier_email_validation(self):
        # Decision Q14: định dạng email chuẩn
        with self.assertRaises(ValueError):
            Supplier("SUP01", "Name", "0901234567", "Hà Nội", "invalid-email")
        with self.assertRaises(ValueError):
            Supplier("SUP01", "Name", "0901234567", "Hà Nội", "a@b")


class TestSupplierService(unittest.TestCase):
    def setUp(self):
        self.sup1 = Supplier("SUP01", "Vinamilk", "0901234567", "Hà Nội", "info@vinamilk.com")
        self.sup2 = Supplier("SUP02", "Samsung", "0987654321", "Bắc Ninh", "support@samsung.com")
        self.service = SupplierService([self.sup1, self.sup2])

    def test_get_all_suppliers(self):
        self.assertEqual(len(self.service.get_all_suppliers()), 2)

    def test_get_supplier_by_id_success_and_failure(self):
        sup = self.service.get_supplier_by_id("SUP01")
        self.assertEqual(sup.name, "Vinamilk")
        with self.assertRaises(KeyError):
            self.service.get_supplier_by_id("NONEXISTENT")

    def test_add_supplier_success(self):
        sup3 = Supplier("SUP03", "Apple", "0912345678", "Mỹ", "apple@apple.com")
        self.service.add_supplier(sup3)
        self.assertEqual(len(self.service.get_all_suppliers()), 3)
        self.assertTrue(self.service.has_supplier("SUP03"))

    def test_add_duplicate_supplier_rejected(self):
        # Decision Q16: kiểm tra trùng mã nhà cung cấp
        dup = Supplier("SUP01", "Duplicate Vinamilk", "0901112233", "Hà Nội", "dup@vinamilk.com")
        with self.assertRaises(ValueError) as ctx:
            self.service.add_supplier(dup)
        self.assertIn("đã tồn tại", str(ctx.exception))

    def test_add_non_supplier_rejected(self):
        with self.assertRaises(TypeError):
            self.service.add_supplier(object())

    def test_update_supplier_success(self):
        self.service.update_supplier("SUP01", name="Vinamilk Corp", phone="0911223344")
        updated = self.service.get_supplier_by_id("SUP01")
        self.assertEqual(updated.name, "Vinamilk Corp")
        self.assertEqual(updated.phone, "0911223344")
        self.assertEqual(updated.email, "info@vinamilk.com")

    def test_update_supplier_missing_id(self):
        with self.assertRaises(KeyError):
            self.service.update_supplier("UNKNOWN", name="New Name")

    def test_update_supplier_invalid_phone_or_email(self):
        with self.assertRaises(ValueError):
            self.service.update_supplier("SUP01", phone="abc")
        with self.assertRaises(ValueError):
            self.service.update_supplier("SUP01", email="not-an-email")

    def test_delete_supplier_without_products_succeeds(self):
        inventory = InventoryManager([])
        self.service.delete_supplier("SUP01", inventory_manager=inventory)
        self.assertEqual(len(self.service.get_all_suppliers()), 1)
        self.assertFalse(self.service.has_supplier("SUP01"))

    def test_delete_supplier_referenced_by_product_fails(self):
        # Decision Q15: Cấm xóa nhà cung cấp khi còn sản phẩm tham chiếu
        product = Product("P1", "Sữa đặc", 25000, 10, "SUP01")
        inventory = InventoryManager([product])
        with self.assertRaises(ValueError) as ctx:
            self.service.delete_supplier("SUP01", inventory_manager=inventory)
        self.assertIn("vẫn còn sản phẩm", str(ctx.exception))
        self.assertTrue(self.service.has_supplier("SUP01"))


if __name__ == "__main__":
    unittest.main()
