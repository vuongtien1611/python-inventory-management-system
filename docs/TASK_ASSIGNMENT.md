# Phân Công Công Việc Lập Trình Nhóm (6 Thành Viên)

- **Dự án:** Product Inventory Management System (`python-inventory-management-system`)
- **Đề tài:** Chủ đề 04 – Quản lý kho sản phẩm bằng Python OOP (Console CLI)
- **Repository:** <https://github.com/vuongtien1611/python-inventory-management-system>
- **Công nghệ:** Python 3.11+, OOP, Console CLI, `unittest`, JSON, CSV (ưu tiên thư viện chuẩn)
- **Tài liệu liên quan:**
  - [README.md](../README.md)
  - [Đề xuất hợp đồng API (`docs/API_CONTRACT.md`)](API_CONTRACT.md) *(Bản đề xuất — chờ cả nhóm xác nhận)*
  - [Hướng dẫn quy trình GitHub (`.github/CONTRIBUTING.md`)](../.github/CONTRIBUTING.md)

---

## Phân biệt chức năng bắt buộc và chức năng mở rộng

Để tránh nhầm lẫn phạm vi khi lập trình và bảo vệ bài tập lớn, nhóm phân định rõ:

| Nhóm chức năng | Phạm vi cụ thể | Thành viên liên quan |
| :--- | :--- | :--- |
| **Bắt buộc theo đề tài** | • Hệ thống lớp OOP sản phẩm (`Product`, `FoodProduct`, `ElectronicProduct`) thể hiện kế thừa, đa hình, đóng gói, validate dữ liệu<br>• Lớp nhà cung cấp (`Supplier`) và quản lý thông tin nhà cung cấp<br>• Quản lý sản phẩm CRUD, tìm kiếm, sắp xếp (`InventoryManager`)<br>• Nghiệp vụ nhập/xuất kho, không xuất vượt tồn, lưu lịch sử (`StockTransaction`, `StockService`)<br>• Thống kê & kiểm tra: tổng giá trị tồn kho, sản phẩm sắp hết hàng, thực phẩm gần hết hạn, kiểm tra hạn sử dụng thực phẩm và thời hạn bảo hành thiết bị điện tử (`ReportService`)<br>• Giao diện Console CLI điều hướng đầy đủ, xử lý nhập sai<br>• Bộ kiểm thử `unittest` tối thiểu **10 trường hợp** (lỗi dữ liệu, trùng mã, ràng buộc nghiệp vụ) | Tiến, Lâm, Sơn, Chi, Minh, Tú |
| **Mở rộng do nhóm lựa chọn** | • Lưu/đọc dữ liệu sản phẩm bằng **JSON** (khôi phục đúng kiểu đối tượng kế thừa)<br>• Xuất báo cáo tồn kho ra **CSV** (hỗ trợ mở bằng Excel) | Tú, Tiến |

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
  - `docs/flowcharts/` (hiện có `docs/flowcharts/main_menu_flowchart.md`)
  - `docs/TASK_ASSIGNMENT.md` và tổng hợp tài liệu báo cáo trong `docs/`
- **Mục tiêu công việc:**
  - Xây dựng hoàn chỉnh giao diện Console CLI (menu chính và 7 menu con) ổn định, không crash khi nhập sai.
  - Chuẩn hóa bộ khung tích hợp (`AppContext`) và tài liệu `API_CONTRACT.md` để 5 thành viên còn lại phát triển độc lập.
  - Tích hợp lần lượt các service sau khi từng Pull Request được review và merge; hoàn thiện sơ đồ UML, lưu đồ và báo cáo cuối kỳ.
- **Trạng thái hiện tại:** PR triển khai menu Console và `API_CONTRACT.md` đã được merge vào `main`. Phần tích hợp nghiệp vụ với các service/storage vẫn chưa hoàn thành.
- **Các lớp / thành phần cần lập trình:**
  - `AppContext` (dataclass chứa tham chiếu `inventory_manager`, `stock_service`, `report_service`, `storage`).
  - `InventoryCLI` trong `cli/menu.py`.
  - `UserExitSignal` và các hàm trợ giúp nhập liệu trong `cli/input_helpers.py`.
- **Danh sách phương thức / hàm cần xây dựng:**
  - `main.py`: gọi `cli.menu.main()`, bắt `KeyboardInterrupt` an toàn.
  - `cli/input_helpers.py`: `read_input_safe()`, `read_menu_choice()`, `confirm_action()`, `read_sort_order()`, `notify_not_implemented()`.
  - `cli/menu.py`: `display_main_menu()`, `display_submenu()`, `run_submenu()`, `run()`, `open_product_menu()`, `open_supplier_menu()`, `open_stock_menu()`, `open_search_sort_menu()`, `open_report_menu()`, `open_inspection_menu()`, `open_data_menu()`, `build_app_context()`, `main()`, và các hàm `_handle_*` gọi service sau khi tích hợp.
- **Yêu cầu kiểm tra dữ liệu:**
  - Kiểm tra lựa chọn menu phải là số nguyên nằm trong phạm vi hợp lệ.
  - Kiểm tra xác nhận thoát (`c`/`k`, `y`/`n`), lựa chọn thứ tự sắp xếp (`asc`/`desc`).
  - Khi tích hợp nghiệp vụ: kiểm tra định dạng cơ bản đầu vào từ bàn phím (không rỗng, đúng kiểu số/ngày) trước khi truyền xuống service.
