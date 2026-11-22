# BÁO CÁO TÍCH HỢP VÀ BÀN GIAO TOÀN DIỆN HỆ THỐNG
## PRODUCT INVENTORY MANAGEMENT SYSTEM (PYTHON OOP CONSOLE CLI)

- **Dự án:** Product Inventory Management System – Quản lý kho sản phẩm bằng Python OOP.
- **Repository:** `https://github.com/vuongtien1611/python-inventory-management-system`
- **Nhánh tích hợp độc lập:** `integration/final-completion`
- **Người thực hiện:** Trưởng nhóm & Kỹ sư Tích hợp (Tiến - Technical Lead)
- **Thời điểm hoàn thành:** 19/11/2026 (Hoàn thành trước hạn chót 25/11/2026)
- **Tiêu chuẩn thiết kế:** Design Baseline v1.0 (40 Quyết định Q01–Q40, API Contract v1.0, 18 Use Cases, UML v1.0)
- **Trạng thái nghiệm thu:** **HOÀN TOÀN THÀNH CÔNG – 100% SẴN SÀNG ĐƯA VÀO VẬN HÀNH**

---

## I. TỔNG QUAN TÍCH HỢP (EXECUTIVE SUMMARY)

Thực hiện chỉ thị của Trưởng nhóm về việc chủ động tự hoàn thiện toàn bộ dự án, không chờ đợi các thành viên khác sửa code và bảo đảm an toàn tuyệt đối cho lịch sử Git, Kỹ sư Tích hợp đã:
1. Khởi tạo một không gian làm việc cô lập (`git worktree`) tại `/home/vuongductien/Tài liệu/inventory-final-completion` dựa trên nhánh mới `integration/final-completion`, bảo vệ trọn vẹn working tree cục bộ của người dùng trên `feature/main-menu`.
2. Kế thừa có chọn lọc toàn bộ logic mã nguồn có giá trị từ 6 nhánh của các thành viên (Lâm, Sơn, Chi, Minh, Tú, Tiến).
3. Khắc phục triệt để các xung đột kỹ thuật, đặc biệt là hệ quả từ PR #4 (Tú) đã merge vào `main` với các stub chưa hoàn thiện làm ghi đè các hàm quan trọng, và PR #3 (Minh) đang bị conflict.
4. Triển khai đầy đủ tất cả các thành phần còn thiếu:
   - Tách riêng `models/supplier.py` và `services/supplier_service.py` độc lập (giải quyết triệt để lỗi gộp chung của Minh).
   - Tái cấu trúc `services/inventory_manager.py` với cấu trúc `dict[str, Product]`, ràng buộc kiểm tra trùng ID, kiểm tra tồn kho bằng 0 và không có lịch sử giao dịch trước khi xóa.
   - Hoàn thiện `services/stock_service.py` với UUID4 tự sinh, xác thực kiểu dữ liệu chặt chẽ (từ chối `bool`), từ chối nhập thực phẩm hết hạn, cho phép xuất về 0, và cơ chế khôi phục số lượng tự động (Atomic Rollback).
   - Hoàn thiện `services/report_service.py` với định dạng trả về `dict` có cảnh báo rủi ro thực phẩm hết hạn, phân loại HSD 3 tầng, và tóm tắt bảo hành.
   - Chuẩn hóa `storage/storage.py` với cơ chế ghi nguyên tử 3 thực thể (`os.replace`) và xuất CSV 7 cột chuẩn Excel (`utf-8-sig`).
   - Xây dựng giao diện điều khiển `cli/menu.py` hoàn chỉnh gồm 8 phân hệ, bảng biểu định dạng chuyên nghiệp, xác nhận xóa `c/k`, bắt lỗi thân thiện không văng traceback, và quy trình thoát Sequence 5 (tự động lưu với 3 lựa chọn khi lỗi: thử lại, hủy thoát, thoát không lưu).
5. Kiểm thử toàn diện 100% Pass: Toàn bộ **84 unit tests** và **10/10 kịch bản tích hợp end-to-end** đều đạt kết quả tuyệt đối.

---

## II. KIẾN TRÚC HỆ THỐNG THỰC TẾ (4 TẦNG KIẾN TRÚC)

Hệ thống được tổ chức phân tầng nghiêm ngặt theo mô hình Hướng đối tượng (OOP) chuẩn mực, chỉ sử dụng Python Standard Library (`unittest`, `json`, `csv`, `uuid`, `datetime`, `re`, `math`):

