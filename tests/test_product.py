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


if __name__ == "__main__":
    unittest.main()