- **Các trường hợp lỗi cần xử lý:**
  - Người dùng nhập chữ thay cho số, nhập chuỗi rỗng hoặc nhập số ngoài phạm vi.
  - Người dùng nhấn `Ctrl+C` (`KeyboardInterrupt`) hoặc kết thúc luồng nhập (`EOFError` / `Ctrl+D`) — thoát sạch, không lặp vô hạn.
  - Khi tích hợp: bắt `ValueError`, `KeyError`, `TypeError`, `OSError` từ tầng service để in thông báo tiếng Việt thân thiện, không làm sập chương trình.
- **Các module cần phối hợp:**
  - Phối hợp với Lâm, Sơn, Chi, Minh, Tú để thống nhất `docs/API_CONTRACT.md`, ghép nối vào `build_app_context()` và các `_handle_*` trong `cli/menu.py`.
- **Checklist công việc:**
  - [x] **(Bắt buộc)** Xây dựng `main.py`, menu chính, 7 menu con, xử lý nhập sai, EOF/Ctrl+C và xác nhận thoát.
  - [x] **(Bắt buộc)** Tạo khung `AppContext`, bản đề xuất `docs/API_CONTRACT.md` và lưu đồ `docs/flowcharts/main_menu_flowchart.md`.
  - [ ] **(Bắt buộc)** Tích hợp `InventoryManager`, `StockService`, `ReportService` vào các menu tương ứng sau khi PR của thành viên được merge.
  - [ ] **(Mở rộng)** Tích hợp lưu/đọc JSON và xuất CSV từ `storage/storage.py` vào Menu 7 (và tự động nạp dữ liệu khi khởi động nếu nhóm thống nhất).
  - [ ] **(Bắt buộc)** Review PR của các thành viên, tổng hợp UML Class Diagram (`docs/uml/`), ảnh chụp màn hình (`docs/screenshots/`) và báo cáo (`docs/reports/`).
- **Tiêu chí nghiệm thu:**
  - Chạy `python3 main.py` thành công ngay từ thư mục gốc.
  - Toàn bộ menu hoạt động ổn định, quay lại menu cha bằng vòng lặp `while` (không đệ quy), không crash khi nhập sai.
  - Sau khi tích hợp, CLI gọi đúng tầng service, không đặt logic nghiệp vụ kho trực tiếp trong `cli/`.
  - Không làm hỏng các chức năng và smoke test hiện có.
- **Cách kiểm thử:**
  - Chạy `python3 main.py` và kiểm tra điều hướng tất cả 7 menu con, nhập chữ/rỗng/ngoài phạm vi, hủy thoát và xác nhận thoát, EOF.
  - Chạy `python3 -m compileall -q main.py cli models services storage tests` và `python3 -m unittest discover -s tests -v`.
- **Kết quả cần bàn giao:**
  - Menu Console hoàn chỉnh, file `docs/API_CONTRACT.md` đã thống nhất, lưu đồ + UML tổng hợp, code tích hợp chạy thông suốt toàn bộ luồng.

---

## 2. Thành viên 2 – LÂM

- **Họ tên:** Lâm
- **Vai trò:** Xây dựng các lớp mô hình sản phẩm và thể hiện đầy đủ nguyên lý OOP.
- **Nhánh GitHub:** `feature/product-models`
- **File chịu trách nhiệm:** `models/product.py` (và export lớp trong `models/__init__.py` khi nhóm đồng bộ).
- **Mục tiêu công việc:**
  - Thiết kế hệ thống lớp sản phẩm chuẩn OOP với **đóng gói**, **kế thừa**, **đa hình** và **kiểm tra dữ liệu đầu vào**.
  - Cung cấp nền tảng thực thể tin cậy cho `InventoryManager`, `StockService`, `ReportService` và `storage.py`.
- **Các lớp cần lập trình:**
  1. `Product` *(lớp cơ sở — bắt buộc)*
  2. `FoodProduct(Product)` *(lớp con — bắt buộc)*
  3. `ElectronicProduct(Product)` *(lớp con — bắt buộc)*
- **Danh sách phương thức cần xây dựng:**
  - **Trên `Product`:**
    - Thuộc tính: `product_id` (`str`), `name` (`str`), `price` (`float`), `quantity` (`int`), `supplier_id` / `supplier` *(xem mục cần thống nhất với `API_CONTRACT.md`)*.
    - `__init__(...)`
    - Các `@property` getter và setter có kiểm tra hợp lệ cho từng thuộc tính.
    - `is_valid() -> bool` *(bắt buộc)*
    - `get_inventory_value() -> float` *(bắt buộc)*
    - `__str__() -> str` *(bắt buộc)*
    - `to_dict() -> dict[str, Any]` *(mở rộng — phục vụ lưu JSON ở `storage/storage.py`)*
  - **Trên `FoodProduct(Product)`:**
    - Thuộc tính bổ sung: `expiry_date` (`str`, khuyến nghị chuẩn ISO `YYYY-MM-DD`).
    - Ghi đè `is_valid()`, `__str__()`, `get_inventory_value()` (nếu có quy tắc riêng) để thể hiện **đa hình**.
    - `to_dict()` có trường nhận diện loại `"type": "FoodProduct"`.
    - Phương thức kiểm tra hạn sử dụng (ví dụ kiểm tra còn hạn / số ngày còn lại hoặc `is_expired()`).
  - **Trên `ElectronicProduct(Product)`:**
    - Thuộc tính bổ sung: `warranty_months` (`int`).
    - Ghi đè `is_valid()`, `__str__()`, `get_inventory_value()` (nếu cần).
    - `to_dict()` có trường nhận diện loại `"type": "ElectronicProduct"`.
