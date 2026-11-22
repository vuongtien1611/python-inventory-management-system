# Phân Công Công Việc Lập Trình Nhóm (6 Thành Viên)

- **Dự án:** Product Inventory Management System (`python-inventory-management-system`)
- **Đề tài:** Chủ đề 04 – Quản lý kho sản phẩm bằng Python OOP (Console CLI)
- **Repository:** <https://github.com/vuongtien1611/python-inventory-management-system>
- **Công nghệ:** Python 3.11+, OOP, Console CLI, `unittest`, JSON, CSV (ưu tiên thư viện chuẩn)
- **Tài liệu liên quan:**
  - [README.md](../README.md)
  - [Hợp đồng API chuẩn hóa v1.0 (`docs/API_CONTRACT.md`)](API_CONTRACT.md) *(Đã phê duyệt 40 quyết định thiết kế)*
  - [Hướng dẫn quy trình GitHub (`.github/CONTRIBUTING.md`)](../.github/CONTRIBUTING.md)

---

## Phân biệt chức năng bắt buộc và chức năng mở rộng

Để tránh nhầm lẫn phạm vi khi lập trình và bảo vệ bài tập lớn, nhóm phân định rõ:

| Nhóm chức năng | Phạm vi cụ thể | Thành viên liên quan |
| :--- | :--- | :--- |
| **Bắt buộc theo đề tài** | • Hệ thống lớp OOP sản phẩm (`Product`, `FoodProduct`, `ElectronicProduct`) thể hiện kế thừa, đa hình, đóng gói, validate dữ liệu<br>• Quản lý nhà cung cấp thông qua `Supplier` và `SupplierService`<br>• Quản lý sản phẩm CRUD, tìm kiếm, sắp xếp (`InventoryManager`)<br>• Nghiệp vụ nhập/xuất kho, không xuất vượt tồn, lưu lịch sử, hoàn tác lỗi (`StockTransaction`, `StockService`)<br>• Thống kê & kiểm tra: tổng giá trị tồn kho, sản phẩm sắp hết hàng, thực phẩm gần hết hạn, kiểm tra hạn sử dụng thực phẩm và thời hạn bảo hành thiết bị điện tử (`ReportService`)<br>• Giao diện Console CLI điều hướng đầy đủ, xử lý nhập sai<br>• Bộ kiểm thử `unittest` tối thiểu **10 trường hợp** (lỗi dữ liệu, trùng mã, ràng buộc nghiệp vụ) | Tiến, Lâm, Sơn, Chi, Minh, Tú |
| **Mở rộng do nhóm lựa chọn** | • Lưu/đọc toàn bộ dữ liệu hệ thống (sản phẩm, nhà cung cấp, lịch sử giao dịch) bằng **JSON** (khôi phục đúng kiểu đối tượng kế thừa, ghi file an toàn nguyên tử)<br>• Xuất báo cáo tồn kho ra **CSV** (đầy đủ 7 cột thông tin, hỗ trợ mở bằng Excel) | Tú, Tiến |

---

## 1. Thành viên 1 – TIẾN

- **Họ tên:** Tiến
- **Vai trò:** Trưởng nhóm, thiết kế menu Console, quản lý tích hợp và tài liệu tổng hợp.
- **Nhánh GitHub:** `feature/main-menu`
- **File chịu trách nhiệm:**
  - `main.py`
  - `cli/menu.py`
  - `cli/input_helpers.py`
  - `cli/__init__.py`
  - `docs/API_CONTRACT.md`
  - `docs/flowcharts/`
  - `docs/uml/`
  - `docs/TASK_ASSIGNMENT.md` và tổng hợp tài liệu báo cáo trong `docs/`
- **Mục tiêu công việc:**
  - Xây dựng hoàn chỉnh giao diện Console CLI (menu chính và 7 menu con) ổn định, không crash khi nhập sai (theo Q36, Q38).
  - Chuẩn hóa bộ khung tích hợp (`AppContext`) và tài liệu `API_CONTRACT.md` v1.0 để 5 thành viên còn lại phát triển độc lập.
  - Tích hợp lần lượt các service sau khi từng Pull Request được review và merge; hoàn thiện sơ đồ UML, lưu đồ và báo cáo cuối kỳ.
  - Tự động lưu dữ liệu an toàn khi thoát ứng dụng (theo Q05).
