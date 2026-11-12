# Đề xuất Hợp đồng API giữa các Module (`API_CONTRACT.md`)

> **Trạng thái tài liệu:** **BẢN ĐỀ XUẤT (DRAFT / PROPOSAL)** — Tài liệu này dùng để thống nhất giao tiếp giữa 6 thành viên trước khi tích hợp. Các chữ ký phương thức chỉ chính thức có hiệu lực sau khi các thành viên liên quan cùng rà soát và xác nhận.

---

## 1. Mục tiêu và nguyên tắc tích hợp

- **Phân tách tầng rõ ràng:** `main.py` → `cli/` (giao diện Console) → `services/` (nghiệp vụ) → `models/` (thực thể dữ liệu), kết hợp `storage/` (lưu trữ JSON / xuất CSV).
- **Không phụ thuộc ngược / không import vòng:**
  - `models/` không import `services/`, `storage/`, `cli/`.
  - `services/` import `models/`, không import `cli/`.
  - `storage/` import `models/` (để khôi phục đúng lớp đối tượng), không import `cli/`.
  - `cli/` chỉ import `services/` và `storage/` thông qua `AppContext` để điều phối, không chứa logic nghiệp vụ kho.

---

## 2. Sơ đồ phụ thuộc giữa các module

```text
main.py
  └── cli/menu.py (+ cli/input_helpers.py)
        ├── services/inventory_manager.py  ──▶ models/product.py
        ├── services/stock_service.py      ──▶ services/inventory_manager.py, models/stock_transaction.py
        ├── services/report_service.py     ──▶ services/inventory_manager.py, models/product.py, models/supplier.py
        └── storage/storage.py             ──▶ models/product.py
```

---

## 3. Quy ước kiểu dữ liệu cốt lõi cho `Product` (Thành viên 2 – Lâm)

| Thuộc tính | Kiểu dữ liệu đề xuất | Ràng buộc & Ghi chú |
| :--- | :--- | :--- |
| `product_id` (mã sản phẩm) | `str` | Không rỗng, tự động `.strip()`, nên chuẩn hóa chữ hoa hoặc so sánh nhất quán |
| `name` (tên sản phẩm) | `str` | Không rỗng sau khi `.strip()` |
| `price` (đơn giá) | `float` | `>= 0` (hoặc `> 0` theo quy ước nhóm); đơn vị VNĐ |
| `quantity` (số lượng tồn) | `int` | Số nguyên `>= 0` |
| `supplier_id` / `supplier` | `str` | Mã hoặc tên nhà cung cấp liên kết |
| `expiry_date` (`FoodProduct`) | `str` (định dạng ISO `YYYY-MM-DD`) hoặc `datetime.date` | Nên thống nhất dùng `YYYY-MM-DD` khi nhận từ Console & lưu JSON |
| `warranty_months` (`ElectronicProduct`) | `int` | Số tháng bảo hành `>= 0` |

### Các lớp và phương thức đề xuất trong `models/product.py`

1. **`Product`** (lớp cơ sở):
   - `__init__(self, product_id: str, name: str, price: float, quantity: int, supplier: str = "") -> None`
   - `@property` getter/setter cho `product_id`, `name`, `price`, `quantity`, `supplier`.
   - `is_valid(self) -> bool`: kiểm tra dữ liệu thực thể có hợp lệ không.
   - `get_inventory_value(self) -> float`: trả về `price * quantity`.
   - `__str__(self) -> str`: chuỗi hiển thị thông tin sản phẩm trên Console.
   - *(Đề xuất bổ sung cho `storage.py`)* `to_dict(self) -> dict[str, Any]` (có trường `"type": "Product"`).
2. **`FoodProduct(Product)`**:
   - Thêm thuộc tính `expiry_date`.
   - Ghi đè `is_valid()`, `get_inventory_value()` (nếu có quy tắc riêng) và `__str__()`.
   - `to_dict()` có `"type": "FoodProduct"`.
3. **`ElectronicProduct(Product)`**:
   - Thêm thuộc tính `warranty_months`.
   - Ghi đè `is_valid()`, `get_inventory_value()` và `__str__()`.
   - `to_dict()` có `"type": "ElectronicProduct"`.

---

## 4. Mô hình Nhà cung cấp & Giao dịch kho

### `models/supplier.py` – `Supplier` (Thành viên 5 – Minh)

- **Trách nhiệm:** Đại diện thông tin nhà cung cấp.
- **Thuộc tính đề xuất:** `supplier_id: str`, `name: str`, `phone: str`, `address: str`, `email: str = ""`.
- **Phương thức đề xuất:** `__init__(...)`, các `@property` có kiểm tra hợp lệ, `is_valid() -> bool`, `__str__() -> str`.