- **Yêu cầu kiểm tra dữ liệu:**
  - `product_id` và `name`: kiểu `str`, không rỗng sau khi `.strip()`.
  - `price`: số không âm (`>= 0`, hoặc `> 0` theo quy ước nhóm); ép kiểu/kiểm tra `bool` không bị nhận nhầm là số.
  - `quantity`: số nguyên không âm (`int`, `>= 0`).
  - `expiry_date`: đúng định dạng ngày hợp lệ (ví dụ `YYYY-MM-DD` qua `datetime.strptime` / `date.fromisoformat`).
  - `warranty_months`: số nguyên không âm (`int`, `>= 0`).
- **Các trường hợp lỗi cần xử lý:**
  - Mã sản phẩm rỗng hoặc chỉ toàn khoảng trắng.
  - Tên sản phẩm rỗng.
  - Giá âm hoặc sai kiểu dữ liệu (chuỗi chữ, `None`, `bool`).
  - Số lượng âm hoặc số thực khi yêu cầu số nguyên.
  - Ngày hết hạn sai định dạng (ví dụ `"2026-02-30"`, `"abc"`).
  - Số tháng bảo hành âm hoặc không phải số nguyên.
- **Các module cần phối hợp:**
  - **Sơn** (`services/inventory_manager.py`): lưu trữ và cập nhật đối tượng `Product`.
  - **Chi** (`services/stock_service.py`): đọc/cập nhật `quantity` thông qua property setter.
  - **Minh** (`services/report_service.py`): đọc `get_inventory_value()`, `expiry_date`, `warranty_months`.
  - **Tú** (`storage/storage.py`, `tests/test_product.py`): dùng `to_dict()` và constructor để lưu/khôi phục JSON và viết unit test.
- **Checklist công việc:**
  - [ ] **(Bắt buộc)** Cài đặt lớp `Product` với thuộc tính private/protected, `@property` getter/setter và validation.
  - [ ] **(Bắt buộc)** Cài đặt `FoodProduct(Product)` ghi đè `is_valid()`, `__str__()` và kiểm tra hạn sử dụng.
  - [ ] **(Bắt buộc)** Cài đặt `ElectronicProduct(Product)` ghi đè `is_valid()`, `__str__()` và kiểm tra bảo hành.
  - [ ] **(Mở rộng)** Cài đặt `to_dict()` cho cả 3 lớp có trường `"type"` để hỗ trợ JSON.
  - [ ] **(Bắt buộc)** Kiểm tra lại tên thuộc tính (`supplier_id` vs `supplier`) khớp với `docs/API_CONTRACT.md`.
- **Tiêu chí nghiệm thu:**
  - Khởi tạo thành công cả 3 loại đối tượng với dữ liệu hợp lệ và từ chối (ném `ValueError`/`TypeError`) khi dữ liệu sai.
  - Thể hiện rõ kế thừa, đóng gói và đa hình khi gọi chung các phương thức trên danh sách hỗn hợp gồm `Product`, `FoodProduct`, `ElectronicProduct`.
  - `get_inventory_value()` tính chính xác `price * quantity`.
  - Không phát sinh lỗi khi các service và storage gọi đến đối tượng.
- **Cách kiểm thử:**
  - Viết script kiểm tra nhanh hoặc phối hợp Tú chạy test case trong `tests/test_product.py` (tạo hợp lệ, giá âm, số lượng âm, ngày sai, đa hình `__str__` & `is_valid`).
- **Kết quả cần bàn giao:**
  - File `models/product.py` hoàn chỉnh, sạch PEP 8, có docstring đầy đủ cho từng lớp và phương thức.

---

## 3. Thành viên 3 – SƠN

- **Họ tên:** Sơn
- **Vai trò:** Xây dựng hệ thống quản lý danh mục sản phẩm (CRUD, tìm kiếm, sắp xếp).
- **Nhánh GitHub:** `feature/product-management`
- **File chịu trách nhiệm:** `services/inventory_manager.py`
- **Mục tiêu công việc:**
  - Xây dựng lớp `InventoryManager` quản lý tập trung danh sách sản phẩm trong kho, bảo đảm toàn vẹn mã sản phẩm và cung cấp đầy đủ nghiệp vụ CRUD, tìm kiếm, sắp xếp.
- **Các lớp cần lập trình:**
  - `InventoryManager` *(bắt buộc)*
- **Danh sách phương thức cần xây dựng:**
  - `add_product(product: Product)` *(bắt buộc)*
  - `update_product(product_id: str, **fields)` *(bắt buộc)*
  - `delete_product(product_id: str)` *(bắt buộc)*
  - `get_product_by_id(product_id: str) -> Product | None` *(bắt buộc — phục vụ tra cứu và `StockService`)*
  - `get_all_products() -> list[Product]` *(bắt buộc)*
  - `search_product(keyword: str, by: str = "name") -> list[Product]` *(bắt buộc)*
  - `sort_products(by: str = "price", reverse: bool = False) -> list[Product]` *(bắt buộc)*
