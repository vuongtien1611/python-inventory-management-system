"""Integration tests exercising real CLI handlers with real services/storage."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cli.menu import AppContext, InventoryCLI
from models.product import FoodProduct, Product
from services.inventory_manager import InventoryManager
from services.report_service import ReportService
from services.stock_service import StockService
from storage import storage


class TestCLIReportAndDataFlows(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.inventory = InventoryManager([
            Product("P1", "Stapler", 100, 2, "Office"),
            FoodProduct("F1", "Milk", 50, 1, "Dairy", "2026-11-20"),
        ])
        self.cli = InventoryCLI(AppContext(
            inventory_manager=self.inventory,
            stock_service=StockService(self.inventory),
            report_service=ReportService(self.inventory),
            storage=storage,
        ))

    def test_report_handler_prints_real_inventory_total(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.cli._handle_total_inventory_value()
        self.assertIn("250 VNĐ", output.getvalue())

    def test_report_menu_routes_to_report_handler(self):
        output = io.StringIO()
        with patch("cli.menu.read_menu_choice", side_effect=[1, 0]), contextlib.redirect_stdout(output):
            self.cli.open_report_menu()
        self.assertIn("Tổng giá trị tồn kho: 250 VNĐ", output.getvalue())
        self.assertIn("Đang quay lại menu chính", output.getvalue())

    def test_stock_menu_routes_import_and_export(self):
        output = io.StringIO()
        with patch("cli.menu.read_menu_choice", side_effect=[1, 2, 0]), \
             patch("cli.menu.read_input_safe", side_effect=["P1", "3", "restock", "P1", "1", "sale"]), \
             contextlib.redirect_stdout(output):
            self.cli.open_stock_menu()
        self.assertEqual(self.inventory.get_product_by_id("P1").quantity, 4)
        self.assertIn("Đã nhập kho", output.getvalue())
        self.assertIn("Đã xuất kho", output.getvalue())

    def test_low_stock_cli_handler_calls_report_service(self):
        output = io.StringIO()
        with patch("cli.menu.read_input_safe", return_value="1"), contextlib.redirect_stdout(output):
            self.cli._handle_low_stock_products()
        self.assertIn("F1: Milk", output.getvalue())
        self.assertNotIn("P1: Stapler", output.getvalue())

    def test_expiry_cli_handler_displays_food_status(self):
        output = io.StringIO()
        with patch("cli.menu.read_input_safe", return_value="F1"), contextlib.redirect_stdout(output):
            self.cli._handle_check_food_expiry()
        self.assertIn("2026-11-20", output.getvalue())

    def test_json_and_csv_handlers_use_real_storage(self):
        json_path = Path(self.temp_dir.name) / "inventory.json"
        csv_path = Path(self.temp_dir.name) / "inventory.csv"
        output = io.StringIO()
        with patch("cli.menu.read_input_safe", side_effect=[str(json_path)]), contextlib.redirect_stdout(output):
            self.cli._handle_save_json()
        self.assertTrue(json_path.is_file())

        self.inventory.replace_products([])
        with patch("cli.menu.read_input_safe", side_effect=[str(json_path)]), contextlib.redirect_stdout(output):
            self.cli._handle_load_json()
        self.assertEqual(len(self.inventory.get_all_products()), 2)

        with patch("cli.menu.read_input_safe", side_effect=[str(csv_path)]), contextlib.redirect_stdout(output):
            self.cli._handle_export_csv()
        self.assertTrue(csv_path.is_file())
        self.assertIn("Đã nạp 2 sản phẩm", output.getvalue())
        self.assertIn("Đã xuất CSV", output.getvalue())

    def test_build_app_context_wires_services_and_storage(self):
        from cli.menu import build_app_context

        context = build_app_context()
        self.assertIsInstance(context.inventory_manager, InventoryManager)
        self.assertIsInstance(context.stock_service, StockService)
        self.assertIsInstance(context.report_service, ReportService)
        self.assertIs(context.storage, storage)


if __name__ == "__main__":
    unittest.main()
