# KẾ HOẠCH KHẮC PHỤC VÀ HOÀN THIỆN KỸ THUẬT (RECOVERY & EXECUTION PLAN)
**Dự án:** Product Inventory Management System  
**Ngày lập kế hoạch:** 19/11/2026  
**Căn cứ kiểm toán:** Báo cáo [TEAM_BRANCH_CODE_AUDIT_2026-11-19.md](TEAM_BRANCH_CODE_AUDIT_2026-11-19.md)  
**Tiêu chuẩn thiết kế bắt buộc:** Design Baseline v1.0 (40 Quyết định phê duyệt – API Contract v1.0 & UML Design v1.0)  
**Hạn chót nghiệm thu toàn bộ:** 25/11/2026 (Còn 6 ngày)  
**Nguyên tắc thực thi:**  
1. Không làm thay phần việc của các thành viên.  
2. Không reset lịch sử Git trên `main`, bảo toàn mã và bộ test có giá trị.  
3. Phân rã công việc rõ ràng: Tệp, phương thức, lỗi BUG, tiêu chí nghiệm thu và mức ưu tiên.  
4. Kiểm thử nghiêm ngặt trước khi hòa trộn (merge) từng nhánh.

---

## 1. PHÂN CÔNG CÔNG VIỆC CHI TIẾT CHO 6 THÀNH VIÊN

### 1.1. Thành viên 3: SƠN (`feature/product-management`)
> **Đánh giá hiện trạng:** 0% (NOT STARTED). Đây là nút thắt cổ chai **P0** nguy cấp nhất của toàn dự án.

| Thuộc tính | Chi tiết phân công |
| :--- | :--- |
| **Tệp chịu trách nhiệm** | `services/inventory_manager.py` |
| **Lỗi liên quan** | **BUG-01** (Module rỗng, chưa cài đặt `InventoryManager`) |
| **Mức ưu tiên** | **P0 (Khẩn cấp tuyệt đối – Phải xong trước 20/11/2026)** |
| **Các phương thức cần viết** | 1. `__init__(self) -> None`: Khởi tạo từ điển nội bộ `_products: dict[str, Product] = {}`.<br>2. `add_product(self, product: Product, supplier_service: SupplierService | None = None) -> None`: Kiểm tra `product.is_valid()`, kiểm tra trùng mã `product_id` (ném `ValueError` theo Q06), kiểm tra `supplier_id` hợp lệ qua `supplier_service.has_supplier(product.supplier_id)` nếu có truyền service (ném `ValueError` theo Q14).<br>3. `update_product(self, product_id: str, **fields) -> None`: Kiểm tra tồn tại mã (ném `KeyError` theo Q18). **Tuyệt đối cấm sửa `quantity`** (ném `ValueError` nếu `"quantity"` có trong `fields` theo Q08). Cập nhật an toàn `name`, `price`, `supplier_id`, `expiry_date`, `warranty_months`.<br>4. `delete_product(self, product_id: str, stock_service: StockService | None = None) -> None`: Ném `KeyError` nếu không tìm thấy. Ném `ValueError` nếu `product.quantity > 0` (theo Q19). Nếu có truyền `stock_service`, gọi `stock_service.has_product_transactions(product_id)`: ném `ValueError` nếu đã có lịch sử giao dịch (theo Q20).<br>5. `get_product_by_id(self, product_id: str) -> Product`: **Ném `KeyError` nếu không thấy** (theo Q18, không được trả về `None`).<br>6. `get_all_products(self) -> list[Product]`: Trả về bản sao danh sách tất cả sản phẩm (`list(self._products.values())`).<br>7. `search_product(self, keyword: str, by: str = "name") -> list[Product]`: Tìm kiếm theo `"id"`, `"name"`, `"supplier"`. So sánh không phân biệt hoa/thường, giữ nguyên dấu tiếng Việt theo Q21.<br>8. `sort_products(self, by: str = "price", reverse: bool = False) -> list[Product]`: Sắp xếp theo `"price"` hoặc `"quantity"`, hỗ trợ tăng/giảm dần theo Q22. |
| **Tiêu chí nghiệm thu (DoD)** | - Toàn bộ 8 phương thức được cài đặt đầy đủ theo chuẩn kiểu dữ liệu Python 3.11+.<br>- Chống trùng mã `product_id` 100%.<br>- Cấm sửa `quantity` qua `update_product` 100%.<br>- `delete_product` chặn xóa khi tồn kho > 0 hoặc đã có giao dịch.<br>- Vượt qua toàn bộ unit test trong `tests/test_inventory.py`. |

