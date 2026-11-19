"""Module lưu trữ dữ liệu JSON và xuất báo cáo CSV (Design Baseline v1.0)."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Iterable

from models.product import ElectronicProduct, FoodProduct, Product
from models.stock_transaction import StockTransaction
from models.supplier import Supplier

DEFAULT_JSON_PATH = "data/inventory_data.json"
DEFAULT_CSV_PATH = "data/inventory_report.csv"

# Danh sách 7 cột chuẩn của file CSV theo Q35
CSV_COLUMNS = [
    "product_id",
    "name",
    "product_type",
    "price",
    "quantity",
    "inventory_value",
    "supplier",
]


def _serialize_item(item: Any) -> dict[str, Any]:
    """Chuyển đổi một đối tượng thành dictionary an toàn để lưu JSON."""
    if isinstance(item, dict):
        return dict(item)
    if hasattr(item, "to_dict") and callable(item.to_dict):
        return item.to_dict()
    raise TypeError(f"Không thể tuần tự hóa đối tượng kiểu {type(item).__name__}.")


def _deserialize_product(data: dict[str, Any]) -> Product:
    """Tái tạo đúng lớp sản phẩm từ dictionary (Q04)."""
    if not isinstance(data, dict):
        raise ValueError("Dữ liệu sản phẩm phải là một object/dict.")

    item_dict = dict(data)
    prod_type = item_dict.pop("type", "Product")

    # Đồng bộ trường supplier_id / supplier
    if "supplier_id" in item_dict:
        item_dict.setdefault("supplier", item_dict["supplier_id"])
    elif "supplier" in item_dict:
        item_dict["supplier_id"] = item_dict["supplier"]

    # Làm sạch các tham số phù hợp với từng constructor
    p_id = str(item_dict.get("product_id", "")).strip()
    name = str(item_dict.get("name", "")).strip()
    price = float(item_dict.get("price", 0.0))
    quantity = int(item_dict.get("quantity", 0))
    supplier_id = str(item_dict.get("supplier_id", "")).strip()

    if prod_type == "FoodProduct":
        exp = item_dict.get("expiry_date", "")
        return FoodProduct(
            product_id=p_id,
            name=name,
            price=price,
            quantity=quantity,
            supplier_id=supplier_id,
            expiry_date=exp,
        )
    elif prod_type == "ElectronicProduct":
        war = int(item_dict.get("warranty_months", 0))
        return ElectronicProduct(
            product_id=p_id,
            name=name,
            price=price,
            quantity=quantity,
            supplier_id=supplier_id,
            warranty_months=war,
        )
    elif prod_type == "Product":
        return Product(
            product_id=p_id,
            name=name,
            price=price,
            quantity=quantity,
            supplier_id=supplier_id,
        )
    else:
        raise ValueError(f"Loại sản phẩm không được hỗ trợ trong JSON: {prod_type}")


def _deserialize_supplier(data: dict[str, Any]) -> Supplier:
    """Tái tạo đối tượng Supplier từ dictionary."""
    if not isinstance(data, dict):
        raise ValueError("Dữ liệu nhà cung cấp phải là một object/dict.")
    return Supplier(
        supplier_id=str(data.get("supplier_id", "")).strip(),
        name=str(data.get("name", "")).strip(),
        phone=str(data.get("phone", "")).strip(),
        address=str(data.get("address", "")).strip(),
        email=str(data.get("email", "")).strip(),
    )


def _deserialize_transaction(data: dict[str, Any]) -> StockTransaction:
    """Tái tạo đối tượng StockTransaction từ dictionary."""
    if not isinstance(data, dict):
        raise ValueError("Dữ liệu giao dịch phải là một object/dict.")
    return StockTransaction(
        transaction_id=str(data.get("transaction_id", "")).strip(),
        product_id=str(data.get("product_id", "")).strip(),
        transaction_type=str(data.get("transaction_type", "IMPORT")).strip(),
        quantity=int(data.get("quantity", 1)),
        timestamp=str(data.get("timestamp", "")).strip(),
        note=str(data.get("note", "")).strip(),
    )


def save_to_json(
    data: dict[str, Any] | Iterable[Any],
    file_path: str | Path = DEFAULT_JSON_PATH,
) -> bool:
    """Lưu toàn bộ 3 nhóm dữ liệu (products, suppliers, transactions) ra file JSON an toàn (Q05, Q33, Q34).

    Cơ chế ghi file nguyên tử (Atomic Write):
    1. Ghi dữ liệu đầy đủ ra tệp tạm (.tmp).
    2. Sử dụng os.replace để tráo đổi tệp tạm sang tệp đích, chống hỏng dữ liệu khi mất điện/crash.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")

    # Chuẩn hóa cấu trúc 3 nhóm thực thể
    if isinstance(data, dict):
        prods = [_serialize_item(p) for p in data.get("products", [])]
        sups = [_serialize_item(s) for s in data.get("suppliers", [])]
        txs = [_serialize_item(t) for t in data.get("transactions", [])]
        payload: dict[str, Any] = {
            "products": prods,
            "suppliers": sups,
            "transactions": txs,
        }
    else:
        # Hỗ trợ tương thích ngược nếu truyền trực tiếp list sản phẩm
        payload = {
            "products": [_serialize_item(p) for p in data],
            "suppliers": [],
            "transactions": [],
        }

    try:
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())

        # Tráo đổi nguyên tử (Atomic replace - Q34)
        os.replace(tmp_path, path)
        return True
    except Exception as exc:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise OSError(f"Không thể lưu dữ liệu vào tệp JSON {file_path}: {exc}") from exc


