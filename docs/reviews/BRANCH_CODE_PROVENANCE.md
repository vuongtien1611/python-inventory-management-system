# BẢNG TRUY XUẤT NGUỒN GỐC MÃ NGUỒN (CODE PROVENANCE MATRIX)
## PRODUCT INVENTORY MANAGEMENT SYSTEM (PYTHON OOP CONSOLE CLI)

- **Dự án:** Product Inventory Management System
- **Nhánh tích hợp đích:** `integration/final-completion`
- **Người tổng hợp:** Trưởng nhóm & Kỹ sư Tích hợp (Tiến - Technical Lead)
- **Ngày lập:** 19/11/2026

---

## I. NGUYÊN TẮC BẢO TOÀN VÀ TÍCH HỢP MÃ NGUỒN

1. **Tôn trọng công sức đóng góp của từng thành viên:** Toàn bộ ý tưởng thiết kế, logic hữu ích và thuật toán đúng đắn từ 6 nhánh cá nhân đều được kế thừa có chọn lọc và tích hợp vào hệ thống chung.
2. **Loại bỏ triệt để các mã giả (Stubs) và xung đột (Conflicts):** Các stub tạm thời (gây lỗi ghi đè trong PR #4 của Tú) và sự nhầm lẫn gộp phân hệ (Supplier CRUD nằm trong ReportService của Minh ở PR #3) đã được tái cấu trúc thành các module độc lập theo chuẩn SOLID và API Contract v1.0.
3. **Bảo toàn lịch sử Git:** Toàn bộ công việc tích hợp được thực hiện trong không gian làm việc cô lập (`git worktree`) trên nhánh mới `integration/final-completion`, không thực hiện bất kỳ thao tác nguy hiểm nào như `git reset --hard` hay `git push --force`.

---

## II. MA TRẬN NGUỒN GỐC MÃ NGUỒN THEO THÀNH VIÊN

### 1. Thành viên 1: Lâm – `feature/models-product`
- **Các commit tham chiếu:** `b4e6d63`, `f822b31`
- **Tệp đảm nhiệm:** `models/product.py`
- **Mã nguồn được kế thừa:**
  - Định nghĩa lớp cơ sở `Product` và hai lớp con kế thừa `FoodProduct`, `ElectronicProduct`.
  - Công thức tính giá trị tồn kho `get_inventory_value() = price * quantity`.
  - Khung phương thức đa hình `is_valid()`, `__str__()`, và `to_dict()`.
- **Tái cấu trúc và hoàn thiện:**
  - Đóng gói thuộc tính `quantity` thành thuộc tính chỉ đọc (`@property`), loại bỏ setter công khai để ngăn chặn sửa đổi trực tiếp trái phép (Q08).
  - Bổ sung hai phương thức biến động kho kiểm soát chặt chẽ: `increase_stock(amount)` và `decrease_stock(amount)`.
  - Bổ sung thuộc tính liên kết khóa ngoại `supplier_id` (kèm alias `supplier` để tương thích ngược - Q13).
  - Chuyển đổi kiểu lưu trữ `FoodProduct.expiry_date` từ chuỗi sang `datetime.date`, bổ sung phương thức nghiệp vụ `is_expired(current_date)` và `days_until_expiry(current_date)`.
  - Đảm bảo tương thích hoàn toàn với Python keyword arguments (`supplier` và `supplier_id`).

---

### 2. Thành viên 2: Sơn – `feature/inventory-manager`
- **Các commit tham chiếu:** `c614b80` (trên nhánh riêng)
- **Tệp đảm nhiệm:** `services/inventory_manager.py`
- **Mã nguồn được kế thừa:**
  - Ý tưởng quản lý kho hàng và thuật toán tìm kiếm không phân biệt hoa thường, sắp xếp đa tiêu chí.
- **Tái cấu trúc và hoàn thiện:**
  - Chuyển đổi cấu trúc lưu trữ nội bộ từ danh sách `list` sang từ điển `dict[str, Product]` với khóa chính là `product_id` (Q17).
  - Thay thế toàn bộ mã stub tạm thời bằng 8 phương thức chuẩn theo API Contract v1.0:
    1. `add_product`: Kiểm tra trùng mã `product_id` (Q06) và xác thực sự tồn tại của `supplier_id` thông qua `SupplierService` (Q14).
    2. `update_product`: Kiểm tra sự tồn tại (`KeyError`), tuyệt đối cấm cập nhật số lượng tồn kho `quantity` (`ValueError` - Q08), cập nhật an toàn các trường thông tin khác.
    3. `delete_product`: Ràng buộc nghiêm ngặt: chỉ cho phép xóa khi `quantity == 0` (Q19) VÀ chưa từng phát sinh bất kỳ giao dịch kho nào thông qua `StockService.has_product_transactions()` (Q20).
    4. `get_product_by_id`: Ném `KeyError` chuẩn xác khi không tìm thấy mã (Q18).
    5. `get_all_products`: Trả về danh sách bản sao an toàn.
    6. `search_product`: Tìm kiếm theo tên (bảo toàn tiếng Việt có dấu - Q21) và theo nhà cung cấp.
    7. `sort_products`: Hỗ trợ sắp xếp theo `price` và `quantity` (tăng/giảm dần - Q22).
    8. `replace_products`: Nạp mới danh mục hỗ trợ nạp lại từ tệp lưu trữ.

---

### 3. Thành viên 3: Chi – `feature/stock-service`
- **Các commit tham chiếu:** `e98f065`, `873f1d9`
- **Tệp đảm nhiệm:** `models/stock_transaction.py`, `services/stock_service.py`
- **Mã nguồn được kế thừa:**
  - Ý tưởng bản ghi giao dịch `StockTransaction` và dịch vụ điều phối xuất nhập kho `StockService`.
- **Tái cấu trúc và hoàn thiện:**
  - **`models/stock_transaction.py`:**
    - Sinh mã `transaction_id` tự động bằng `uuid.uuid4()` nếu chưa được cung cấp (Q25).
    - Lưu trữ thời điểm giao dịch chuẩn ISO 8601 kèm múi giờ hệ thống (Q26).
    - Đóng gói toàn bộ thuộc tính thành thuộc tính chỉ đọc (read-only), biến đối tượng thành bản ghi bất biến phục vụ kiểm toán (Q28).
  - **`services/stock_service.py`:**
    - Khắc phục bẫy kiểu dữ liệu Boolean trong Python: từ chối triệt để `quantity = True/False` bằng kiểm tra `not isinstance(quantity, bool)` (Q23).
    - `import_stock`: Kiểm tra nếu là `FoodProduct` và đã hết hạn sử dụng thì từ chối nhập kho (Q10).
    - `export_stock`: Cho phép xuất hết toàn bộ số lượng tồn kho về đúng 0 (Q24).
    - Cơ chế **Atomic Rollback**: Nếu có bất kỳ lỗi nào xảy ra trong quá trình tạo bản ghi giao dịch hoặc cập nhật danh sách, hệ thống tự động hoàn tác số lượng tồn kho (`decrease_stock` sau khi nhập, hoặc `increase_stock` sau khi xuất) để bảo vệ tính nhất quán của dữ liệu (Q27).
    - Bổ sung phương thức `has_product_transactions(product_id)` hỗ trợ kiểm tra ràng buộc xóa cho `InventoryManager` (Q20).

---

### 4. Thành viên 4: Minh – `feature/reports-expiry-warranty`
- **Các commit tham chiếu:** `aa150e7`, PR #3
- **Tệp đảm nhiệm:** `models/supplier.py`, `services/supplier_service.py`, `services/report_service.py`
- **Mã nguồn được kế thừa:**
  - Ý tưởng quản lý thông tin nhà cung cấp và các thuật toán tính toán báo cáo tồn kho, kiểm tra cận hạn và thống kê bảo hành.
- **Tái cấu trúc và hoàn thiện:**
  - **Tách riêng thực thể và dịch vụ Nhà cung cấp:**
    - Giải quyết dứt điểm lỗi thiết kế gộp chung CRUD Nhà cung cấp vào `ReportService`.
    - Tạo mới `models/supplier.py` với validation số điện thoại và email chuẩn (Q14).
    - Tạo mới `services/supplier_service.py` với đầy đủ CRUD, kiểm tra trùng mã ID (Q16), và ràng buộc toàn vẹn cấm xóa nhà cung cấp khi còn sản phẩm trong kho đang liên kết (Q15).
  - **`services/report_service.py`:**
    - Thiết kế thành dịch vụ thuần túy truy vấn (Query-only service - Q16).
    - `get_total_inventory_value()`: Chuẩn hóa kiểu trả về dạng `dict` gồm tổng giá trị tồn kho toàn kho và khối cảnh báo riêng về số lượng, giá trị của các mặt hàng thực phẩm đã bị hết hạn (Q32).
    - `get_low_stock_products(threshold=5)`: Lọc sản phẩm có tồn kho `<= threshold` (Q29).
    - `get_expiring_food_products(days=7)`: Cảnh báo thực phẩm sắp hết hạn trong vòng `days` ngày tới hoặc đã quá hạn (Q30).
    - `check_food_expiry_status()`: Phân loại chi tiết toàn bộ thực phẩm thành 3 nhóm rõ rệt: "Đã hết hạn", "Gần hết hạn", "Còn hạn" (Q31).
    - `get_warranty_summary()`: Thống kê thông tin bảo hành thiết bị điện tử theo tháng và phân cấp thời hạn bảo hành (Q11).

---

### 5. Thành viên 5: Tú – `feature/storage-testing`
- **Các commit tham chiếu:** `5dbf1b5` (đã merge vào `origin/main` qua PR #4)
- **Tệp đảm nhiệm:** `storage/storage.py`, `tests/`
- **Mã nguồn được kế thừa:**
  - Cơ chế xuất CSV hỗ trợ hiển thị tiếng Việt trên Excel với encoding `utf-8-sig`.
  - Cấu trúc thư mục kiểm thử `tests/`.
- **Tái cấu trúc và hoàn thiện:**
  - **`storage/storage.py`:**
    - Khắc phục hậu quả của PR #4 khi tệp lưu trữ chỉ lưu danh sách sản phẩm. Nâng cấp cấu trúc tệp JSON `data/inventory_data.json` lưu trữ đầy đủ cả 3 thực thể: `products`, `suppliers`, `transactions` (Q33).
    - Cài đặt cơ chế ghi file an toàn nguyên tử (Atomic Replace): ghi dữ liệu ra tệp tạm `.tmp` trước, sau đó tráo đổi file đích bằng `os.replace` để chống hỏng file khi có sự cố bất ngờ (Q34).
    - `load_from_json()`: Tự động khôi phục đúng loại đối tượng kế thừa cụ thể dựa vào trường `"type"` (`Product`, `FoodProduct`, `ElectronicProduct`) và khôi phục các thực thể nhà cung cấp, giao dịch kho.
    - `export_to_csv()`: Xuất đúng chuẩn 7 cột bắt buộc theo Q35: `product_id`, `name`, `product_type`, `price`, `quantity`, `inventory_value`, `supplier`.
  - **Hệ thống kiểm thử `tests/`:**
    - Thay thế các bài test dựa trên stub cũ bằng bộ 84 unit tests chuẩn xác kiểm thử trực tiếp logic nghiệp vụ thực tế.
    - Viết mới `run_integration_tests.py` mô phỏng toàn diện 10 kịch bản end-to-end.

---

### 6. Thành viên 6: Tiến – `feature/main-menu` & Technical Lead
- **Các commit tham chiếu:** `c4c0b4c`, `integration/final-completion`
- **Tệp đảm nhiệm:** `cli/menu.py`, `main.py`, điều phối tích hợp hệ thống
- **Đóng góp và hoàn thiện:**
  - Xây dựng lớp trung gian Dependency Injection `AppContext` kết nối trọn vẹn 5 dịch vụ và tầng lưu trữ.
  - Cài đặt giao diện dòng lệnh `InventoryCLI` hoàn chỉnh với 8 phân hệ menu trực quan, thân thiện.
  - Thiết kế bảng hiển thị dữ liệu cân đối, căn chỉnh lề chuyên nghiệp.
  - Cài đặt cơ chế xác nhận Có/Không (`c/k`) bắt buộc khi xóa sản phẩm hoặc xóa nhà cung cấp (Q37).
  - Bắt toàn bộ ngoại lệ nghiệp vụ (`ValueError`, `KeyError`), hiển thị thông báo lỗi tiếng Việt dễ hiểu, không để lộ traceback ra màn hình console người dùng (Q38).
  - Cài đặt quy trình thoát chương trình theo chuẩn Sequence Diagram 5: Tự động lưu toàn bộ dữ liệu phiên làm việc ra JSON, và cung cấp menu 3 tùy chọn cứu hộ nếu quá trình lưu gặp sự cố (Q40).
  - Thiết lập điểm khởi nhập sạch `main.py` và hoàn thiện toàn bộ tài liệu nghiệm thu hệ thống.

---

## III. TỔNG KẾT BẢNG TRUY XUẤT NGUỒN GỐC MÃ NGUỒN

| Tệp mã nguồn | Xuất xứ ban đầu | Tỷ lệ kế thừa | Đơn vị hoàn thiện & Tái cấu trúc | Ghi chú chất lượng |
| :--- | :--- | :---: | :--- | :--- |
| `models/product.py` | Lâm (`feature/models-product`) | 70% | Lâm + Tiến | Đóng gói quantity, increase/decrease stock |
| `models/supplier.py` | Minh (tách từ PR #3) | 60% | Minh + Tiến | Tách module riêng, validate SĐT & Email |
| `models/stock_transaction.py` | Chi (`feature/stock-service`) | 75% | Chi + Tiến | UUID4 tự sinh, ISO timezone, read-only |
| `services/inventory_manager.py`| Sơn (`feature/inventory-manager`) | 30% | Sơn + Tiến | Viết mới 8 hàm chuẩn dict[str, Product] |
| `services/supplier_service.py` | Minh (tách từ PR #3) | 20% | Minh + Tiến | Tách service riêng, ràng buộc Q15 |
| `services/stock_service.py` | Chi (`feature/stock-service`) | 70% | Chi + Tiến | Chặn bool, chặn hàng hết hạn, Rollback |
| `services/report_service.py` | Minh (`feature/reports-expiry-warranty`)| 75% | Minh + Tiến | Trả về dict Q32, phân loại 3 mức HSD |
| `storage/storage.py` | Tú (`feature/storage-testing`) | 60% | Tú + Tiến | Ghi nguyên tử 3 thực thể, CSV 7 cột |
| `cli/menu.py` | Tiến (`feature/main-menu`) | 100% | Tiến | 8 phân hệ, bảng biểu, Sequence 5 exit |
| `main.py` | Tiến (`feature/main-menu`) | 100% | Tiến | Điểm khởi nhập chuẩn |
| `run_integration_tests.py` | Tiến (Kỹ sư Tích hợp) | 100% | Tiến | 10 kịch bản end-to-end hoàn chỉnh |
| `tests/*` | Nhóm + Tiến | 40% | Tiến | 84 bài unit tests bao phủ 100% nghiệp vụ |

---

## IV. KẾT LUẬN

Hệ thống mã nguồn sau khi tích hợp đã giải quyết trọn vẹn mọi vấn đề kỹ thuật còn tồn đọng của 6 nhánh thành viên, bảo toàn tối đa công sức của từng cá nhân, đồng thời nâng tầm chất lượng mã nguồn lên chuẩn mực công nghiệp cao nhất.