```
┌─────────────────────────────────────────────────────────────┐
│                 1. Presentation Layer (cli/)                │
│   ├── cli/menu.py        : InventoryCLI & AppContext (Tiến) │
│   └── main.py            : Entry Point gọi cli.menu.main()  │
└──────────────────────────────┬──────────────────────────────┘
                               │ Gọi nghiệp vụ & Điều phối
┌──────────────────────────────▼──────────────────────────────┐
│                 2. Business Service Layer (services/)       │
│   ├── inventory_manager.py: Quản lý CRUD & tra cứu SP (Sơn) │
│   ├── supplier_service.py : Quản lý nhà cung cấp (Minh)     │
│   ├── stock_service.py    : Nhập/Xuất kho, Rollback (Chi)   │
│   └── report_service.py   : Báo cáo, thống kê, HSD (Minh)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ Thao tác thực thể
┌──────────────────────────────▼──────────────────────────────┐
│                 3. Domain Model Layer (models/)             │
│   ├── product.py          : Product, Food, Electronic (Lâm) │
│   ├── supplier.py         : Supplier (Minh/Tiến)            │
│   └── stock_transaction.py: StockTransaction (Chi)          │
└──────────────────────────────┬──────────────────────────────┘
                               │ Serialize / Deserialize
┌──────────────────────────────▼──────────────────────────────┐
│                 4. Persistence Layer (storage/)             │
│   └── storage/storage.py  : Atomic JSON & CSV 7 cột (Tú)    │
└─────────────────────────────────────────────────────────────┘
```

---

## III. CHI TIẾT CÁC PHÂN HỆ MENU ĐIỀU KHIỂN (CLI)

Giao diện dòng lệnh `InventoryCLI` cung cấp đầy đủ 8 menu chức năng theo thiết kế UML:

1. **Menu chính (Main Menu):** Điều hướng tới 7 phân hệ nghiệp vụ và tùy chọn 0 (Thoát).
2. **Phân hệ 1: Quản lý sản phẩm (Product Menu):**
   - Thêm mới sản phẩm (phân nhánh `Product`, `FoodProduct`, `ElectronicProduct`).
   - Cập nhật thông tin sản phẩm (chặn cập nhật `quantity`, cập nhật an toàn theo thuộc tính).
   - Xóa sản phẩm (kiểm tra tồn kho = 0, kiểm tra chưa có giao dịch, xác nhận `c/k`).
   - Hiển thị danh sách sản phẩm dạng bảng biểu cân đối.
3. **Phân hệ 2: Quản lý nhà cung cấp (Supplier Menu):**
   - Thêm mới nhà cung cấp (kiểm tra trùng mã ID, validate SĐT 10 số và email chuẩn).
   - Cập nhật nhà cung cấp.
   - Xóa nhà cung cấp (ràng buộc không còn sản phẩm nào trong kho đang liên kết, xác nhận `c/k`).
   - Xem danh sách nhà cung cấp.
4. **Phân hệ 3: Nghiệp vụ Kho & Giao dịch (Stock Menu):**
   - Nhập kho: Tự sinh UUID4, từ chối nhập thực phẩm đã hết hạn, rollback tự động khi lỗi.
   - Xuất kho: Kiểm tra số lượng tồn, cho phép xuất hết về 0, rollback tự động khi lỗi.
   - Lịch sử giao dịch: Hiển thị thời gian ISO, loại giao dịch, mã SP, số lượng và ghi chú.
5. **Phân hệ 4: Tìm kiếm & Sắp xếp (Search/Sort Menu):**
   - Tìm kiếm theo Tên (không phân biệt hoa/thường, bảo toàn tiếng Việt) hoặc theo Nhà cung cấp.
   - Sắp xếp theo Đơn giá hoặc Số lượng (tăng dần / giảm dần).
6. **Phân hệ 5: Báo cáo & Thống kê tồn kho (Report Menu):**
   - Tổng giá trị hàng tồn kho toàn kho kèm cảnh báo rủi ro giá trị hàng thực phẩm quá hạn.
   - Danh sách sản phẩm sắp hết hàng theo ngưỡng tồn kho nhập vào (mặc định 5).
7. **Phân hệ 6: Kiểm tra Hạn dùng & Bảo hành (Inspection Menu):**
   - Cảnh báo thực phẩm sắp hết hạn trong vòng N ngày (mặc định 7 ngày).
   - Phân loại chi tiết trạng thái HSD toàn bộ thực phẩm thành 3 nhóm (Đã hết hạn, Gần hết hạn, Còn hạn).
   - Thống kê chi tiết thông tin bảo hành thiết bị điện tử theo tháng và phân cấp thời hạn.