- **Yêu cầu kiểm tra dữ liệu:**
  - Khi thêm: `product` phải là instance của `Product` (hoặc lớp con) và `product.is_valid()` đạt `True`; không được trùng `product_id`.
  - Khi cập nhật: `product_id` phải tồn tại; kiểm tra từng trường cập nhật hợp lệ trước khi gán (tránh cập nhật dở dang một phần khi có trường sai).
  - Khi xóa: kiểm tra tồn tại `product_id` và kiểm tra dữ liệu liên quan theo quy ước nhóm (ví dụ: còn tồn kho `quantity > 0` hoặc có giao dịch liên quan) trước khi xóa.
  - Khi tìm kiếm / sắp xếp: kiểm tra tham số `by` hợp lệ (`{"id", "name", "supplier"}` cho tìm kiếm; `{"price", "quantity"}` cho sắp xếp).
- **Các trường hợp lỗi cần xử lý:**
  - Thêm sản phẩm trùng mã `product_id` → ném `ValueError`.
  - Thêm đối tượng không phải `Product` hoặc không hợp lệ → ném `TypeError` / `ValueError`.
  - Cập nhật hoặc xóa mã sản phẩm không tồn tại → ném `KeyError` hoặc `ValueError` (theo `API_CONTRACT.md`).
  - Xóa sản phẩm đang vi phạm ràng buộc liên quan → ném `ValueError` với thông báo rõ ràng.
  - Kho hàng rỗng khi gọi `get_all_products()`, `search_product()`, `sort_products()` → trả về `[]` an toàn, không crash.
  - Tiêu chí tìm kiếm hoặc sắp xếp `by` không hợp lệ → ném `ValueError`.
- **Các module cần phối hợp:**
  - **Lâm** (`models/product.py`): sử dụng `Product`, `FoodProduct`, `ElectronicProduct`.
  - **Chi** (`services/stock_service.py`): cung cấp `get_product_by_id()` để nhập/xuất kho.
  - **Minh** (`services/report_service.py`): cung cấp `get_all_products()` để thống kê báo cáo.
  - **Tú** (`storage/storage.py`, `tests/test_inventory.py`): cung cấp `get_all_products()` / nạp dữ liệu sau khi đọc JSON và phối hợp kiểm thử.
  - **Tiến** (`cli/menu.py`): kết nối vào Menu 1 và Menu 4.
- **Checklist công việc:**
  - [ ] **(Bắt buộc)** Cài đặt cấu trúc lưu trữ nội bộ (khuyến nghị `dict[str, Product]` theo `API_CONTRACT.md`).
  - [ ] **(Bắt buộc)** Cài đặt `add_product()` chống trùng mã và validate đối tượng.
  - [ ] **(Bắt buộc)** Cài đặt `update_product()` kiểm tra tồn tại và kiểm tra dữ liệu mới trước khi áp dụng.
  - [ ] **(Bắt buộc)** Cài đặt `delete_product()` có kiểm tra ràng buộc dữ liệu liên quan.
  - [ ] **(Bắt buộc)** Cài đặt `get_product_by_id()` và `get_all_products()` (trả về bản sao list mới để tránh sửa trực tiếp bên ngoài).
  - [ ] **(Bắt buộc)** Cài đặt `search_product()` hỗ trợ tìm chính xác theo mã, tìm gần đúng (không phân biệt hoa thường) theo tên và nhà cung cấp.
  - [ ] **(Bắt buộc)** Cài đặt `sort_products()` hỗ trợ sắp xếp theo `price` và `quantity`, tăng dần (`reverse=False`) và giảm dần (`reverse=True`), không làm thay đổi thứ tự dữ liệu gốc nếu dùng list.
- **Tiêu chí nghiệm thu:**
  - Toàn bộ thao tác CRUD hoạt động chính xác cho cả `Product`, `FoodProduct` và `ElectronicProduct`.
  - Không thể thêm sản phẩm trùng mã.
  - Tìm kiếm và sắp xếp xử lý tốt kho rỗng, không làm thay đổi dữ liệu gốc ngoài ý muốn.
  - Thống nhất kiểu trả về và exception với `API_CONTRACT.md`.
- **Cách kiểm thử:**
  - Phối hợp Tú chạy test case trong `tests/test_inventory.py` (thêm hợp lệ, trùng mã, cập nhật, xóa không tồn tại, tìm kiếm kho rỗng, sắp xếp tăng/giảm dần).
- **Kết quả cần bàn giao:**
  - File `services/inventory_manager.py` hoàn chỉnh, tuân thủ PEP 8 và `API_CONTRACT.md`.

---

## 4. Thành viên 4 – CHI

- **Họ tên:** Chi
- **Vai trò:** Xây dựng mô hình giao dịch và nghiệp vụ nhập/xuất kho.
- **Nhánh GitHub:** `feature/stock-transactions`
- **File chịu trách nhiệm:**
  - `models/stock_transaction.py`
  - `services/stock_service.py`
- **Mục tiêu công việc:**
  - Ghi nhận minh bạch mọi biến động nhập/xuất kho, bảo đảm tồn kho được cập nhật chính xác và không bao giờ xuất âm.
- **Các lớp cần lập trình:**
  1. `StockTransaction` trong `models/stock_transaction.py` *(bắt buộc)*
  2. `StockService` trong `services/stock_service.py` *(bắt buộc)*