---

### 1.2. Thành viên 2: LÂM (`feature/product-models`)
> **Đánh giá hiện trạng:** 68% (PARTIAL). Thiếu đóng gói tồn kho và phương thức nghiệp vụ.

| Thuộc tính | Chi tiết phân công |
| :--- | :--- |
| **Tệp chịu trách nhiệm** | `models/product.py` |
| **Lỗi liên quan** | **BUG-07** (Hở `@quantity.setter`, thiếu `increase_stock`/`decrease_stock`, lệch tên `supplier_id`) |
| **Mức ưu tiên** | **P1 (Cao – Cần xong trước 20/11/2026)** |
| **Các phương thức cần sửa/viết** | 1. **Đóng gói tồn kho (Q08):** Xóa bỏ hoàn toàn `@quantity.setter`. Thuộc tính `quantity` chỉ có `@property quantity(self) -> int` trả về `self._quantity` (chỉ đọc).<br>2. `increase_stock(self, amount: int) -> None`: Kiểm tra `isinstance(amount, int) and not isinstance(amount, bool) and amount > 0` (ném `ValueError` nếu vi phạm). Tăng `self._quantity += amount`.<br>3. `decrease_stock(self, amount: int) -> None`: Kiểm tra `isinstance(amount, int) and not isinstance(amount, bool) and amount > 0`. Kiểm tra `amount <= self._quantity` (ném `ValueError` nếu xuất vượt tồn, không cho tồn kho âm). Giảm `self._quantity -= amount`.<br>4. **Đổi tên thuộc tính:** Đổi `supplier` thành `supplier_id` (biến lưu trữ `_supplier_id`).<br>5. **Bổ sung nghiệp vụ `FoodProduct`:**<br>   - Thêm phương thức `days_until_expiry(self, current_date: date | None = None) -> int`: tính số ngày còn lại đến hạn sử dụng.<br>   - Sửa `is_expired(self, current_date: date | None = None) -> bool`: nhận tham số ngày tùy chọn, mặc định là hôm nay.<br>6. **Chuẩn hóa chữ ký khởi tạo `__init__`:**<br>   - `Product(product_id, name, price, quantity=0, supplier_id="")`<br>   - `FoodProduct(product_id, name, price, quantity=0, supplier_id="", expiry_date="")`<br>   - `ElectronicProduct(product_id, name, price, quantity=0, supplier_id="", warranty_months=0)` |
| **Tiêu chí nghiệm thu (DoD)** | - Không còn `@quantity.setter` (gán `p.quantity = 10` sẽ báo lỗi `AttributeError`).<br>- `increase_stock` và `decrease_stock` hoạt động chính xác, từ chối `bool` (`True/False`) và số âm.<br>- Khởi tạo đúng thứ tự tham số API Contract.<br>- Vượt qua `tests/test_product.py`. |

---

### 1.3. Thành viên 5: MINH (`feature/supplier-reports`)
> **Đánh giá hiện trạng:** 70% (MOSTLY COMPLETE). Cần tách module `SupplierService`, thêm `to_dict()`, và giải quyết xung đột PR #3.