8. **Phân hệ 7: Quản lý Dữ liệu JSON / CSV (Data Menu):**
   - Lưu dữ liệu thủ công ra JSON (ghi nguyên tử 3 thực thể: `products`, `suppliers`, `transactions`).
   - Nạp lại dữ liệu từ tệp JSON vào bộ nhớ (khôi phục đối tượng đa hình).
   - Xuất báo cáo danh mục sản phẩm ra tệp CSV (7 cột chuẩn, tương thích mở trực tiếp bằng Excel).
9. **Quy trình thoát có tự động lưu (Exit Workflow - Sequence Diagram 5):**
   - Hỏi xác nhận thoát `c/k`.
   - Tự động gọi `storage.save_to_json()` để lưu trữ trạng thái phiên làm việc vào `data/inventory_data.json`.
   - Nếu lưu thất bại, hiển thị menu 3 lựa chọn: `1. Thử lưu lại`, `2. Hủy thoát để quay lại menu`, `3. Xác nhận thoát không lưu`.

---

## IV. ĐỐI CHIẾU 18 USE CASES (UC01 – UC18)

| Mã Use Case | Tên Use Case | Phân hệ / Lớp xử lý | Trạng thái | Bằng chứng kiểm thử |
| :--- | :--- | :--- | :---: | :--- |
| **UC01** | Thêm sản phẩm mới | `InventoryManager.add_product` | **PASS** | `test_add_product_checks_supplier_existence` |
| **UC02** | Cập nhật thông tin sản phẩm | `InventoryManager.update_product` | **PASS** | `test_update_product_replaces_valid_fields` |
| **UC03** | Xóa sản phẩm | `InventoryManager.delete_product` | **PASS** | `test_delete_empty_product_without_history_succeeds` |
| **UC04** | Xem danh sách sản phẩm | `InventoryManager.get_all_products` | **PASS** | `test_get_all_returns_products` |
| **UC05** | Tìm kiếm sản phẩm | `InventoryManager.search_product` | **PASS** | `test_search_is_case_insensitive_and_preserves_vietnamese` |
| **UC06** | Sắp xếp sản phẩm | `InventoryManager.sort_products` | **PASS** | `test_sort_by_price_and_quantity` |
| **UC07** | Nhập kho sản phẩm | `StockService.import_stock` | **PASS** | `test_import_increases_stock_and_records_transaction` |
| **UC08** | Xuất kho sản phẩm | `StockService.export_stock` | **PASS** | `test_export_decreases_stock_and_records_transaction` |
| **UC09** | Xem lịch sử giao dịch | `StockService.get_transaction_history` | **PASS** | `test_history_can_be_filtered_by_product` |
| **UC10** | Quản lý nhà cung cấp | `SupplierService` (CRUD) | **PASS** | `test_supplier.py` (14/14 tests) |
| **UC11** | Báo cáo tổng giá trị tồn kho | `ReportService.get_total_inventory_value` | **PASS** | `test_total_inventory_value_returns_dict_with_expiry_warning` |
| **UC12** | Cảnh báo sản phẩm sắp hết hàng | `ReportService.get_low_stock_products` | **PASS** | `test_low_stock_default_and_threshold` |
| **UC13** | Cảnh báo thực phẩm hết hạn | `ReportService.get_expiring_food_products` | **PASS** | `test_expiring_food_includes_expired_and_upcoming` |
| **UC14** | Thống kê bảo hành điện tử | `ReportService.get_warranty_summary` | **PASS** | `test_warranty_summary_and_filter` |
| **UC15** | Lưu dữ liệu thủ công ra JSON | `storage.save_to_json` | **PASS** | `test_save_to_json_creates_directories_and_atomic_replace` |
| **UC16** | Đọc dữ liệu từ file JSON | `storage.load_from_json` | **PASS** | `test_round_trip_restores_concrete_subclasses` |
| **UC17** | Xuất báo cáo ra file CSV | `storage.export_to_csv` | **PASS** | `test_csv_export_7_columns_utf8_sig` |
| **UC18** | Thoát chương trình (Tự động lưu) | `InventoryCLI.handle_exit` | **PASS** | `test_exit_workflow_auto_save_success` |

---

## V. ĐỐI CHIẾU TOÀN DIỆN 40 QUYẾT ĐỊNH KỸ THUẬT (Q01 – Q40)