def load_from_json(
    file_path: str | Path = DEFAULT_JSON_PATH,
) -> dict[str, Any]:
    """Nạp dữ liệu từ file JSON và khôi phục đúng các đối tượng thực thể (Q34).

    Returns:
        dict gồm {"products": list[Product], "suppliers": list[Supplier], "transactions": list[StockTransaction]}
    """
    path = Path(file_path)
    if not path.exists():
        return {"products": [], "suppliers": [], "transactions": []}

    try:
        with path.open("r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as exc:
        raise OSError(f"Không thể đọc tệp JSON {file_path}: {exc}") from exc

    if not raw.strip():
        return {"products": [], "suppliers": [], "transactions": []}

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Tệp JSON bị hỏng hoặc sai cú pháp ({file_path}): {exc}") from exc

    # Xử lý cả dạng dict chuẩn 3 nhóm lẫn dạng list cũ
    if isinstance(data, dict):
        raw_prods = data.get("products", [])
        raw_sups = data.get("suppliers", [])
        raw_txs = data.get("transactions", [])
    elif isinstance(data, list):
        raw_prods = data
        raw_sups = []
        raw_txs = []
    else:
        raise ValueError("Dữ liệu JSON gốc phải là một object chứa các nhóm thực thể.")

    # Khôi phục các đối tượng
    products = [_deserialize_product(item) for item in raw_prods]
    suppliers = [_deserialize_supplier(item) for item in raw_sups]
    transactions = [_deserialize_transaction(item) for item in raw_txs]

    return {
        "products": products,
        "suppliers": suppliers,
        "transactions": transactions,
    }


def export_to_csv(
    products: Iterable[Product],
    file_path: str | Path = DEFAULT_CSV_PATH,
) -> None:
    """Xuất danh sách sản phẩm trong kho ra file CSV gồm đúng 7 cột chuẩn (Q35).

    Encoding utf-8-sig để hỗ trợ hiển thị tiếng Việt hoàn hảo khi mở trên Microsoft Excel.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for p in products:
        if isinstance(p, Product):
            rows.append({
                "product_id": p.product_id,
                "name": p.name,
                "product_type": type(p).__name__,
                "price": f"{p.price:.2f}",
                "quantity": p.quantity,
                "inventory_value": f"{p.get_inventory_value():.2f}",
                "supplier": getattr(p, "supplier_id", "") or getattr(p, "supplier", ""),
            })

    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