- **Trạng thái hiện tại:** PR triển khai menu Console và `API_CONTRACT.md` đã được merge vào `main`. Phần tích hợp nghiệp vụ với các service/storage đang chờ các nhánh thành viên hoàn thành.
- **Các lớp / thành phần cần lập trình:**
  - `AppContext` (dataclass chứa tham chiếu `inventory_manager`, `stock_service`, `supplier_service`, `report_service`, `storage`).
  - `InventoryCLI` trong `cli/menu.py`.
  - `UserExitSignal` và các hàm trợ giúp nhập liệu trong `cli/input_helpers.py`.
- **Danh sách phương thức / hàm cần xây dựng:**
  - `main.py`: gọi `cli.menu.main()`, bắt `KeyboardInterrupt` an toàn.
  - `cli/input_helpers.py`: `read_input_safe()`, `read_menu_choice()`, `confirm_action()`, `read_sort_order()`, `notify_not_implemented()`.
  - `cli/menu.py`: `display_main_menu()`, `display_submenu()`, `run_submenu()`, `run()`, các hàm mở menu 1..7, `build_app_context()`, `main()`, và các hàm `_handle_*` gọi service.
- **Yêu cầu kiểm tra dữ liệu & Xử lý lỗi:**
  - Bắt mọi ngoại lệ nghiệp vụ (`KeyError`, `ValueError`), hiển thị tiếng Việt, không in raw traceback (theo Q38).
  - Xóa sản phẩm hoặc nhà cung cấp phải yêu cầu xác nhận `c/k` (theo Q37).
  - Thoát chương trình có xác nhận và tự động lưu dữ liệu (theo Q05).

---

## 2. Thành viên 2 – LÂM

- **Họ tên:** Lâm
- **Vai trò:** Xây dựng các lớp mô hình sản phẩm và thể hiện đầy đủ nguyên lý OOP.
- **Nhánh GitHub:** `feature/product-models`
- **File chịu trách nhiệm:** `models/product.py`
- **Mục tiêu công việc:**
  - Thiết kế hệ thống lớp sản phẩm chuẩn OOP với **đóng gói**, **kế thừa**, **đa hình** và **kiểm tra dữ liệu đầu vào**.
  - Cung cấp nền tảng thực thể tin cậy cho `InventoryManager`, `StockService`, `ReportService` và `storage.py`.
- **Các lớp cần lập trình:**
  1. `Product` *(lớp cơ sở — bắt buộc theo Q04, Q12)*
  2. `FoodProduct(Product)` *(lớp con — bắt buộc theo Q04, Q09)*
  3. `ElectronicProduct(Product)` *(lớp con — bắt buộc theo Q04, Q11)*
- **Danh sách phương thức cần xây dựng:**
  - **Trên `Product`:**
    - Thuộc tính: `_product_id: str` (theo Q06), `_name: str`, `_price: float` (`price >= 0` theo Q07), `_quantity: int` (khởi tạo `0` theo Q08), `_supplier_id: str` (theo Q13).
    - `__init__(self, product_id: str, name: str, price: float, quantity: int = 0, supplier_id: str = "")`
    - `@property` getter/setter cho `product_id`, `name`, `price`, `supplier_id` với validation.
    - `@property` getter chỉ đọc cho `quantity` (tuyệt đối không tạo setter công khai nhằm bảo vệ tính đóng gói; số lượng tồn kho chỉ được cập nhật qua `increase_stock` / `decrease_stock` theo Q08).
    - `increase_stock(amount: int) -> None`: Tăng tồn kho thêm `amount` (`amount > 0`). Dành riêng cho `StockService`.
    - `decrease_stock(amount: int) -> None`: Giảm tồn kho đi `amount` (`amount > 0`, không vượt quá tồn hiện tại). Dành riêng cho `StockService`.
    - `is_valid() -> bool`
    - `get_inventory_value() -> float`: trả về `round(price * quantity, 2)`
    - `to_dict() -> dict`: có trường `"type": "Product"`
    - `__str__() -> str`
  - **Trên `FoodProduct(Product)`:**
    - Thuộc tính bổ sung: `_expiry_date: datetime.date` (xử lý kiểu `date`, lưu chuỗi `YYYY-MM-DD` theo Q09).
    - Ghi đè `is_valid()`, `__str__()`, `to_dict()` (có `"type": "FoodProduct"`).
    - `is_expired(current_date=None) -> bool`
    - `days_until_expiry(current_date=None) -> int`
  - **Trên `ElectronicProduct(Product)`:**
    - Thuộc tính bổ sung: `_warranty_months: int` (số tháng bảo hành `>= 0` theo Q11).
    - Ghi đè `is_valid()`, `__str__()`, `to_dict()` (có `"type": "ElectronicProduct"`).