| Thuộc tính | Chi tiết phân công |
| :--- | :--- |
| **Tệp chịu trách nhiệm** | `models/supplier.py`, `services/supplier_service.py` (tạo mới), `services/report_service.py` |
| **Lỗi liên quan** | **BUG-02** (Thiếu module `SupplierService`), **BUG-03** (Xung đột PR #3), **BUG-08** (Thiếu `Supplier.to_dict`) |
| **Mức ưu tiên** | **P1 (Cao – Cần xong trước 21/11/2026)** |
| **Các phương thức cần sửa/viết** | 1. **Bổ sung `Supplier.to_dict()` trong `models/supplier.py`:** Trả về dictionary gồm `supplier_id`, `name`, `phone`, `address`, `email`.<br>2. **Tạo mới `services/supplier_service.py` (Q16):**<br>   - Chuyển toàn bộ các phương thức CRUD nhà cung cấp từ `ReportService` sang lớp `SupplierService`:<br>     • `__init__(self) -> None`: khởi tạo `_suppliers: dict[str, Supplier] = {}`.<br>     • `add_supplier(self, supplier: Supplier) -> None`: kiểm tra `supplier.is_valid()`, chống trùng mã (theo Q16).<br>     • `update_supplier(self, supplier_id: str, **fields) -> None`: cập nhật `name`, `phone`, `address`, `email`.<br>     • `delete_supplier(self, supplier_id: str, inventory_manager: InventoryManager | None = None) -> None`: ném `KeyError` nếu không tìm thấy. Nếu có truyền `inventory_manager`, kiểm tra xem có bất kỳ sản phẩm nào có `p.supplier_id == supplier_id`, nếu có ném `ValueError` (cấm xóa theo Q15).<br>     • `get_supplier_by_id(self, supplier_id: str) -> Supplier`: ném `KeyError` nếu không thấy.<br>     • `get_all_suppliers(self) -> list[Supplier]`<br>     • `has_supplier(self, supplier_id: str) -> bool`: trả về `True/False`.<br>3. **Tinh chỉnh `services/report_service.py`:**<br>   - Xóa bỏ các phương thức CRUD nhà cung cấp, giữ `ReportService` thuần túy làm nhiệm vụ truy vấn/báo cáo.<br>   - Sửa `get_total_inventory_value(self) -> dict`: tính tổng giá trị hàng tồn và thống kê giá trị thực phẩm hết hạn theo Q32.<br>4. **Giải quyết xung đột Git trên PR #3:** Thực hiện rebase với `origin/main` (xem Mục 3). |
| **Tiêu chí nghiệm thu (DoD)** | - Tồn tại độc lập `services/supplier_service.py` có đầy đủ 7 phương thức CRUD.<br>- `Supplier` có `to_dict()`.<br>- `ReportService` chỉ thuần túy thống kê.<br>- PR #3 chuyển sang trạng thái `mergeable: true`. |

---

### 1.4. Thành viên 4: CHI (`feature/stock-transactions`)
> **Đánh giá hiện trạng:** 48% (PARTIAL). Cần sửa chữ ký hàm, thêm atomic rollback, chặn bool và bổ sung `has_product_transactions`.

| Thuộc tính | Chi tiết phân công |
| :--- | :--- |
| **Tệp chịu trách nhiệm** | `models/stock_transaction.py`, `services/stock_service.py` |
| **Lỗi liên quan** | **BUG-05** (Lệch chữ ký API, thiếu UUID tự động), **BUG-06** (Lỗ hổng boolean) |
| **Mức ưu tiên** | **P1 (Cao – Cần xong trước 21/11/2026)** |
| **Các phương thức cần sửa/viết** | 1. **Đóng gói `models/stock_transaction.py`:**<br>   - Đóng gói thuộc tính `_transaction_id`, `_product_id`, `_transaction_type`, `_quantity`, `_timestamp`, `_note` thành `@property` chỉ đọc (bất biến theo Q28).<br>   - `timestamp` lưu theo ISO 8601 có múi giờ (Q26): `datetime.now().astimezone().isoformat()`.<br>2. **Sửa chữ ký `services/stock_service.py`:**<br>   - `import_stock(self, product_id: str, quantity: int, note: str = "") -> StockTransaction`: **Tự sinh `transaction_id = str(uuid.uuid4())` bên trong** (theo Q25), không bắt người gọi truyền ID.<br>   - `export_stock(self, product_id: str, quantity: int, note: str = "") -> StockTransaction`: Tương tự, tự sinh UUID4.<br>3. **Sửa lỗi kiểu dữ liệu (Q23):** Kiểm tra `if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0: raise ValueError(...)`.<br>4. **Tích hợp kiểm tra thực phẩm hết hạn (Q10):** Trong `import_stock`, lấy sản phẩm qua `inventory_manager.get_product_by_id(product_id)`. Nếu `isinstance(product, FoodProduct)` và `product.is_expired() == True`, từ chối nhập và ném `ValueError`.<br>5. **Tương tác đúng với Model & Atomic Rollback (Q27):**<br>   - Nhập kho: gọi `product.increase_stock(quantity)`. Nếu việc tạo `StockTransaction` hoặc lưu vào danh sách lỗi, gọi `product.decrease_stock(quantity)` để hoàn tác.<br>   - Xuất kho: gọi `product.decrease_stock(quantity)`. Nếu lưu giao dịch lỗi, gọi `product.increase_stock(quantity)` để hoàn tác.<br>6. **Bổ sung phương thức:** `has_product_transactions(self, product_id: str) -> bool`: trả về `True` nếu đã có ít nhất một giao dịch của sản phẩm (hỗ trợ Q20 cho Sơn).<br>7. **Dọn dẹp code:** Xóa bỏ toàn bộ các lệnh `print()` trong service. |
| **Tiêu chí nghiệm thu (DoD)** | - Chữ ký không còn tham số `transaction_id`.<br>- Tự sinh mã UUID4 chuẩn xác.<br>- Chặn thành công `True/False` khi truyền vào `quantity`.<br>- Từ chối nhập thực phẩm hết hạn.<br>- Rollback hoạt động hoàn hảo khi có lỗi.<br>- Vượt qua `tests/test_stock.py`. |

---

### 1.5. Thành viên 6: TÚ (`feature/storage-testing`)
> **Đánh giá hiện trạng:** 58% (PARTIAL). Lưu trữ thiếu 2 thực thể, cần dọn dẹp các tệp stub đã merge vào `main`.

| Thuộc tính | Chi tiết phân công |
| :--- | :--- |
| **Tệp chịu trách nhiệm** | `storage/storage.py`, `tests/` |
| **Lỗi liên quan** | **BUG-04** (Lưu trữ thiếu `suppliers` và `transactions`, ghi file không nguyên tử) |
| **Mức ưu tiên** | **P1 (Cao – Cần xong trước 22/11/2026)** |
| **Các phương thức cần sửa/viết** | 1. **Chuẩn hóa `save_to_json` trong `storage/storage.py`:**<br>   - Chữ ký: `save_to_json(data: dict[str, Any], file_path: str = "data/inventory_data.json") -> bool`.<br>   - Lưu đầy đủ cả 3 nhóm: `data["products"]`, `data["suppliers"]`, `data["transactions"]` (theo Q05, Q33).<br>   - Cơ chế ghi file nguyên tử (Q34): Ghi dữ liệu ra tệp tạm `data/inventory_data.json.tmp`, sau đó dùng `os.replace` để tráo đổi an toàn, chống hỏng file khi mất điện.<br>2. **Chuẩn hóa `load_from_json`:**<br>   - Chữ ký: `load_from_json(file_path: str = "data/inventory_data.json") -> dict[str, Any]`.<br>   - Khôi phục chính xác các lớp cụ thể: `Product`, `FoodProduct`, `ElectronicProduct`, `Supplier`, `StockTransaction`.<br>   - Nếu file rỗng/chưa có, trả về `{"products": [], "suppliers": [], "transactions": []}`.<br>   - Nếu JSON hỏng cấu trúc, ném `ValueError` và không làm thay đổi bộ nhớ (Q34).<br>3. **Chuẩn hóa `export_to_csv` (Q35):**<br>   - Chữ ký: `export_to_csv(products: list[Product], file_path: str = "data/inventory_report.csv") -> None`.<br>   - Xuất đúng **7 cột**: `product_id, name, product_type, price, quantity, inventory_value, supplier` với encoding `utf-8-sig`.<br>4. **Cập nhật bộ kiểm thử `tests/`:**<br>   - Cập nhật các bài test trong `tests/test_inventory.py` để kiểm tra việc `update_product` **từ chối sửa `quantity`** (hiện tại test của Tú đang cho phép sửa `quantity`).<br>   - Bổ sung test serialize/deserialize cả 3 thực thể trong `test_inventory.py`. |
| **Tiêu chí nghiệm thu (DoD)** | - JSON lưu và nạp đủ 3 nhóm thực thể.<br>- Ghi file an toàn qua file tạm và `os.replace`.<br>- CSV xuất đúng 7 cột mở được trên Excel.<br>- Bộ unit test kiểm thử các quy tắc nghiệp vụ thật, không kiểm thử stub. |

---

### 1.6. Thành viên 1: TIẾN (`feature/main-menu`)
> **Đánh giá hiện trạng:** 90% (MOSTLY COMPLETE). Sẵn sàng tích hợp khi các service hoàn thiện.

| Thuộc tính | Chi tiết phân công |
| :--- | :--- |
| **Tệp chịu trách nhiệm** | `main.py`, `cli/menu.py`, `cli/input_helpers.py`, `docs/*` |
| **Mức ưu tiên** | **P1 (Tiến hành tích hợp từ 22/11 – 23/11/2026)** |
| **Nhiệm vụ cụ thể** | 1. **Bảo tồn hồ sơ thiết kế:** Chuyển giao các tệp tài liệu v1.0 đã hoàn thiện (`docs/API_CONTRACT.md`, `docs/TASK_ASSIGNMENT.md`, `docs/uml/*`) vào nhánh `main`.<br>2. **Đấu nối `AppContext` trong `cli/menu.py`:**<br>   - Khi các nhánh dịch vụ được merge vào `main`, thay thế bản mock/stub của Tú bằng việc khởi tạo các service chuẩn:<br>     ```python
context = AppContext(
    inventory_manager=InventoryManager(),
    supplier_service=SupplierService(),
    stock_service=StockService(inventory_manager),
    report_service=ReportService(inventory_manager),
    storage=storage_module
)
```<br>3. **Đấu nối các Menu CLI:** Nối các menu con với đúng các phương thức dịch vụ thật của Sơn, Minh, Chi, Tú.<br>4. **Kiểm tra luồng thoát và tự động lưu:** Xác nhận quy trình thoát gọi `save_to_json` và hỗ trợ 3 lựa chọn khi lỗi (Thử lưu lại, Hủy thoát, Thoát không lưu).<br>5. **Chạy toàn bộ test suite và smoke test:** Đảm bảo `python main.py` chạy mượt mà trên Console. |
| **Tiêu chí nghiệm thu (DoD)** | - Toàn bộ 8 menu Console hoạt động trơn tru.<br>- Không crash khi nhập sai hoặc dữ liệu rỗng.<br>- Tự động lưu JSON 3 thực thể khi thoát.<br>- Chạy `python3 -m unittest discover -s tests -v` đạt 100% PASS. |

---

## 2. MA TRẬN PHỤ THUỘC VÀ KHẢ NĂNG TRIỂN KHAI SONG SONG

Nhằm tối ưu hóa thời gian (còn 6 ngày), các thành viên cần biết rõ phần nào có thể làm độc lập và phần nào phải chờ nhau:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   GIAI ĐOẠN 1: TRIỂN KHAI SONG SONG (20/11)             │
│                                                                        │
│  [Lâm] models/product.py          [Minh] models/supplier.py            │
│  (Thêm increase/decrease_stock,   (Thêm to_dict)                       │
│   bỏ quantity setter)                    │                             │
│         │                                ▼                             │
│         │                         [Minh] services/supplier_service.py  │
│         │                         (Tạo mới SupplierService)            │
│         ▼                                │                             │
│  [Sơn] services/inventory_manager.py ◄───┘                             │
│  (Nhận Product của Lâm và SupplierService của Minh)                    │
│                                                                        │
│  [Chi] models/stock_transaction.py                                     │
│  (Đóng gói @property, timestamp ISO)                                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                   GIAI ĐOẠN 2: GHÉP NỐI DỊCH VỤ (21/11)                │
│                                                                        │
│  [Chi] services/stock_service.py                                       │
│  (Phụ thuộc: InventoryManager của Sơn + Product của Lâm)               │
│                                                                        │
│  [Minh] services/report_service.py                                     │
│  (Phụ thuộc: InventoryManager của Sơn)                                 │
│                                                                        │
│  [Tú] storage/storage.py                                               │
│  (Phụ thuộc: to_dict() của Product, Supplier, StockTransaction)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                   GIAI ĐOẠN 3: TÍCH HỢP & TEST (22/11 - 23/11)         │
│                                                                        │
│  [Tú] tests/ (Cập nhật unit tests cho 3 thực thể, xóa test stub)       │
│  [Tiến] cli/menu.py (Đấu nối AppContext và 8 menu Console)             │
│  [Cả nhóm] Chạy toàn bộ 60+ Test Cases & Smoke Test Console            │
└────────────────────────────────────────────────────────────────────────┘
```

- **Lâm và Minh có thể làm độc lập ngay lập tức** vì tầng `models/` không phụ thuộc vào ai.
- **Sơn cần giao diện của `Product` và `SupplierService`** để viết `add_product` và `delete_product`. Vì hợp đồng đã có trong `API_CONTRACT.md`, Sơn có thể viết code ngay dựa trên hợp đồng mà không cần chờ Lâm/Minh merge.
- **Chi cần `increase_stock`/`decrease_stock` của Lâm** và `get_product_by_id` của Sơn.
- **Tú cần định dạng `to_dict()` của cả 3 model** để hoàn thiện `save_to_json`.

---

## 3. PHƯƠNG ÁN KHẮC PHỤC HẬU QUẢ PR #4 VÀ XỬ LÝ CONFLICT PR #3

### 3.1. Phương án khắc phục hậu quả PR #4 trên `main`
- **Nguyên tắc:** **KHÔNG dùng `git reset --hard` hoặc `git push --force` trên `main`** để tránh phá vỡ commit tree của các thành viên khác.
- **Giải pháp xử lý:**
  1. **Bảo tồn các thành phần có giá trị từ PR #4:**
     - Giữ nguyên bộ khung kiểm thử và tài liệu thuyết trình: `create_demo_deck.py`, `docs/DEMO_SLIDES.md`, `docs/INTEGRATION_TEST_PLAN.md`, `docs/presentations/`.
     - Giữ nguyên cấu trúc các tệp test trong `tests/` và bộ chạy `run_integration_tests.py`.
  2. **Thay thế dần các stub bằng code thật:**
     - Các tệp stub dở dang mà Tú đã đưa vào `main` (`models/product.py`, `services/inventory_manager.py`, `services/stock_service.py`, `services/report_service.py`, `cli/menu.py`) sẽ được **ghi đè hợp lệ bằng chính code thật chuẩn hóa** của từng thành viên tương ứng thông qua các PR tiếp theo.
     - Khi hòa trộn code chuẩn của Lâm, Sơn, Minh, Chi, Tiến vào `main`, code thật sẽ tự động thay thế hoàn toàn các đoạn stub tạm thời.

### 3.2. Phương án giải quyết xung đột hòa trộn (Conflict) cho PR #3 của Minh
PR #3 của Minh hiện tại bị `mergeable: false` do xung đột tệp `services/report_service.py` với commit của Tú trên `main`.
- **Quy trình các bước Minh cần thực hiện trên máy của mình:**
  1. Checkout nhánh của mình và cập nhật remote:
     ```bash
     git checkout feature/supplier-reports
     git fetch origin
     ```
  2. Tạo file `services/supplier_service.py`, chuyển CRUD nhà cung cấp sang đó. Thêm `to_dict()` vào `models/supplier.py`. Sửa `services/report_service.py` chỉ giữ lại phần báo cáo.
  3. Rebase code trên nền `origin/main` mới nhất:
     ```bash
     git rebase origin/main
     ```
  4. Khi Git báo xung đột tại `services/report_service.py`:
     - Mở file `services/report_service.py` giải quyết xung đột: **Chọn giữ lại toàn bộ code báo cáo đầy đủ của Minh**, loại bỏ đoạn stub sơ sài của Tú.
     - Đánh dấu đã giải quyết: `git add services/report_service.py services/supplier_service.py models/supplier.py`.
     - Tiếp tục rebase: `git rebase --continue`.
  5. Đẩy code cập nhật lên nhánh remote:
     ```bash
     git push --force-with-lease origin feature/supplier-reports
     ```
  6. **Kết quả:** PR #3 trên GitHub sẽ tự động chuyển sang màu xanh (`mergeable: true`), sẵn sàng để merge sạch sẽ!

---

## 4. CHECKLIST KIỂM THỬ BẮT BUỘC TRƯỚC KHI MERGE TỪNG NHÁNH

Trước khi trưởng nhóm (Tiến) phê duyệt bất kỳ Pull Request nào vào `main`, nhánh đó phải vượt qua checklist 5 điểm sau:

```markdown
### Pre-Merge Verification Checklist
- [ ] 1. Cú pháp & Compile: `python3 -m compileall -q .` không có bất kỳ lỗi cú pháp nào.
- [ ] 2. Không import vòng (Circular Imports): `python3 -c "import models, services, storage, cli"` thành công.
- [ ] 3. Kiểm thử đơn vị (Unit Tests): `python3 -m unittest discover -s tests -v` đạt 100% OK, không có FAIL hay ERROR.
- [ ] 4. Không vi phạm phạm vi (Scope): Nhánh chỉ sửa đổi các tệp thuộc trách nhiệm phân công, không sửa đè file của thành viên khác.
- [ ] 5. Đối chiếu API Contract v1.0: Tên lớp, phương thức, tham số và ngoại lệ khớp 100% với `docs/API_CONTRACT.md`.
```

---

## 5. PHÂN BIỆT RÕ RÀNG: TEST CHẠY VỚI STUB VS TEST NGHIỆP VỤ THẬT

Trong quá trình nghiệm thu, nhóm cần phân biệt rạch ròi hai nhóm kiểm thử:

| Tiêu chí | Test chạy với Stub (Code tạm của Tú) | Test kiểm tra nghiệp vụ thật (Target State v1.0) |
| :--- | :--- | :--- |
| **Bản chất** | Kiểm tra các hàm giả lập/chắp vá để test case màu xanh (PASS giả tạo). | Kiểm tra tính bất biến (Invariants) và toàn vẹn dữ liệu kế toán kho. |
| **Ví dụ: Sửa số lượng tồn kho** | Test chấp nhận `update_product(p_id, quantity=100)` thành công. | **Test bắt buộc ném `ValueError`** khi cố tình sửa `quantity` qua `update_product` (Q08). |
| **Ví dụ: Nhập thực phẩm hết hạn** | Test cho phép nhập bất kỳ sản phẩm nào. | **Test bắt buộc ném `ValueError`** từ chối nhập thực phẩm đã hết hạn (Q10). |
| **Ví dụ: Xóa sản phẩm** | Test chỉ kiểm tra `p.quantity == 0`. | **Test kiểm tra cả 2 điều kiện:** `p.quantity == 0` VÀ `has_product_transactions() == False` (Q19, Q20). |
| **Ví dụ: Lưu trữ JSON** | Chỉ kiểm tra danh sách sản phẩm `products`. | **Kiểm tra lưu đủ 3 nhóm:** `products`, `suppliers`, `transactions` an toàn qua file tạm (Q05, Q33, Q34). |
| **Ví dụ: Kiểu dữ liệu nhập/xuất** | Chấp nhận `quantity = True` (do lọt kiểu bool). | **Bắt buộc ném `ValueError`** từ chối giá trị kiểu boolean (Q23). |

*Yêu cầu:* Tú và cả nhóm phải rà soát lại thư mục `tests/`, cập nhật các test case để phản ánh đúng các ràng buộc nghiệp vụ thật của API Contract v1.0.

---

## 6. THỨ TỰ TÍCH HỢP AN TOÀN TRÊN NHÁNH CHÍNH (`main`)

Để tránh xung đột dây chuyền, Tiến sẽ thực hiện hòa trộn các nhánh theo đúng lộ trình 6 bước:

| Thứ tự | Nhánh cần Merge | Người phụ trách | Điều kiện tiên quyết trước khi Merge | Kết quả đạt được |
| :---: | :--- | :--- | :--- | :--- |
| **Bước 1** | `feature/product-models` | Lâm | Đã có `increase_stock()`, `decrease_stock()`, xóa setter `quantity`, đổi `supplier_id`. | Hoàn thiện tầng thực thể sản phẩm chuẩn trên `main`. |
| **Bước 2** | `feature/supplier-reports` | Minh | Đã tách `SupplierService`, thêm `Supplier.to_dict()`, rebase hết conflict PR #3. | Hoàn thiện thực thể nhà cung cấp và dịch vụ báo cáo. |
| **Bước 3** | `feature/product-management` | Sơn | Đã viết xong 8 phương thức của `InventoryManager`, kết nối được với Product và Supplier. | Trái tim quản lý danh mục sản phẩm hoạt động trên `main`. |
| **Bước 4** | `feature/stock-transactions` | Chi | Đã tự sinh UUID4, thêm rollback, chặn bool, có `has_product_transactions()`. | Nghiệp vụ nhập/xuất kho nguyên tử hoàn tất. |
| **Bước 5** | `feature/storage-testing` | Tú | Đã sửa lưu đủ 3 nhóm JSON qua `os.replace`, xuất CSV 7 cột, test chuẩn. | Tầng lưu trữ bền vững hoàn chỉnh. |
| **Bước 6** | `feature/main-menu` | Tiến | Đấu nối `AppContext` trong `cli/menu.py` với 5 service thật, chạy toàn bộ kiểm thử. | **ỨNG DỤNG CONSOLE CLI HOÀN TẤT 100%.** |

---

## 7. TIẾN ĐỘ THỜI GIAN THEO NGÀY (DEADLINE: 25/11/2026)

- **Ngày 20/11 (Thứ Sáu):**  
  - Sơn hoàn thành `services/inventory_manager.py` (P0).  
  - Lâm hoàn thành sửa `models/product.py` (P1).  
  - Merge Bước 1 (`feature/product-models`).
- **Ngày 21/11 (Thứ Bảy):**  
  - Minh tách `SupplierService`, giải quyết conflict PR #3. Merge Bước 2.  
  - Chi sửa xong `StockService` và `StockTransaction`.  
  - Merge Bước 3 (`feature/product-management`).
- **Ngày 22/11 (Chủ Nhật):**  
  - Merge Bước 4 (`feature/stock-transactions`).  
  - Tú cập nhật `storage/storage.py` (lưu 3 thực thể) và chuẩn hóa bộ unit test. Merge Bước 5.
- **Ngày 23/11 (Thứ Hai):**  
  - Tiến tích hợp `AppContext` tại `cli/menu.py`. Chạy kiểm thử tích hợp toàn hệ thống. Merge Bước 6.
- **Ngày 24/11 (Thứ Ba):**  
  - Chạy thử nghiệm toàn bộ kịch bản người dùng trên Console CLI.  
  - Chụp ảnh màn hình các menu chức năng đưa vào thư mục báo cáo.  
  - Hoàn thiện báo cáo đồ án bài tập lớn (Word/PDF) và slide thuyết trình.
- **Ngày 25/11 (Thứ Tư):**  
  - **NGHIỆM THU DỰ ÁN VÀ NỘP BÀI CHÍNH THỨC.**

---
*Kế hoạch kỹ thuật được phê duyệt bởi Trưởng nhóm Tiến và lưu trữ chính thức tại [docs/reviews/TEAM_RECOVERY_PLAN_2026-11-19.md](file:///home/vuongductien/Tài%20liệu/quản%20lý%20kho%20hàng%20python/docs/reviews/TEAM_RECOVERY_PLAN_2026-11-19.md).*

