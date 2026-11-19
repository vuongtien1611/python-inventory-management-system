"""Lưu và khôi phục sản phẩm JSON, xuất danh sách kho thành CSV."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable


DEFAULT_JSON_PATH = Path("data/products.json")
DEFAULT_CSV_PATH = Path("data/inventory_report.csv")
_COMMON_FIELDS = ("product_id", "name", "price", "quantity", "supplier")
_SUBTYPE_FIELDS = {
    "FoodProduct": ("expiry_date",),
    "ElectronicProduct": ("warranty_months",),
}


def _product_types() -> dict[str, type]:
    """Import trễ để storage vẫn dùng được trong lúc model đang được tích hợp."""
    from models.product import ElectronicProduct, FoodProduct, Product

    return {"Product": Product, "FoodProduct": FoodProduct, "ElectronicProduct": ElectronicProduct}


def _product_to_dict(product: Any) -> dict[str, Any]:
    if isinstance(product, dict):
        data = dict(product)
        data.setdefault("type", "Product")
        return data
    serializer = getattr(product, "to_dict", None)
    if callable(serializer):
        data = dict(serializer())
        data.setdefault("type", type(product).__name__)
        return data

    types = _product_types()
    kind = next((name for name, product_class in types.items() if type(product) is product_class), None)
    if kind is None:
        kind = next((name for name, product_class in types.items() if isinstance(product, product_class)), type(product).__name__)
    if kind not in {"Product", *_SUBTYPE_FIELDS}:
        raise TypeError(f"Loại sản phẩm không được hỗ trợ: {kind}")
    data = {"type": kind}
    for field in (*_COMMON_FIELDS, *_SUBTYPE_FIELDS.get(kind, ())):
        if hasattr(product, field):
            data[field] = getattr(product, field)
    missing = [field for field in _COMMON_FIELDS if field not in data]
    if missing:
        raise ValueError(f"Thiếu thuộc tính sản phẩm: {', '.join(missing)}")
    return data


def _product_from_dict(data: dict[str, Any]) -> Any:
    if not isinstance(data, dict):
        raise ValueError("Mỗi sản phẩm trong JSON phải là một object.")
    kind = data.get("type", "Product")
    product_class = _product_types().get(kind)
    if product_class is None:
        raise ValueError(f"Loại sản phẩm không được hỗ trợ: {kind}")
    fields = {key: value for key, value in data.items() if key != "type"}
    try:
        return product_class(**fields)
    except TypeError as exc:
        raise ValueError(f"Dữ liệu không phù hợp với {kind}: {exc}") from exc


def save_to_json(products: Iterable[Any], file_path: str | Path = DEFAULT_JSON_PATH) -> None:
    """Ghi danh sách sản phẩm JSON UTF-8; tự tạo thư mục cha nếu cần."""
    path = Path(file_path)
    try:
        payload = [_product_to_dict(product) for product in products]
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
    except OSError:
        raise


def load_from_json(file_path: str | Path = DEFAULT_JSON_PATH) -> list[Any]:
    """Đọc JSON. File chưa có hoặc rỗng được xem là kho mới; JSON lỗi báo ValueError."""
    path = Path(file_path)
    try:
        with path.open("r", encoding="utf-8") as stream:
            raw = stream.read()
    except FileNotFoundError:
        return []
    if not raw.strip():
        return []
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Tệp JSON không hợp lệ: {path}") from exc
    if not isinstance(payload, list):
        raise ValueError("Dữ liệu JSON phải là một danh sách sản phẩm.")
    return [_product_from_dict(item) for item in payload]


def export_to_csv(products: Iterable[Any], file_path: str | Path = DEFAULT_CSV_PATH) -> None:
    """Xuất danh sách sản phẩm ra CSV UTF-8-SIG, tương thích Excel."""
    path = Path(file_path)
    rows = [_product_to_dict(product) for product in products]
    fields = list(dict.fromkeys(("type", *_COMMON_FIELDS, "expiry_date", "warranty_months")))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