- **Yêu cầu kiểm tra dữ liệu:**
  - `product_id` không rỗng sau khi `.strip()` (theo Q06).
  - `price >= 0` (cho phép bằng 0 theo Q07, không chấp nhận giá âm).
  - `quantity >= 0`, `warranty_months >= 0`.
  - `expiry_date` đúng định dạng `YYYY-MM-DD`.

---

## 3. Thành viên 3 – SƠN

- **Họ tên:** Sơn
- **Vai trò:** Xây dựng hệ thống quản lý danh mục sản phẩm (CRUD, tìm kiếm, sắp xếp).
- **Nhánh GitHub:** `feature/product-management`
- **File chịu trách nhiệm:** `services/inventory_manager.py`
- **Mục tiêu công việc:**
  - Xây dựng lớp `InventoryManager` quản lý tập trung danh sách sản phẩm trong kho bằng `dict[str, Product]`, bảo đảm toàn vẹn dữ liệu, chống trùng mã và kiểm tra ràng buộc xóa chặt chẽ.
- **Các lớp cần lập trình:**
  - `InventoryManager` *(bắt buộc)*
- **Danh sách phương thức cần xây dựng:**
  - `add_product(product: Product, supplier_service: SupplierService | None = None)`: Kiểm tra trùng mã (theo Q06) và kiểm tra `supplier_id` tồn tại trong `supplier_service` (theo Q14).
  - `update_product(product_id: str, **fields)`: Cập nhật `name`, `price`, `supplier_id`,... **Tuyệt đối cấm sửa `quantity`** (ném `ValueError` theo Q08). Ném `KeyError` nếu không tìm thấy `product_id`.
  - `delete_product(product_id: str, stock_service: StockService | None = None)`: Ném `KeyError` nếu không thấy; ném `ValueError` nếu `product.quantity > 0` (theo Q19); nếu có truyền `stock_service`, gọi `stock_service.has_product_transactions(product_id)` để kiểm tra và ném `ValueError` nếu đã có giao dịch (theo Q20). Ràng buộc được kiểm tra trực tiếp ở tầng service.
  - `get_product_by_id(product_id: str) -> Product`: **Ném `KeyError` nếu không tìm thấy** (theo Q18, không trả về `None`).
  - `get_all_products() -> list[Product]`: Trả về danh sách toàn bộ sản phẩm.
  - `search_product(keyword: str, by: str = "name") -> list[Product]`: Tìm theo mã, nhà cung cấp, hoặc tên (không phân biệt hoa/thường, giữ nguyên dấu tiếng Việt theo Q21).
  - `sort_products(by: str = "price", reverse: bool = False) -> list[Product]`: Sắp xếp theo giá hoặc số lượng, hỗ trợ tăng/giảm dần (theo Q22).
- **Cấu trúc lưu trữ nội bộ:** `_products: dict[str, Product]` (theo Q17).

---

## 4. Thành viên 4 – CHI

- **Họ tên:** Chi
- **Vai trò:** Xây dựng mô hình giao dịch và nghiệp vụ nhập/xuất kho.
- **Nhánh GitHub:** `feature/stock-transactions`
- **File chịu trách nhiệm:**
  - `models/stock_transaction.py`
  - `services/stock_service.py`
- **Mục tiêu công việc:**
  - Quản lý biến động kho, đảm bảo tính nguyên tử (atomic consistency) khi cập nhật tồn kho, không xuất vượt tồn và lưu lịch sử giao dịch bất biến.