- **Danh sách phương thức cần xây dựng:**
  - **Trên `StockTransaction`:**
    - Thuộc tính: `transaction_id`, `product_id`, `transaction_type` (`"IMPORT"` / `"EXPORT"`), `quantity`, `timestamp`, `note`.
    - `__init__(...)`, các `@property` kiểm tra hợp lệ, `is_valid() -> bool` (nếu cần), `__str__() -> str`.
  - **Trên `StockService`:**
    - `__init__(self, inventory_manager: InventoryManager)`
    - `import_stock(product_id: str, quantity: int, note: str = "") -> StockTransaction`
    - `export_stock(product_id: str, quantity: int, note: str = "") -> StockTransaction`
    - `get_transaction_history(product_id: str | None = None) -> list[StockTransaction]`
- **Yêu cầu kiểm tra dữ liệu:**
  - `quantity` giao dịch phải là số nguyên dương (`isinstance(quantity, int)` và không phải `bool`, `quantity > 0`).
  - `transaction_type` chỉ chấp nhận `"IMPORT"` hoặc `"EXPORT"`.
  - `product_id` phải tồn tại trong `inventory_manager`.
  - Với `export_stock`: `quantity <= product.quantity`.
  - Mỗi giao dịch phải có `transaction_id` duy nhất và `timestamp` hợp lệ.
- **Các trường hợp lỗi cần xử lý:**
  - Nhập hoặc xuất số lượng `<= 0`, số âm, số thực hoặc chuỗi không hợp lệ → ném `ValueError`/`TypeError`.
  - Giao dịch với `product_id` không tồn tại → ném `KeyError`/`ValueError`.
  - Xuất kho vượt quá số lượng tồn hiện tại → ném `ValueError` và **không thay đổi tồn kho, không tạo `StockTransaction`**.
  - Lỗi khi cập nhật tồn kho → đảm bảo tính nguyên tử (không ghi lịch sử giao dịch thành công nếu tồn kho chưa cập nhật).
- **Các module cần phối hợp:**
  - **Sơn** (`services/inventory_manager.py`): gọi `inventory_manager.get_product_by_id(product_id)` để lấy sản phẩm.
  - **Lâm** (`models/product.py`): cập nhật `product.quantity` thông qua setter hợp lệ.
  - **Tú** (`tests/test_stock.py`): phối hợp viết và chạy unit test nhập/xuất kho.
  - **Tiến** (`cli/menu.py`): kết nối vào Menu 3 (Nhập kho, Xuất kho, Xem lịch sử giao dịch).
- **Checklist công việc:**
  - [ ] **(Bắt buộc)** Cài đặt `StockTransaction` với đóng gói (`@property`), kiểm tra dữ liệu và `__str__()` hiển thị rõ lịch sử.
  - [ ] **(Bắt buộc)** Cài đặt `StockService.__init__(inventory_manager)` nhận dependency từ ngoài.
  - [ ] **(Bắt buộc)** Cài đặt `import_stock()` tăng tồn kho và lưu `StockTransaction`.
  - [ ] **(Bắt buộc)** Cài đặt `export_stock()` kiểm tra đủ tồn kho trước khi giảm và lưu `StockTransaction`.
  - [ ] **(Bắt buộc)** Cài đặt `get_transaction_history()` hỗ trợ xem toàn bộ hoặc lọc theo `product_id`.
- **Tiêu chí nghiệm thu:**
  - Nhập kho làm tăng đúng số lượng tồn; xuất kho làm giảm đúng số lượng tồn.
  - Xuất vượt tồn kho bị từ chối dứt khoát và không tạo bản ghi giao dịch giả.
  - Lịch sử giao dịch lưu đầy đủ thời gian, loại giao dịch, mã sản phẩm, số lượng, ghi chú.
- **Cách kiểm thử:**
  - Phối hợp Tú chạy test case trong `tests/test_stock.py` (nhập hợp lệ, xuất hợp lệ, xuất vượt tồn, số lượng <= 0, mã sản phẩm không tồn tại).
- **Kết quả cần bàn giao:**
  - Hai file `models/stock_transaction.py` và `services/stock_service.py` hoàn chỉnh, có docstring và xử lý lỗi chặt chẽ.

---

## 5. Thành viên 5 – MINH

- **Họ tên:** Minh
- **Vai trò:** Quản lý thông tin nhà cung cấp, thống kê tồn kho và cảnh báo hạn sử dụng / bảo hành.
- **Nhánh GitHub:** `feature/supplier-reports`
- **File chịu trách nhiệm:**
  - `models/supplier.py`
  - `services/report_service.py`
- **Mục tiêu công việc:**
  - Xây dựng thực thể `Supplier` và các nghiệp vụ quản lý nhà cung cấp, thống kê giá trị tồn kho, cảnh báo hàng sắp hết, thực phẩm cận hạn và theo dõi bảo hành thiết bị điện tử.
- **Các lớp cần lập trình:**
  1. `Supplier` trong `models/supplier.py` *(bắt buộc theo đề tài)*
  2. `ReportService` trong `services/report_service.py` *(bắt buộc theo đề tài; CRUD nhà cung cấp đặt trong `ReportService` hoặc tách service riêng sau khi thống nhất với nhóm)*