### `models/stock_transaction.py` – `StockTransaction` (Thành viên 4 – Chi)

- **Trách nhiệm:** Lưu thông tin một lần nhập kho hoặc xuất kho.
- **Thuộc tính đề xuất:**
  - `transaction_id: str`
  - `product_id: str`
  - `transaction_type: str` (`"IMPORT"` hoặc `"EXPORT"`)
  - `quantity: int` (`> 0`)
  - `timestamp: str` (ISO-8601)
  - `note: str = ""`
- **Phương thức đề xuất:** `__init__(...)`, các `@property` kiểm tra hợp lệ, `__str__() -> str`.

---

## 5. Hợp đồng tầng Service (`services/`)

### A. `InventoryManager` (`services/inventory_manager.py` – Thành viên 3: Sơn)

- **Cách lưu trữ đề xuất:** Lưu nội bộ bằng `dict[str, Product]` (key là `product_id`) hoặc `list[Product]` kèm kiểm tra duy nhất `product_id`. Dùng `dict[str, Product]` giúp tra cứu nhanh $O(1)$ theo mã và tránh trùng mã tự nhiên.
- **Phương thức đề xuất:**

| Phương thức | Tham số đầu vào | Kiểu trả về | Mô tả & Lỗi |
| :--- | :--- | :--- | :--- |
| `add_product` | `product: Product` | `None` (hoặc `bool`) | Ném `ValueError` nếu `product` không hợp lệ hoặc `product_id` đã tồn tại |
| `update_product` | `product_id: str, **fields` | `None` (hoặc `bool`) | Ném `KeyError` / `ValueError` nếu không tìm thấy mã hoặc dữ liệu mới sai |
| `delete_product` | `product_id: str` | `None` (hoặc `bool`) | Kiểm tra ràng buộc (ví dụ còn tồn kho hoặc có giao dịch liên quan nếu quy định) trước khi xóa; ném `ValueError`/`KeyError` nếu vi phạm |
| `get_product_by_id` | `product_id: str` | `Product \| None` | Phục vụ `StockService` và tìm kiếm theo mã |
| `get_all_products` | không có | `list[Product]` | Trả về danh sách sản phẩm (trả về `[]` nếu kho rỗng) |
| `search_product` | `keyword: str, by: str = "name"` | `list[Product]` | `by` thuộc `{"id", "name", "supplier"}`; trả về `[]` nếu không thấy hoặc kho rỗng |
| `sort_products` | `by: str = "price", reverse: bool = False` | `list[Product]` | `by` thuộc `{"price", "quantity"}`; `reverse=False` (tăng dần), `reverse=True` (giảm dần) |

---

### B. `StockService` (`services/stock_service.py` – Thành viên 4: Chi)

- **Cách truy cập và cập nhật tồn kho:**
  - `StockService.__init__(self, inventory_manager: InventoryManager)` nhận đối tượng `InventoryManager` từ bên ngoài (Dependency Injection).
  - Khi nhập/xuất, `StockService` gọi `inventory_manager.get_product_by_id(product_id)` để tìm sản phẩm, kiểm tra ràng buộc và cập nhật `product.quantity` thông qua setter/phương thức cập nhật hợp lệ, sau đó tạo và lưu `StockTransaction` vào danh sách lịch sử nội bộ `list[StockTransaction]`.
- **Phương thức đề xuất:**

| Phương thức | Tham số đầu vào | Kiểu trả về | Mô tả & Lỗi |
| :--- | :--- | :--- | :--- |
| `import_stock` | `product_id: str, quantity: int, note: str = ""` | `StockTransaction` | Kiểm tra `quantity > 0` (kiểu `int`), sản phẩm tồn tại; tăng tồn kho; ném `ValueError` nếu sai |
| `export_stock` | `product_id: str, quantity: int, note: str = ""` | `StockTransaction` | Kiểm tra `quantity > 0` và `quantity <= product.quantity`; giảm tồn kho; ném `ValueError` nếu vượt tồn |
| `get_transaction_history` | `product_id: str \| None = None` | `list[StockTransaction]` | Trả về toàn bộ lịch sử hoặc lọc theo `product_id` |

---

### C. `ReportService` (`services/report_service.py` – Thành viên 5: Minh)

- **Nguồn dữ liệu đầu vào:**
  - `ReportService.__init__(self, inventory_manager: InventoryManager, suppliers: list[Supplier] | None = None)` nhận `InventoryManager` để truy xuất `get_all_products()` và quản lý/nhận danh sách `Supplier`.
  - *(Ghi chú thống nhất)*: Nhóm cần xác nhận có tách `SupplierManager` riêng hay đặt CRUD `Supplier` trong `ReportService` / `InventoryManager`. Hiện tại Menu 2 đang tạm định hướng gắn với `ReportService` theo phân công của Minh.