- **Các lớp cần lập trình:**
  1. `StockTransaction` trong `models/stock_transaction.py` *(bắt buộc)*
  2. `StockService` trong `services/stock_service.py` *(bắt buộc)*
- **Danh sách phương thức cần xây dựng:**
  - **Trên `StockTransaction`:**
    - Thuộc tính: `transaction_id` (sinh tự động qua `uuid.uuid4()` theo Q25), `product_id`, `transaction_type` (`"IMPORT"` / `"EXPORT"`), `quantity`, `timestamp` (ISO có timezone theo Q26), `note`.
    - Thuộc tính chỉ đọc (read-only theo Q28), `to_dict()`, `__str__()`.
  - **Trên `StockService`:**
    - `__init__(self, inventory_manager: InventoryManager)`
    - `import_stock(product_id: str, quantity: int, note: str = "") -> StockTransaction`: Số lượng nguyên dương (theo Q23), không nhập thực phẩm đã hết hạn (theo Q10), tăng tồn kho, ghi nhận giao dịch, hoàn tác nếu lỗi (theo Q27).
    - `export_stock(product_id: str, quantity: int, note: str = "") -> StockTransaction`: Số lượng nguyên dương, không xuất vượt tồn kho, cho phép xuất hết về 0 (theo Q24), giảm tồn kho, ghi nhận giao dịch, hoàn tác nếu lỗi (theo Q27).
    - `get_transaction_history(product_id: str | None = None) -> list[StockTransaction]`: Trả về lịch sử giao dịch (chỉ đọc theo Q28).
    - `has_product_transactions(product_id: str) -> bool`: Kiểm tra sản phẩm đã phát sinh giao dịch chưa (hỗ trợ Q20).

---

## 5. Thành viên 5 – MINH

- **Họ tên:** Minh
- **Vai trò:** Quản lý nhà cung cấp, thống kê tồn kho và cảnh báo hạn sử dụng / bảo hành.
- **Nhánh GitHub:** `feature/supplier-reports`
- **File chịu trách nhiệm:**
  - `models/supplier.py`
  - `services/supplier_service.py` *(module mới theo Q16)*
  - `services/report_service.py`
- **Mục tiêu công việc:**
  - Xây dựng thực thể `Supplier`, tách riêng `SupplierService` quản lý CRUD nhà cung cấp, và `ReportService` chỉ thuần túy thực hiện truy vấn/thống kê.
- **Các lớp cần lập trình:**
  1. `Supplier` trong `models/supplier.py` *(bắt buộc theo Q13, Q16)*
  2. `SupplierService` trong `services/supplier_service.py` *(bắt buộc theo Q16)*
  3. `ReportService` trong `services/report_service.py` *(bắt buộc — thuần truy vấn/thống kê)*
- **Danh sách phương thức cần xây dựng:**
  - **Trên `Supplier`:**
    - Thuộc tính: `supplier_id` (duy nhất), `name`, `phone`, `address`, `email`.
    - `__init__(...)`, `@property`, `is_valid()`, `to_dict()`, `__str__()`.
  - **Trên `SupplierService` (CRUD Nhà cung cấp theo Q16):**
    - `add_supplier(supplier)`: Chống trùng `supplier_id`.
    - `update_supplier(supplier_id, **fields)`: Ném `KeyError` nếu không tìm thấy.
    - `delete_supplier(supplier_id: str, inventory_manager: InventoryManager | None = None)`: Ném `KeyError` nếu không tìm thấy; nếu có truyền `inventory_manager`, kiểm tra trong `get_all_products()` và ném `ValueError` nếu đang có sản phẩm liên kết với NCC (theo Q15). Ràng buộc toàn vẹn thực thi trực tiếp tại service.
    - `get_supplier_by_id(supplier_id) -> Supplier`: Ném `KeyError` nếu không tìm thấy.
    - `get_all_suppliers() -> list[Supplier]`
    - `has_supplier(supplier_id: str) -> bool`
  - **Trên `ReportService` (Thống kê & Cảnh báo):**
    - `__init__(self, inventory_manager: InventoryManager)`
    - `get_total_inventory_value() -> dict[str, float]`: Tính tổng giá trị toàn kho và tách riêng cảnh báo giá trị thực phẩm đã hết hạn (theo Q32).
    - `get_low_stock_products(threshold: int = 5) -> list[Product]`: Cảnh báo sắp hết hàng (mặc định 5 theo Q29).
    - `get_expiring_food_products(days: int = 7) -> list[FoodProduct]`: Cảnh báo thực phẩm cận hạn (mặc định 7 ngày theo Q30).
    - `check_food_expiry_status(product_id: str | None = None) -> list[dict]`: Phân loại 3 trạng thái: Đã hết hạn, Cận hạn, Còn hạn (theo Q31).
    - `get_warranty_summary(product_id: str | None = None) -> list[dict]`: Tổng hợp thời hạn bảo hành thiết bị điện tử theo tháng (theo Q11).