- **Danh sách phương thức cần xây dựng:**
  - **Trên `Supplier`:**
    - Thuộc tính: `supplier_id`, `name`, `phone`, `address`, `email`.
    - `__init__(...)`, các `@property` getter/setter cần thiết, `is_valid() -> bool`, `__str__() -> str`.
  - **Quản lý nhà cung cấp** *(Menu 2 — bắt buộc theo đề tài)*:
    - `add_supplier(supplier)` (kiểm tra trùng `supplier_id`)
    - `update_supplier(supplier_id, **fields)`
    - `delete_supplier(supplier_id)` (kiểm tra sản phẩm liên kết trước khi xóa)
    - `get_all_suppliers()`
  - **Trên `ReportService`:**
    - `__init__(self, inventory_manager: InventoryManager, suppliers: list[Supplier] | None = None)`
    - `get_total_inventory_value() -> float` *(bắt buộc)*
    - `get_low_stock_products(threshold: int = 5) -> list[Product]` *(bắt buộc)*
    - `get_expiring_food_products(days: int = 7) -> list[FoodProduct]` *(bắt buộc)*
    - `check_food_expiry_status(product_id: str | None = None) -> list[dict[str, Any]]` *(bắt buộc theo đề tài — phân biệt còn hạn, gần hết hạn, đã hết hạn)*
    - `get_warranty_summary(product_id: str | None = None) -> list[dict[str, Any]]` *(bắt buộc theo đề tài — thống kê bảo hành thiết bị điện tử)*
- **Yêu cầu kiểm tra dữ liệu:**
  - `Supplier`: `supplier_id` và `name` không rỗng; `phone` đúng định dạng số điện thoại cơ bản; `email` hợp lệ nếu có nhập.
  - `threshold >= 0` (`int`) và `days >= 0` (`int`) ở các hàm thống kê.
  - Xử lý an toàn khi danh sách sản phẩm hoặc danh sách nhà cung cấp rỗng.
- **Các trường hợp lỗi cần xử lý:**
  - Thêm nhà cung cấp trùng `supplier_id` hoặc dữ liệu thiếu/sai định dạng.
  - Cập nhật/xóa `supplier_id` không tồn tại.
  - Xóa nhà cung cấp đang được sản phẩm tham chiếu trong kho → từ chối xóa và ném `ValueError`.
  - Ngày `expiry_date` trong dữ liệu không hợp lệ khi kiểm tra hạn sử dụng → xử lý an toàn, không làm sập toàn bộ báo cáo.
  - Tham số `threshold < 0` hoặc `days < 0` → ném `ValueError`.
- **Các module cần phối hợp:**
  - **Lâm** (`models/product.py`): dùng `Product.get_inventory_value()`, `FoodProduct`, `ElectronicProduct`.
  - **Sơn** (`services/inventory_manager.py`): gọi `inventory_manager.get_all_products()` để thống kê và kiểm tra liên kết nhà cung cấp trước khi xóa.
  - **Tú** (`tests/test_reports.py`): phối hợp viết test thống kê và báo cáo.
  - **Tiến** (`cli/menu.py`): kết nối vào Menu 2, Menu 5 và Menu 6; thống nhất trước với nhóm việc đặt CRUD `Supplier` trong `ReportService` hay tách `SupplierManager`.
- **Checklist công việc:**
  - [ ] **(Bắt buộc)** Cài đặt `Supplier` với `@property`, `is_valid()`, `__str__()`.
  - [ ] **(Bắt buộc)** Cài đặt CRUD `Supplier` (chống trùng mã, kiểm tra liên kết sản phẩm khi xóa) sau khi chốt vị trí lớp với nhóm.
  - [ ] **(Bắt buộc)** Cài đặt `get_total_inventory_value()` tổng hợp đúng giá trị tồn toàn kho.
  - [ ] **(Bắt buộc)** Cài đặt `get_low_stock_products(threshold=5)`.
  - [ ] **(Bắt buộc)** Cài đặt `get_expiring_food_products(days=7)`.
  - [ ] **(Bắt buộc)** Cài đặt `check_food_expiry_status()` phân loại rõ còn hạn / gần hết hạn / đã hết hạn và `get_warranty_summary()` cho `ElectronicProduct`.
- **Tiêu chí nghiệm thu:**
  - Tổng giá trị tồn kho tính chính xác (bằng `0.0` khi kho rỗng).
  - Không bỏ sót thực phẩm gần hết hạn hoặc đã hết hạn.
  - Dữ liệu `Supplier` được validate đầy đủ, không xóa nhầm nhà cung cấp đang gắn với sản phẩm.
  - Đã thống nhất rõ với nhóm cách tổ chức CRUD nhà cung cấp trước khi triển khai.
- **Cách kiểm thử:**
  - Phối hợp Tú chạy test case trong `tests/test_reports.py` (tổng giá trị tồn kho, hàng sắp hết, thực phẩm gần hết hạn/hết hạn, bảo hành điện tử, kho rỗng).
- **Kết quả cần bàn giao:**
  - Hai file `models/supplier.py` và `services/report_service.py` hoàn chỉnh, có docstring rõ ràng.

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
  - Hiện thực hóa tính năng lưu/đọc JSON bảo toàn đúng kiểu lớp đối tượng OOP, xuất báo cáo CSV tiếng Việt chuẩn cho Excel, và xây dựng bộ kiểm thử đơn vị toàn diện cho cả dự án.
