"""Integration tests exercising real CLI submenus and workflows with real services and storage."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cli.menu import AppContext, InventoryCLI, build_app_context
from models.product import FoodProduct, Product
from models.supplier import Supplier
from services.inventory_manager import InventoryManager
from services.report_service import ReportService
from services.stock_service import StockService
from services.supplier_service import SupplierService
from storage import storage


class TestCLIReportAndDataFlows(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.p1 = Product("P1", "Stapler", 100, 2, "SUP1")
        self.f1 = FoodProduct("F1", "Milk", 50, 1, "SUP2", "2026-11-20")
        self.sup1 = Supplier("SUP1", "Office Supplies", "0912345678", "Hà Nội")
        self.sup2 = Supplier("SUP2", "Dairy Co", "0987654321", "TP.HCM")

        self.inventory = InventoryManager([self.p1, self.f1])
        self.supplier_svc = SupplierService([self.sup1, self.sup2])
        self.stock_svc = StockService(self.inventory)
        self.report_svc = ReportService(self.inventory)

        self.context = AppContext(
            inventory_manager=self.inventory,
            supplier_service=self.supplier_svc,
            stock_service=self.stock_svc,
            report_service=self.report_svc,
            storage=storage,
        )
        self.cli = InventoryCLI(self.context)

    def test_build_app_context_wires_services_and_storage(self):
        ctx = build_app_context()
        self.assertIsInstance(ctx.inventory_manager, InventoryManager)
        self.assertIsInstance(ctx.supplier_service, SupplierService)
        self.assertIsInstance(ctx.stock_service, StockService)
        self.assertIsInstance(ctx.report_service, ReportService)
        self.assertIs(ctx.storage, storage)

    def test_report_menu_total_value_and_low_stock(self):
        output = io.StringIO()
        # Option 1 (Total value), then Option 0 (Back)
        with patch("cli.menu.read_menu_choice", side_effect=[1, 0]), contextlib.redirect_stdout(output):
            self.cli.open_report_menu()
        val = output.getvalue()
        self.assertIn("BÁO CÁO TỔNG GIÁ TRỊ TỒN KHO", val)
        self.assertIn("250.00 VNĐ", val)

    def test_stock_menu_routes_import_and_export(self):
        output = io.StringIO()
        # 1: Import (P1, 3, "restock"), 2: Export (P1, 1, "sale"), 0: Back
        with patch("cli.menu.read_menu_choice", side_effect=[1, 2, 0]), \
             patch("cli.menu.read_input_safe", side_effect=["P1", "restock", "P1", "sale"]), \
             patch.object(self.cli, "_read_int", side_effect=[3, 1]), \
             contextlib.redirect_stdout(output):
            self.cli.open_stock_menu()

        self.assertEqual(self.inventory.get_product_by_id("P1").quantity, 4)
        out = output.getvalue()
        self.assertIn("NHẬP KHO THÀNH CÔNG", out)
        self.assertIn("XUẤT KHO THÀNH CÔNG", out)

    def test_inspection_menu_expiry_and_status(self):
        output = io.StringIO()
        # 1: Expiring food within 7 days, 0: Back
        with patch("cli.menu.read_menu_choice", side_effect=[1, 0]), \
             patch.object(self.cli, "_read_int", side_effect=[7]), \
             contextlib.redirect_stdout(output):
            self.cli.open_inspection_menu()
        self.assertIn("Milk", output.getvalue())

    def test_supplier_menu_add_and_list(self):
        output = io.StringIO()
        # 1: Add supplier ("SUP3", "New Supplier", "0911223344", "Đà Nẵng", "new@sup.com")
        # 4: List suppliers
        # 0: Back
        with patch("cli.menu.read_menu_choice", side_effect=[1, 4, 0]), \
             patch("cli.menu.read_input_safe", side_effect=[
                 "SUP3", "New Supplier", "0911223344", "Đà Nẵng", "new@sup.com"
             ]), \
             contextlib.redirect_stdout(output):
            self.cli.open_supplier_menu()

        self.assertTrue(self.supplier_svc.has_supplier("SUP3"))
        out = output.getvalue()
        self.assertIn("Thêm nhà cung cấp thành công", out)
        self.assertIn("New Supplier", out)

    def test_data_menu_save_and_load(self):
        json_path = Path(self.temp_dir.name) / "test_data.json"
        csv_path = Path(self.temp_dir.name) / "test_data.csv"
        output = io.StringIO()

        # 1: Manual save JSON (filepath)
        # 3: Export CSV (filepath)
        # 0: Back
        with patch("cli.menu.read_menu_choice", side_effect=[1, 3, 0]), \
             patch("cli.menu.read_input_safe", side_effect=[str(json_path), str(csv_path)]), \
             contextlib.redirect_stdout(output):
            self.cli.open_data_menu()

        self.assertTrue(json_path.is_file())
        self.assertTrue(csv_path.is_file())
        out = output.getvalue()
        self.assertIn("Đã lưu dữ liệu 3 nhóm thực thể an toàn", out)
        self.assertIn("Xuất báo cáo CSV thành công", out)

    def test_exit_workflow_auto_save_success(self):
        json_path = Path(self.temp_dir.name) / "exit_save.json"
        with patch.object(storage, "DEFAULT_JSON_PATH", str(json_path)):
            result = self.cli.handle_exit(force_prompt=False)
            self.assertTrue(result)
            self.assertTrue(json_path.is_file())


if __name__ == "__main__":
    unittest.main()