---

## 6. Thành viên 6 – TÚ

- **Họ tên:** Tú
- **Vai trò:** Lưu trữ dữ liệu (JSON), xuất báo cáo (CSV) và xây dựng bộ kiểm thử `unittest`.
- **Nhánh GitHub:** `feature/storage-testing`
- **File chịu trách nhiệm:**
  - `storage/storage.py`
  - `tests/test_product.py`
  - `tests/test_inventory.py`
  - `tests/test_stock.py`
  - `tests/test_reports.py`
- **Mục tiêu công việc:**
  - Hiện thực hóa tính năng lưu/đọc JSON bảo toàn 3 thực thể (`products`, `suppliers`, `transactions`), cơ chế ghi file an toàn nguyên tử (atomic replace), xuất báo cáo CSV 7 cột tiếng Việt chuẩn, và xây dựng bộ kiểm thử tối thiểu 10 test case nghiệp vụ.
- **Các hàm / lớp cần lập trình trong `storage/storage.py`:**
  - `save_to_json(data: dict, file_path="data/inventory_data.json") -> bool`: Lưu 3 nhóm thực thể (theo Q33), ghi ra file tạm rồi đổi tên thay thế file đích an toàn (theo Q34).
  - `load_from_json(file_path="data/inventory_data.json") -> dict`: Đọc và khôi phục đúng loại đối tượng, kiểm tra tính hợp lệ dữ liệu trước khi thay thế bộ nhớ (theo Q34).
  - `export_to_csv(products: list[Product], file_path="data/inventory_report.csv") -> None`: Xuất đầy đủ 7 cột: `product_id`, `name`, `product_type`, `price`, `quantity`, `inventory_value`, `supplier` với encoding `utf-8-sig` (theo Q35).
- **Danh sách kiểm thử tối thiểu (12 test case nghiệp vụ trong `tests/`):**
  1. Tạo sản phẩm hợp lệ (`Product`, `FoodProduct`, `ElectronicProduct`).
  2. Tạo sản phẩm có giá âm (bị từ chối theo Q07).
  3. Tạo sản phẩm có số lượng âm (bị từ chối).
  4. Thêm sản phẩm trùng mã (bị từ chối theo Q06).
  5. Cập nhật sản phẩm không cho phép sửa `quantity` (bị từ chối theo Q08).
  6. Xóa sản phẩm khi còn tồn kho hoặc đã có lịch sử giao dịch (bị từ chối theo Q19, Q20).
  7. Tìm kiếm trong kho rỗng và tìm kiếm không phân biệt hoa thường có dấu (theo Q21).
  8. Sắp xếp sản phẩm theo giá và số lượng tăng/giảm dần (theo Q22).
  9. Nhập kho số lượng nguyên dương và từ chối thực phẩm hết hạn (theo Q10, Q23).
  10. Xuất kho vượt tồn (từ chối) và xuất hết tồn về 0 (cho phép theo Q24).
  11. Thống kê tổng giá trị tồn kho phân tách thực phẩm hết hạn (theo Q32).
  12. Lưu và khôi phục dữ liệu JSON bảo toàn đúng kiểu lớp đối tượng và liên kết nhà cung cấp (theo Q33, Q34).

---