- **Các hàm / lớp cần lập trình:**
  - Trong `storage/storage.py` *(chức năng mở rộng theo đề)*:
    - `save_to_json(products: list[Product], file_path: str = "data/products.json") -> None`
    - `load_from_json(file_path: str = "data/products.json") -> list[Product]`
    - `export_to_csv(products: list[Product], file_path: str = "data/inventory_report.csv") -> None`
    - *(Lưu ý)*: Thống nhất với Tiến xem giữ dạng hàm module hay bọc thêm class `InventoryStorage` để truyền vào `AppContext.storage`.
  - Trong `tests/`: các lớp `unittest.TestCase` tương ứng từng module (giữ nguyên `TestProjectBootstrap` hoặc mở rộng trong `tests/test_product.py`).
- **Danh sách kiểm thử tối thiểu (12 test case nghiệp vụ trong `tests/`):**
  1. Tạo sản phẩm hợp lệ (`Product`, `FoodProduct`, `ElectronicProduct`).
  2. Tạo sản phẩm có giá âm (bị từ chối).
  3. Tạo sản phẩm có số lượng âm (bị từ chối).
  4. Thêm sản phẩm trùng mã (bị từ chối).
  5. Cập nhật sản phẩm thành công / thất bại.
  6. Xóa sản phẩm không tồn tại (báo lỗi đúng).
  7. Tìm kiếm trong kho rỗng (trả về rỗng, không crash).
  8. Sắp xếp sản phẩm theo giá (tăng dần & giảm dần).
  9. Nhập kho hợp lệ (tồn kho tăng đúng, ghi nhận lịch sử).
  10. Xuất kho vượt tồn (bị từ chối, tồn kho không đổi).
  11. Thống kê tổng giá trị tồn kho chính xác.
  12. Lưu và khôi phục dữ liệu JSON (đúng kiểu `Product` / `FoodProduct` / `ElectronicProduct`).
- **Yêu cầu kiểm tra dữ liệu & kỹ thuật:**
  - JSON lưu với `encoding="utf-8"`, `ensure_ascii=False`, `indent=2` để không mất dấu tiếng Việt.
  - Khi đọc JSON: dựa vào trường `"type"` để khôi phục đúng instance `Product`, `FoodProduct` hoặc `ElectronicProduct`.
  - CSV xuất với `encoding="utf-8-sig"`, `newline=""`, có header rõ ràng gồm: Mã sản phẩm, Tên, Loại sản phẩm, Nhà cung cấp, Đơn giá, Số lượng, Giá trị tồn kho (và thông tin bổ sung nếu cần).
  - Tự động tạo thư mục cha (ví dụ `data/`) nếu chưa tồn tại trước khi ghi file.
- **Các trường hợp lỗi cần xử lý:**
  - File JSON chưa tồn tại khi đọc (`load_from_json`) → trả về `[]` an toàn (hoặc thông báo rõ theo thống nhất).
  - File JSON rỗng hoặc sai cú pháp JSON (`json.JSONDecodeError`) → ném `ValueError` với thông báo tiếng Việt rõ ràng.
  - Bản ghi JSON thiếu trường bắt buộc hoặc `"type"` không hợp lệ → ném `ValueError`.
  - Lỗi quyền ghi file (`OSError` / `PermissionError`) khi lưu JSON hoặc xuất CSV.
- **Các module cần phối hợp:**
  - **Lâm** (`models/product.py`): dùng `to_dict()` và constructor để serialize/deserialize.
  - **Sơn, Chi, Minh**: phối hợp kiểm thử các lớp service sau khi từng thành viên hoàn thành.
  - **Tiến** (`cli/menu.py`): thống nhất interface của `storage/storage.py` để gắn vào Menu 7 và tổng hợp bảng kết quả kiểm thử vào `docs/reports/`.
- **Checklist công việc:**
  - [ ] **(Mở rộng)** Cài đặt `save_to_json()` và `load_from_json()` khôi phục đúng 3 lớp sản phẩm.
  - [ ] **(Mở rộng)** Cài đặt `export_to_csv()` hỗ trợ tiếng Việt trên Excel.
  - [ ] **(Bắt buộc)** Viết unit test trong `tests/test_product.py` (kế thừa/đa hình/validate).
  - [ ] **(Bắt buộc)** Viết unit test trong `tests/test_inventory.py` (CRUD, tìm kiếm, sắp xếp) và kiểm thử JSON *(mở rộng)*.
  - [ ] **(Bắt buộc)** Viết unit test trong `tests/test_stock.py` (nhập/xuất, xuất vượt tồn, lịch sử).
  - [ ] **(Bắt buộc)** Viết unit test trong `tests/test_reports.py` (tổng giá trị tồn kho, sắp hết, cận hạn, bảo hành) và kiểm thử CSV *(mở rộng)*.
  - [ ] **(Bắt buộc)** Chạy toàn bộ `unittest` (tối thiểu 10 trường hợp kiểm thử nghiệp vụ), ghi nhận rõ số test pass/fail và nguyên nhân lỗi (nếu có).
- **Tiêu chí nghiệm thu:**
  - Lưu và đọc lại JSON giữ nguyên tiếng Việt và đúng kiểu đối tượng (`isinstance(..., FoodProduct)` / `ElectronicProduct`).
  - Xuất CSV mở trên Excel không lỗi font tiếng Việt và tính đúng giá trị tồn kho.
  - Chạy `python3 -m unittest discover -s tests -v` với tối thiểu 10 test case nghiệp vụ pass toàn bộ.
- **Cách kiểm thử:**
  - Sử dụng file tạm (`tempfile.TemporaryDirectory`) trong unit test để không ghi đè dữ liệu thật trong `data/`.
  - Chạy `python3 -m unittest discover -s tests -v`.
