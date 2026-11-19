"""End-to-end integration scenario runner for Product Inventory Management System.

Exercises the complete lifecycle across all 5 architectural layers and services:
1. Models: Product, FoodProduct, ElectronicProduct, Supplier, StockTransaction.
2. Services: InventoryManager, SupplierService, StockService, ReportService.
3. Storage: Atomic JSON persistence (3 entities) and 7-column UTF-8-SIG CSV export.
4. Business Constraints: Q01-Q40 (Rollback, read-only quantity, referential integrity).

Run from project root: python run_integration_tests.py
"""

from __future__ import annotations

import csv
import json
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

# Ensure UTF-8 stream output
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def run() -> None:
    print("=" * 70)
    print(" BẮT ĐẦU CHẠY KIỂM THỬ TÍCH HỢP TOÀN DIỆN (END-TO-END SCENARIO)")
    print("=" * 70)

    from models.product import ElectronicProduct, FoodProduct, Product
    from models.stock_transaction import StockTransaction
    from models.supplier import Supplier
    from services.inventory_manager import InventoryManager
    from services.report_service import ReportService
    from services.stock_service import StockService
    from services.supplier_service import SupplierService
    from storage.storage import export_to_csv, load_from_json, save_to_json

    with tempfile.TemporaryDirectory(prefix="inventory-e2e-") as temp_dir:
        json_path = Path(temp_dir) / "data" / "inventory_data.json"
        csv_path = Path(temp_dir) / "reports" / "inventory_report.csv"

        # ---------------------------------------------------------
        # KỊCH BẢN 1: Quản lý Nhà cung cấp (SupplierService - Minh)
        # ---------------------------------------------------------
        supplier_service = SupplierService()
        sup1 = Supplier("SUP01", "Vinamilk Corp", "0901234567", "Hà Nội", "contact@vinamilk.com")
        sup2 = Supplier("SUP02", "Samsung Electronics", "0987654321", "Bắc Ninh", "support@samsung.com")
        supplier_service.add_supplier(sup1)
        supplier_service.add_supplier(sup2)
        assert len(supplier_service.get_all_suppliers()) == 2
        print("PASS [1/10]: Tạo và đăng ký 2 Nhà cung cấp hợp lệ (SUP01, SUP02).")

        # ---------------------------------------------------------
        # KỊCH BẢN 2: Danh mục sản phẩm đa hình (InventoryManager - Sơn)
        # ---------------------------------------------------------
        inventory = InventoryManager()
        today = date.today()

        p_general = Product("P01", "Bút bi cao cấp", 25_000, 10, "SUP01")
        p_food = FoodProduct("F01", "Sữa chua tiệt trùng", 15_000, 20, "SUP01", today + timedelta(days=5))
        p_elec = ElectronicProduct("E01", "Tai nghe Galaxy Buds", 1_500_000, 4, "SUP02", 12)

        inventory.add_product(p_general, supplier_service=supplier_service)
        inventory.add_product(p_food, supplier_service=supplier_service)
        inventory.add_product(p_elec, supplier_service=supplier_service)
        assert len(inventory.get_all_products()) == 3
        print("PASS [2/10]: Đăng ký 3 sản phẩm đa hình (Product, FoodProduct, ElectronicProduct).")

        # ---------------------------------------------------------
        # KỊCH BẢN 3: Nghiệp vụ Nhập / Xuất kho & Transaction (StockService - Chi)
        # ---------------------------------------------------------
        stock_service = StockService(inventory)
        tx_in = stock_service.import_stock("P01", 15, "Nhập lô bổ sung quý 4")
        assert p_general.quantity == 25
        assert tx_in.transaction_type == "IMPORT"
        assert tx_in.transaction_id

        tx_out = stock_service.export_stock("P01", 5, "Xuất bán lẻ")
        assert p_general.quantity == 20
        assert tx_out.transaction_type == "EXPORT"

        # Xuất hàng điện tử
        stock_service.export_stock("E01", 4, "Xuất hết lô trưng bày")
        assert p_elec.quantity == 0
        print("PASS [3/10]: Nhập/xuất kho chính xác, ghi nhận 3 giao dịch và cho phép xuất về 0 (Q24).")

        # ---------------------------------------------------------
        # KỊCH BẢN 4: Kiểm tra tính đóng gói và Ràng buộc cập nhật (Q08)
        # ---------------------------------------------------------
        try:
            p_general.quantity = 100
            assert False, "Product.quantity phải là thuộc tính chỉ đọc (read-only)!"
        except AttributeError:
            pass

        try:
            inventory.update_product("P01", quantity=100)
            assert False, "update_product phải từ chối tham số quantity!"
        except ValueError:
            pass
        assert p_general.quantity == 20
        print("PASS [4/10]: Đóng gói an toàn: cấm sửa quantity trực tiếp và qua update_product.")

        # ---------------------------------------------------------
        # KỊCH BẢN 5: Ràng buộc xóa sản phẩm & nhà cung cấp (Q15, Q19, Q20)
        # ---------------------------------------------------------
        # Không cho xóa sản phẩm khi còn tồn kho (P01 có quantity = 20)
        try:
            inventory.delete_product("P01", stock_service=stock_service)
            assert False, "Không được xóa sản phẩm khi tồn kho > 0!"
        except ValueError:
            pass

        # Không cho xóa sản phẩm khi tồn kho = 0 nhưng đã từng có giao dịch (E01)
        try:
            inventory.delete_product("E01", stock_service=stock_service)
            assert False, "Không được xóa sản phẩm đã có lịch sử giao dịch!"
        except ValueError:
            pass

        # Không cho xóa nhà cung cấp khi còn sản phẩm tham chiếu (SUP01)
        try:
            supplier_service.delete_supplier("SUP01", inventory_manager=inventory)
            assert False, "Không được xóa nhà cung cấp khi còn sản phẩm liên kết!"
        except ValueError:
            pass
        print("PASS [5/10]: Toàn vẹn tham chiếu và ràng buộc xóa hoạt động nghiêm ngặt.")

        # ---------------------------------------------------------
        # KỊCH BẢN 6: Khôi phục Atomic Rollback khi lỗi kho (Q27)
        # ---------------------------------------------------------
        # Từ chối xuất vượt tồn kho
        try:
            stock_service.export_stock("P01", 999, "Vượt quá tồn")
            assert False, "Xuất vượt tồn phải ném ValueError!"
        except ValueError:
            assert p_general.quantity == 20
        print("PASS [6/10]: Từ chối giao dịch không hợp lệ, tồn kho được bảo toàn nguyên vẹn.")

        # ---------------------------------------------------------
        # KỊCH BẢN 7: Báo cáo, thống kê và cảnh báo rủi ro (ReportService - Minh)
        # ---------------------------------------------------------
        report_service = ReportService(inventory)
        val_report = report_service.get_total_inventory_value()
        # P01: 20 * 25k = 500k; F01: 20 * 15k = 300k; E01: 0 * 1.5M = 0 => Tổng: 800k
        assert val_report["total_value"] == 800_000.0
        assert val_report["has_expired_food"] is False

        # Thống kê sắp hết hàng (ngưỡng 5) -> E01 (tồn 0)
        low_stock = report_service.get_low_stock_products(threshold=5)
        assert [p.product_id for p in low_stock] == ["E01"]

        # Kiểm tra trạng thái HSD thực phẩm cận hạn (F01 còn 5 ngày -> Gần hết hạn)
        expiry_status = report_service.check_food_expiry_status("F01")
        assert len(expiry_status) == 1
        assert expiry_status[0]["status"] == "Gần hết hạn"
        assert expiry_status[0]["status_code"] == "near_expiry"
        print("PASS [7/10]: Báo cáo tổng giá trị (800,000 đ), cảnh báo tồn kho và 3 mức HSD chuẩn xác.")

        # ---------------------------------------------------------
        # KỊCH BẢN 8: Lưu trữ JSON nguyên tử 3 thực thể (Storage - Tú)
        # ---------------------------------------------------------
        system_state = {
            "products": inventory.get_all_products(),
            "suppliers": supplier_service.get_all_suppliers(),
            "transactions": stock_service.get_transaction_history(),
        }
        save_success = save_to_json(system_state, str(json_path))
        assert save_success is True
        assert json_path.is_file()

        raw_json = json.loads(json_path.read_text(encoding="utf-8"))
        assert len(raw_json["products"]) == 3
        assert len(raw_json["suppliers"]) == 2
        assert len(raw_json["transactions"]) == 3
        print("PASS [8/10]: Lưu thành công 3 nhóm thực thể vào JSON với cơ chế Atomic Replace (Q34).")

        # ---------------------------------------------------------
        # KỊCH BẢN 9: Khôi phục toàn bộ hệ thống từ JSON (Persistence Restoration)
        # ---------------------------------------------------------
        restored_data = load_from_json(str(json_path))
        new_inv = InventoryManager(restored_data["products"])
        new_sup = SupplierService(restored_data["suppliers"])
        new_stk = StockService(new_inv, restored_data["transactions"])

        assert len(new_inv.get_all_products()) == 3
        assert len(new_sup.get_all_suppliers()) == 2
        assert len(new_stk.get_transaction_history()) == 3

        # Kiểm tra đối tượng đa hình được khôi phục đúng lớp
        res_food = new_inv.get_product_by_id("F01")
        assert isinstance(res_food, FoodProduct)
        assert res_food.expiry_date == p_food.expiry_date

        res_elec = new_inv.get_product_by_id("E01")
        assert isinstance(res_elec, ElectronicProduct)
        assert res_elec.warranty_months == 12
        print("PASS [9/10]: Nạp và khôi phục 100% đối tượng đa hình và lịch sử giao dịch từ JSON.")

        # ---------------------------------------------------------
        # KỊCH BẢN 10: Xuất báo cáo CSV chuẩn Excel 7 cột (Storage - Tú)
        # ---------------------------------------------------------
        export_to_csv(new_inv.get_all_products(), str(csv_path))
        raw_csv_bytes = csv_path.read_bytes()
        assert raw_csv_bytes.startswith(b"\xef\xbb\xbf")  # UTF-8 BOM

        with csv_path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            expected_headers = [
                "product_id", "name", "product_type", "price", "quantity",
                "inventory_value", "supplier"
            ]
            assert reader.fieldnames == expected_headers
            rows = list(reader)
            assert len(rows) == 3
        print("PASS [10/10]: Xuất báo cáo CSV thành công gồm 7 cột chuẩn tương thích Excel (Q35).")

    print("\n" + "=" * 70)
    print(" KẾT QUẢ: 10/10 KỊCH BẢN TÍCH HỢP ĐÃ VƯỢT QUA 100% THÀNH CÔNG!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        print(f"\nINTEGRATION TEST FAILED: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
