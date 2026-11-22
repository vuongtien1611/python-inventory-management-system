"""Exercise the product -> stock -> JSON/CSV workflow against real project APIs.

Run from the project root with ``python run_integration_tests.py``. This is an
integration runner, not a fixture-based test: it intentionally refuses to
report success while the model/service modules are still TODO stubs.
"""

from __future__ import annotations

import csv
import json
import sys
import tempfile
from pathlib import Path

# Windows terminals can default to a legacy code page that cannot print the
# Vietnamese status messages below. Prefer UTF-8 when the stream supports it.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def require_apis():
    try:
        from models.product import Product
        from services.inventory_manager import InventoryManager
        from services.stock_service import StockService
        from storage.storage import export_to_csv, load_from_json, save_to_json
    except ImportError as exc:
        raise RuntimeError(
            "Chưa thể chạy test tích hợp: cần Product, InventoryManager và "
            "StockService được triển khai theo docs/API_CONTRACT.md."
        ) from exc
    required = ("add_product", "get_product_by_id")
    missing = [name for name in required if not callable(getattr(InventoryManager, name, None))]
    missing += [name for name in ("import_stock", "export_stock") if not callable(getattr(StockService, name, None))]
    if missing:
        raise RuntimeError("Chưa thể chạy test tích hợp; API còn thiếu: " + ", ".join(missing))
    return Product, InventoryManager, StockService, save_to_json, load_from_json, export_to_csv


def run() -> None:
    Product, InventoryManager, StockService, save_to_json, load_from_json, export_to_csv = require_apis()
    with tempfile.TemporaryDirectory(prefix="inventory-integration-") as temp:
        json_path = Path(temp) / "data" / "products.json"
        csv_path = Path(temp) / "reports" / "inventory.csv"

        inventory = InventoryManager()
        product = Product("IT-001", "Sản phẩm kiểm thử", 125_000, 3, "NCC-DEMO")
        inventory.add_product(product)
        assert inventory.get_product_by_id("IT-001") is product
        print("PASS: tạo và đăng ký sản phẩm")

        stock = StockService(inventory)
        stock.import_stock("IT-001", 5, "Tích hợp test")
        assert product.quantity == 8, f"Tồn sau nhập phải là 8, nhận {product.quantity}"
        stock.export_stock("IT-001", 2, "Tích hợp test")
        assert product.quantity == 6, f"Tồn sau xuất phải là 6, nhận {product.quantity}"
        print("PASS: nhập 5, xuất 2; tồn kho còn 6")

        history = stock.get_transaction_history(product_id="IT-001")
        assert len(history) == 2, f"Cần 2 giao dịch, nhận {len(history)}"
        print("PASS: lịch sử giao dịch có 2 bản ghi")

        products = inventory.get_all_products()
        save_to_json(products, json_path)
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        assert len(payload) == 1 and payload[0]["product_id"] == "IT-001"
        restored = load_from_json(json_path)
        assert len(restored) == 1 and restored[0].quantity == 6
        print("PASS: lưu và nạp lại JSON")

        export_to_csv(products, csv_path)
        with csv_path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == 1 and rows[0]["product_id"] == "IT-001"
        print("PASS: CSV có header và 1 sản phẩm")

        try:
            stock.export_stock("IT-001", 7, "Phải bị từ chối")
        except ValueError:
            assert product.quantity == 6, "Tồn kho thay đổi sau giao dịch bị từ chối"
        else:
            raise AssertionError("Xuất vượt tồn kho phải ném ValueError")
        print("PASS: từ chối xuất vượt tồn, không đổi số lượng")

    print("\nTất cả kịch bản tích hợp đều PASS.")


if __name__ == "__main__":
    try:
        run()
    except (AssertionError, RuntimeError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"INTEGRATION TEST BLOCKED/FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