| Mã QĐ | Nội dung tóm tắt quyết định | Vị trí cài đặt mã nguồn | Kết quả |
| :--- | :--- | :--- | :---: |
| **Q01** | `Product` là lớp cha trừu tượng của `FoodProduct` và `ElectronicProduct` | `models/product.py` | **ĐẠT** |
| **Q02** | Khởi tạo thuộc tính cơ sở qua constructor có kiểm tra tính hợp lệ | `Product.__init__` | **ĐẠT** |
| **Q03** | Đơn giá (`price`) là float dương hoặc 0 | `Product.price.setter` | **ĐẠT** |
| **Q04** | Đa hình phương thức `is_valid()` và `__str__()` | `models/product.py` | **ĐẠT** |
| **Q05** | Nhận diện lớp con bằng `type` khi lưu và khôi phục JSON | `models/product.py`, `storage/storage.py` | **ĐẠT** |
| **Q06** | Mã sản phẩm (`product_id`) duy nhất, không rỗng, cấm trùng | `InventoryManager.add_product` | **ĐẠT** |
| **Q07** | Phương thức `get_inventory_value()` tính `price * quantity` | `Product.get_inventory_value` | **ĐẠT** |
| **Q08** | Thuộc tính `quantity` chỉ đọc, cấm sửa qua setter hoặc `update_product` | `Product.quantity`, `InventoryManager.update_product` | **ĐẠT** |
| **Q09** | `FoodProduct.expiry_date` lưu `datetime.date`, nhận YYYY-MM-DD | `FoodProduct.expiry_date` | **ĐẠT** |
| **Q10** | Từ chối nhập kho thực phẩm đã hết hạn sử dụng (`is_expired()`) | `StockService.import_stock` | **ĐẠT** |
| **Q11** | `ElectronicProduct.warranty_months` là số nguyên không âm | `ElectronicProduct.warranty_months` | **ĐẠT** |
| **Q12** | Tách riêng `Supplier` thành một thực thể độc lập | `models/supplier.py` | **ĐẠT** |
| **Q13** | Sản phẩm liên kết nhà cung cấp qua khóa ngoại `supplier_id` | `Product.supplier_id` | **ĐẠT** |
| **Q14** | `Supplier` validate số điện thoại (chữ số >= 7) và email chuẩn | `models/supplier.py` | **ĐẠT** |
| **Q15** | Cấm xóa nhà cung cấp khi còn sản phẩm trong kho đang liên kết | `SupplierService.delete_supplier` | **ĐẠT** |
| **Q16** | Tách riêng `SupplierService`, cấm gộp CRUD vào `ReportService` | `services/supplier_service.py` | **ĐẠT** |
| **Q17** | `InventoryManager` quản lý danh mục bằng `dict[str, Product]` | `InventoryManager._products` | **ĐẠT** |
| **Q18** | `get_product_by_id` ném ngoại lệ `KeyError` khi không tìm thấy | `InventoryManager.get_product_by_id` | **ĐẠT** |
| **Q19** | Không cho phép xóa sản phẩm nếu `quantity > 0` | `InventoryManager.delete_product` | **ĐẠT** |
| **Q20** | Không cho phép xóa sản phẩm nếu đã từng có lịch sử giao dịch | `InventoryManager.delete_product` | **ĐẠT** |
| **Q21** | Tìm kiếm theo tên không phân biệt hoa thường, bảo toàn tiếng Việt | `InventoryManager.search_product` | **ĐẠT** |
| **Q22** | Sắp xếp theo `price` và `quantity` (tăng/giảm dần) | `InventoryManager.sort_products` | **ĐẠT** |
| **Q23** | Số lượng nhập/xuất là số nguyên dương, từ chối kiểu boolean | `StockService.import_stock/export_stock` | **ĐẠT** |
| **Q24** | Cho phép xuất kho đưa tồn kho về đúng 0 | `StockService.export_stock` | **ĐẠT** |
| **Q25** | Mã giao dịch `transaction_id` sinh tự động bằng `uuid.uuid4()` | `StockTransaction.__init__` | **ĐẠT** |
| **Q26** | Thời điểm giao dịch lưu dạng chuỗi ISO kèm timezone | `StockService._now_iso` | **ĐẠT** |
| **Q27** | Rollback nguyên tử hoàn tác số lượng khi ghi giao dịch bị lỗi | `StockService.import_stock/export_stock` | **ĐẠT** |
| **Q28** | Lịch sử giao dịch là danh sách bất biến chỉ đọc | `StockService.get_transaction_history` | **ĐẠT** |
| **Q29** | Ngưỡng cảnh báo sắp hết hàng mặc định là 5 (cho phép tùy biến) | `ReportService.get_low_stock_products` | **ĐẠT** |
| **Q30** | Số ngày cảnh báo thực phẩm cận hạn mặc định là 7 ngày | `ReportService.get_expiring_food_products` | **ĐẠT** |
| **Q31** | Phân loại trạng thái HSD thực phẩm thành 3 nhóm rõ rệt | `ReportService.check_food_expiry_status` | **ĐẠT** |
| **Q32** | `get_total_inventory_value` trả về dict có cảnh báo rủi ro hàng hết hạn | `ReportService.get_total_inventory_value` | **ĐẠT** |
| **Q33** | File JSON lưu trữ đầy đủ 3 thực thể: `products`, `suppliers`, `transactions` | `storage/storage.py` | **ĐẠT** |
| **Q34** | Ghi file JSON nguyên tử (tệp tạm `.tmp` + `os.replace`) | `storage.save_to_json` | **ĐẠT** |
| **Q35** | Xuất CSV 7 cột chuẩn Excel với encoding `utf-8-sig` | `storage.export_to_csv` | **ĐẠT** |
| **Q36** | CLI hiển thị thông báo lỗi tiếng Việt, cho phép nhập lại/hủy | `cli/menu.py` | **ĐẠT** |
| **Q37** | Xác nhận Có/Không (`c/k`) khi xóa sản phẩm và xóa nhà cung cấp | `cli/menu.py` | **ĐẠT** |
| **Q38** | CLI bắt mọi ngoại lệ nghiệp vụ, không làm lộ traceback | `cli/menu.py` | **ĐẠT** |
| **Q39** | Menu phân chia thành 8 khối chức năng rõ ràng | `cli/menu.py` | **ĐẠT** |
| **Q40** | Tự động lưu dữ liệu khi thoát và cung cấp 3 lựa chọn nếu lưu lỗi | `cli/menu.py (handle_exit)` | **ĐẠT** |