- **Kết quả cần bàn giao:**
  - File `storage/storage.py`, bộ 4 file kiểm thử trong `tests/`, và tổng hợp kết quả pass/fail gửi Tiến đưa vào `docs/reports/`.

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
3. **Đọc kỹ [docs/API_CONTRACT.md](API_CONTRACT.md)** trước khi viết code.
4. **Chỉ chỉnh sửa module mình phụ trách** (không tự ý sửa file của thành viên khác nếu chưa trao đổi với nhóm).
5. **Kiểm tra code trước khi commit** (cú pháp, PEP 8, chạy thử `python3 main.py` và `python3 -m unittest discover -s tests -v`).
6. **Commit với thông điệp rõ ràng** (theo quy ước trong `.github/CONTRIBUTING.md`).
7. **Push lên branch cá nhân** trên GitHub (**tuyệt đối không push trực tiếp lên `main`**).
8. **Tạo Pull Request (PR) vào `main`** và điền đầy đủ mẫu trong `.github/PULL_REQUEST_TEMPLATE.md`.
9. **Chờ Trưởng nhóm (Tiến) review** và chạy kiểm tra tích hợp trước khi merge.

**Ví dụ thao tác mẫu cho Thành viên 2 (Lâm):**

```bash
git switch feature/product-models
git pull origin feature/product-models
# (Lập trình trong models/product.py)
python3 -m compileall -q models/product.py
git add models/product.py
git commit -m "feat: implement product OOP models"
git push origin feature/product-models
```

---

## 8. Bảng theo dõi tiến độ

> **Nguyên tắc cập nhật:** Chỉ cập nhật sang trạng thái hoàn thành khi đã có code thực tế và bằng chứng kiểm thử tương ứng.

| Thành viên | Module | Trạng thái | Kiểm thử | Pull Request |
| :--- | :--- | :--- | :--- | :--- |
| **Tiến** | `main.py`, `cli/`, `docs/` | PR menu Console & API Contract đã merge vào `main`; phần tích hợp nghiệp vụ chưa hoàn thành | Đã chạy smoke test khởi động CLI (`2 tests OK`) & kiểm thử menu thủ công | Đã merge PR menu Console & API Contract vào `main` |
| **Lâm** | `models/product.py` | Chưa triển khai | Chưa có | Chưa mở PR |
| **Sơn** | `services/inventory_manager.py` | Chưa triển khai | Chưa có | Chưa mở PR |
| **Chi** | `models/stock_transaction.py`, `services/stock_service.py` | Chưa triển khai | Chưa có | Chưa mở PR |
| **Minh** | `models/supplier.py`, `services/report_service.py` | Chưa triển khai | Chưa có | Chưa mở PR |
| **Tú** | `storage/storage.py`, `tests/` | Chưa triển khai | Chưa có (mới có 2 smoke test khung) | Chưa mở PR |

---

## 9. Quy định nghiệm thu Pull Request & Các điểm chờ thống nhất

### Tiêu chí duyệt Pull Request vào `main`

Một Pull Request chỉ được chấp nhận merge khi đáp ứng đủ toàn bộ điều kiện sau:

- Code nằm đúng module được phân công.
- Không có lỗi cú pháp (`python3 -m compileall -q main.py cli models services storage tests`).
- Không phá vỡ chức năng hoặc bài kiểm thử hiện có (`python3 -m unittest discover -s tests -v`).
- Tuân thủ hợp đồng API trong `docs/API_CONTRACT.md` đã được nhóm thống nhất.
- Có kiểm tra đầy đủ các trường hợp dữ liệu không hợp lệ / ràng buộc nghiệp vụ.
- Có kết quả kiểm thử phù hợp đính kèm trong mô tả PR.
- Không chứa thông tin đăng nhập, token, file tạm hoặc dữ liệu test rác trong `data/`.
- Có mô tả rõ các chức năng đã triển khai theo mẫu PR.
- Được **Tiến** review và xác nhận tích hợp trước khi merge.

### Các điểm trong `docs/API_CONTRACT.md` cần nhóm chốt trước khi lập trình sâu

> **Lưu ý:** `docs/API_CONTRACT.md` hiện đang là **bản đề xuất**, chưa được xem là chốt chính thức nếu các thành viên chưa xác nhận:

1. **Tên thuộc tính nhà cung cấp trên `Product`:** dùng `supplier_id` hay `supplier` (Lâm – Sơn – Minh chốt chung).
2. **Định dạng ngày hạn sử dụng `FoodProduct`:** thống nhất `YYYY-MM-DD` hay `DD/MM/YYYY` (Lâm – Minh – Tú chốt chung).
3. **Cách sinh mã định danh (`product_id`, `supplier_id`, `transaction_id`):** người dùng nhập tay hay hệ thống tự sinh (Sơn – Chi – Minh – Tiến chốt chung).
4. **Quy tắc ràng buộc khi `delete_product()`:** cấm xóa khi `quantity > 0`, khi đã có `StockTransaction`, hay cho phép xác nhận xóa (Sơn – Chi chốt chung).
5. **Vị trí CRUD `Supplier`:** đặt trong `ReportService` hay tách lớp `SupplierService` riêng (Minh – Tiến chốt chung).
6. **Giao diện `storage/storage.py`:** dùng các hàm module (`save_to_json`, `load_from_json`, `export_to_csv`) hay đóng gói thành class `InventoryStorage` (Tú – Tiến chốt chung).