## 7. Quy định làm việc nhóm trên GitHub

Mỗi thành viên tuân thủ nghiêm ngặt quy trình sau:

1. **Clone repository** về máy (nếu chưa có):
   ```bash
   git clone https://github.com/vuongtien1611/python-inventory-management-system.git
   cd python-inventory-management-system
   ```
2. **Checkout đúng branch được phân công** và kéo bản mới nhất:
   ```bash
   git fetch origin
   git switch <ten-nhanh-cua-ban>
   git pull origin <ten-nhanh-cua-ban>
   ```
3. **Đọc kỹ [docs/API_CONTRACT.md](API_CONTRACT.md)** (bản chuẩn hóa v1.0) trước khi viết code.
4. **Chỉ chỉnh sửa module mình phụ trách** (không tự ý sửa file của thành viên khác nếu chưa trao đổi với nhóm).
5. **Kiểm tra code trước khi commit** (cú pháp, PEP 8, chạy thử `python3 main.py` và `python3 -m unittest discover -s tests -v`).
6. **Commit với thông điệp rõ ràng** (theo quy ước trong `.github/CONTRIBUTING.md`).
7. **Push lên branch cá nhân** trên GitHub (**tuyệt đối không push trực tiếp lên `main`**).
8. **Tạo Pull Request (PR) vào `main`** và điền đầy đủ mẫu trong `.github/PULL_REQUEST_TEMPLATE.md`.
9. **Chờ Trưởng nhóm (Tiến) review** và chạy kiểm tra tích hợp trước khi merge.

---

## 8. Bảng theo dõi tiến độ

| Thành viên | Module phụ trách | Trạng thái hiện tại | Kiểm thử | Pull Request |
| :--- | :--- | :--- | :--- | :--- |
| **Tiến** | `main.py`, `cli/`, `docs/` | PR menu Console & API Contract v1.0 đã merge vào `main`; phần tích hợp nghiệp vụ chờ các service | Đã chạy smoke test khởi động CLI (`2 tests OK`) & kiểm thử menu thủ công | Đã merge PR menu Console & API Contract vào `main` |
| **Lâm** | `models/product.py` | Chưa triển khai | Chưa có | Chưa mở PR |
| **Sơn** | `services/inventory_manager.py` | Chưa triển khai | Chưa có | Chưa mở PR |
| **Chi** | `models/stock_transaction.py`, `services/stock_service.py` | Chưa triển khai | Chưa có | Chưa mở PR |
| **Minh** | `models/supplier.py`, `services/supplier_service.py`, `services/report_service.py` | Chưa triển khai | Chưa có | Chưa mở PR |
| **Tú** | `storage/storage.py`, `tests/` | Chưa triển khai | Chưa có (mới có 2 smoke test khung) | Chưa mở PR |

---

## 9. Quy định nghiệm thu Pull Request & Xác nhận thiết kế v1.0

### Tiêu chí duyệt Pull Request vào `main`
Một Pull Request chỉ được chấp nhận merge khi đáp ứng đủ toàn bộ điều kiện sau:
- Code nằm đúng module được phân công.
- Không có lỗi cú pháp (`python3 -m compileall -q main.py cli models services storage tests`).
- Không phá vỡ chức năng hoặc bài kiểm thử hiện có (`python3 -m unittest discover -s tests -v`).
- Tuân thủ chính xác hợp đồng API trong [docs/API_CONTRACT.md](API_CONTRACT.md) v1.0.
- Có kiểm tra đầy đủ các trường hợp dữ liệu không hợp lệ / ràng buộc nghiệp vụ (40 quyết định thiết kế).
- Có kết quả kiểm thử phù hợp đính kèm trong mô tả PR.
- Không chứa thông tin đăng nhập, token, file tạm hoặc dữ liệu test rác trong `data/`.
- Được **Tiến** review và xác nhận tích hợp trước khi merge.

> **Xác nhận:** Toàn bộ 40 quyết định thiết kế kiến trúc và nghiệp vụ đã được trưởng nhóm và các thành viên phê duyệt chính thức (Approved Design v1.0). Toàn bộ nhóm bám sát tài liệu này để hoàn thành dự án trước **25/11/2026**.