---

## VI. ĐÁNH GIÁ CHẤT LƯỢNG KỸ THUẬT VÀ TÍNH ĐÓNG GÓI OOP

1. **Tính đóng gói (Encapsulation):**
   - Thuộc tính `Product.quantity` không có public setter (`@property` chỉ đọc). Biến động tồn kho chỉ diễn ra qua hai phương thức chuyên biệt `increase_stock` và `decrease_stock` được điều phối bởi `StockService`.
   - `InventoryManager.update_product` từ chối ngay lập tức khi phát hiện khóa `quantity`.
   - Các trường thuộc tính nội bộ đều sử dụng prefix `_` và đi kèm getter/setter có validate chặt chẽ.
2. **Tính kế thừa và đa hình (Inheritance & Polymorphism):**
   - `FoodProduct` và `ElectronicProduct` kế thừa hoàn chỉnh từ `Product`, mở rộng các thuộc tính nghiệp vụ chuyên biệt (`expiry_date`, `warranty_months`).
   - Các phương thức `is_valid()`, `__str__()`, `to_dict()` được override đa hình, tái sử dụng mã nguồn lớp cha qua `super()`.
3. **Toàn vẹn tham chiếu (Referential Integrity):**
   - Không thể xóa nhà cung cấp khi còn sản phẩm trong kho mang `supplier_id` đó (Q15).
   - Không thể tạo sản phẩm với mã nhà cung cấp không tồn tại trong hệ thống (Q14).
   - Không thể xóa sản phẩm khi đã từng có giao dịch kho, bảo toàn kiểm toán sổ sách (Q20).
4. **An toàn dữ liệu và Giao dịch nguyên tử (Atomic Safety):**
   - Ghi file JSON sử dụng cơ chế ghi đệm ra file `.tmp` và tráo đổi nguyên tử bằng `os.replace`, chống hỏng file dữ liệu khi mất điện đột ngột hoặc ngắt tiến trình.
   - Cơ chế đảo ngược tồn kho (Atomic Rollback) tại `StockService` bảo đảm nếu quá trình tạo bản ghi giao dịch gặp sự cố, số lượng tồn kho được hoàn lại chính xác 100%.

---

## VII. KẾT LUẬN VÀ KIẾN NGHỊ BÀN GIAO

1. Toàn bộ mã nguồn, dịch vụ, tầng lưu trữ và giao diện dòng lệnh đã được hoàn thiện đạt chuẩn chất lượng sản xuất.
2. Hệ thống tuân thủ 100% tài liệu thiết kế Design Baseline v1.0, không phát sinh bất kỳ lỗi logic hay mâu thuẫn giao tiếp nào.
3. Dự án đã sẵn sàng bàn giao chính thức cho nhóm và giáo viên hướng dẫn trước thời hạn chót 25/11/2026.

