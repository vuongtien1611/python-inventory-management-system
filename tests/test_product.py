"""Kiểm thử đơn vị cho các lớp mô hình sản phẩm (`models/product.py`).

Người phụ trách: Thành viên 6 - Tú (nhánh `feature/storage-testing`).

Các trường hợp kiểm thử dự kiến:
- Khởi tạo hợp lệ cho `Product`, `FoodProduct`, `ElectronicProduct`.
- Kiểm tra tính đóng gói và validate dữ liệu đầu vào (giá < 0, số lượng < 0, mã rỗng...).
- Kiểm tra tính đa hình của `is_valid()`, `get_inventory_value()` và `__str__()`.

TODO (Tú):
- [ ] Bổ sung unit test cho `Product`, `FoodProduct`, `ElectronicProduct` sau khi Lâm hoàn thành `models/product.py`.
"""

import importlib
import unittest
from models.product import ElectronicProduct, FoodProduct, Product


class TestProjectBootstrap(unittest.TestCase):
    """Bài kiểm thử khởi động đơn giản kiểm tra cấu trúc import của bộ khung dự án."""

    def test_core_packages_importable(self) -> None:
        """Đảm bảo các package và module bộ khung có thể import không lỗi."""
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
        """Đảm bảo hàm `main` trong `cli.menu` tồn tại và gọi được."""
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

    def test_inventory_value_is_price_times_quantity(self):
        self.assertEqual(Product("P1", "Item", 25, 4).get_inventory_value(), 100)

    def test_product_serialization_includes_type(self):
        self.assertEqual(Product("P1", "Item", 25).to_dict()["type"], "Product")

    def test_food_product_serializes_expiry(self):
        food = FoodProduct("F1", "Milk", 10, 2, "Dairy Co", "2026-12-01")
        self.assertEqual(food.to_dict()["expiry_date"], "2026-12-01")

    def test_food_product_accepts_expiry_before_supplier(self):
        food = FoodProduct("F1", "Milk", 10, 2, "2026-12-01", "Dairy Co")
        self.assertEqual(food.supplier, "Dairy Co")
        self.assertEqual(food.expiry_date, "2026-12-01")

    def test_electronic_product_serializes_warranty(self):
        device = ElectronicProduct("E1", "Mouse", 20, 1, "Tech Co", 24)
        self.assertEqual(device.to_dict()["warranty_months"], 24)

    def test_electronic_product_accepts_warranty_before_supplier(self):
        device = ElectronicProduct("E1", "Mouse", 20, 1, 24, "Tech Co")
        self.assertEqual(device.supplier, "Tech Co")
        self.assertEqual(device.warranty_months, 24)

    def test_food_product_rejects_invalid_expiry_format(self):
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            FoodProduct("F1", "Milk", 10, 2, "Dairy Co", "20/11/2026")

    def test_subclass_string_includes_specialized_field(self):
        food = FoodProduct("F1", "Milk", 10, 2, "Dairy Co", "2026-12-01")
        self.assertIn("2026-12-01", str(food))


if __name__ == "__main__":
    unittest.main()