- **Phương thức đề xuất:**

| Phương thức | Tham số đầu vào | Kiểu trả về | Mô tả |
| :--- | :--- | :--- | :--- |
| `get_total_inventory_value` | không có | `float` | Tổng `product.get_inventory_value()` của toàn kho |
| `get_low_stock_products` | `threshold: int = 5` | `list[Product]` | Sản phẩm có `quantity <= threshold` |
| `get_expiring_food_products` | `days: int = 7` | `list[FoodProduct]` | Thực phẩm còn hạn `<= days` ngày (hoặc đã hết hạn) |
| `check_food_expiry_status` | `product_id: str \| None = None` | `list[dict[str, Any]]` | Trả về trạng thái hạn sử dụng của thực phẩm |
| `get_warranty_summary` | `product_id: str \| None = None` | `list[dict[str, Any]]` | Thông tin thời hạn bảo hành thiết bị điện tử |
| `add_supplier` / `update_supplier` / `delete_supplier` / `get_all_suppliers` | theo thuộc tính `Supplier` | `None` / `list[Supplier]` | Quản lý danh sách nhà cung cấp |

---

## 6. Hợp đồng tầng Lưu trữ (`storage/storage.py` – Thành viên 6: Tú)

- **Cách nhận dữ liệu và khôi phục đối tượng:**
  - **Lưu JSON (`save_to_json(products: list[Product], file_path: str = "data/products.json") -> None`):** Chuyển từng đối tượng sang `dict` kèm trường phân loại `"type"` (`"Product"`, `"FoodProduct"`, `"ElectronicProduct"`), ghi file với `encoding="utf-8"`, `indent=2`, `ensure_ascii=False`.
  - **Đọc JSON (`load_from_json(file_path: str = "data/products.json") -> list[Product]`):** Đọc danh sách `dict`, dựa vào `"type"` để khởi tạo đúng lớp (`Product`, `FoodProduct`, `ElectronicProduct`). Nếu file chưa tồn tại thì trả về `[]` (hoặc thông báo rõ); nếu JSON hỏng thì ném `ValueError`.
  - **Xuất CSV (`export_to_csv(products: list[Product], file_path: str = "data/inventory_report.csv") -> None`):** Ghi header và từng dòng sản phẩm bằng thư viện `csv` (`encoding="utf-8-sig"` để mở tốt bằng Excel).

---

## 7. Quy tắc xử lý lỗi và luồng giao tiếp giữa Menu & Service

1. **Tầng Service** chịu trách nhiệm kiểm tra nghiệp vụ và ném exception chuẩn của Python (`ValueError`, `KeyError`, `TypeError`, `FileNotFoundError`) với thông báo rõ ràng bằng tiếng Việt.
2. **Tầng Menu (`cli/menu.py`)**:
   - Đọc chuỗi từ người dùng thông qua `cli/input_helpers.py`, kiểm tra định dạng cơ bản (không rỗng, đúng kiểu số nguyên/số thực khi cần).
   - Gọi phương thức tương ứng trên `AppContext` (`context.inventory_manager`, `context.stock_service`, `context.report_service`, `context.storage`).
   - Bọc lời gọi service trong khối `try ... except (ValueError, KeyError, OSError) as err:` để in thông báo lỗi thân thiện ra Console mà không làm sập chương trình.
3. **Nạp dữ liệu vào `AppContext` (`build_app_context()` trong `cli/menu.py`)**:
   - Khi các module sẵn sàng, `build_app_context()` sẽ khởi tạo:
     1. `inventory_manager = InventoryManager()`
     2. *(Tùy chọn)* nạp danh sách sản phẩm từ `storage.load_from_json(...)`
     3. `stock_service = StockService(inventory_manager)`
     4. `report_service = ReportService(inventory_manager)`
     5. Trả về `AppContext(inventory_manager=..., stock_service=..., report_service=..., storage=...)`.

---

## 8. Các điểm cần 5 thành viên xác nhận trước khi code tích hợp

1. Thống nhất định dạng ngày hạn sử dụng của `FoodProduct` (`YYYY-MM-DD` hay `DD/MM/YYYY`).
2. Thống nhất cơ chế sinh mã tự động hay nhập tay cho `product_id`, `supplier_id`, `transaction_id`.
3. Xác nhận `delete_product` kiểm tra ràng buộc liên quan dựa trên điều kiện nào (còn tồn kho > 0 hay đã phát sinh `StockTransaction`).
4. Xác nhận CRUD `Supplier` đặt trong `ReportService` hay tách riêng `SupplierService`.
5. Xác nhận tên lớp/hàm chính xác trong `storage/storage.py` (dạng class `InventoryStorage` hay hàm module `save_to_json` / `load_from_json` / `export_to_csv`).

