# BÁO CÁO KIỂM THỬ TOÀN DIỆN CUỐI CÙNG (FINAL TEST REPORT)
## PRODUCT INVENTORY MANAGEMENT SYSTEM (PYTHON OOP CONSOLE CLI)

- **Dự án:** Product Inventory Management System
- **Môi trường thực thi:** Python 3.12 (Linux x86_64), Standard Library Only
- **Kỹ sư QA & Kiểm thử Tích hợp:** Tiến (Technical Lead & Integration QA)
- **Ngày hoàn thành kiểm thử:** 19/11/2026
- **Tổng số Unit Tests:** **84 bài kiểm thử** (Tỷ lệ đạt: **100% PASS - 0 Failures - 0 Errors**)
- **Thời gian chạy bộ kiểm thử:** **0.014 giây**
- **Kiểm thử tích hợp End-to-End (`run_integration_tests.py`):** **10/10 kịch bản PASS (100%)**

---

## I. TỔNG QUAN KIỂM THỬ (TEST SUMMARY)

Hệ thống kiểm thử được xây dựng bao phủ toàn bộ 4 tầng kiến trúc và 8 phân hệ dòng lệnh của ứng dụng. Mọi quy tắc nghiệp vụ khắt khe nhất trong Design Baseline v1.0 (40 Quyết định Q01–Q40) và 18 Use Cases đều được kiểm chứng độc lập bằng các ca kiểm thử tự động, không phụ thuộc vào mock bên thứ ba.

```
======================================================================
KẾT QUẢ TỔNG HỢP KIỂM THỬ:
----------------------------------------------------------------------
Tệp kiểm thử                   Số ca test       Thất bại      Lỗi       Tỷ lệ đạt
----------------------------------------------------------------------
tests/test_product.py             17               0           0         100%
tests/test_supplier.py            14               0           0         100%
tests/test_inventory.py           23               0           0         100%
tests/test_stock.py               14               0           0         100%
tests/test_reports.py              9               0           0         100%
tests/test_cli_integration.py      7               0           0         100%
----------------------------------------------------------------------
TỔNG CỘNG                         84               0           0         100% OK
======================================================================
```

---

## II. PHÂN RÃ CHI TIẾT BỘ UNIT TESTS (UNIT TEST BREAKDOWN)

### 1. `tests/test_product.py` (17 tests) – Mô hình Sản phẩm & Giao dịch kho
Phụ trách kiểm tra tính đóng gói, đa hình, và tính bất biến của các đối tượng miền:

| STT | Tên ca kiểm thử | Mục đích kiểm tra | Kết quả |
| :---: | :--- | :--- | :---: |
| 1 | `test_core_packages_importable` | Xác nhận toàn bộ 12 package/module cốt lõi import thành công | **PASS** |
| 2 | `test_cli_main_callable` | Kiểm tra hàm `main()` tồn tại và gọi được | **PASS** |
| 3 | `test_product_rejects_empty_id` | Từ chối mã sản phẩm rỗng (`ValueError`) | **PASS** |
| 4 | `test_product_rejects_negative_price` | Từ chối đơn giá âm (`ValueError`) | **PASS** |
| 5 | `test_product_rejects_negative_quantity`| Từ chối số lượng khởi tạo âm (`ValueError`) | **PASS** |
| 6 | `test_product_rejects_boolean_quantity_in_init` | Ngăn chặn bẫy `isinstance(True, int)` khi khởi tạo | **PASS** |
| 7 | `test_quantity_is_read_only_no_setter` | Xác nhận `quantity` không có setter (`AttributeError`) | **PASS** |
| 8 | `test_increase_stock_validation` | Xác thực tăng tồn kho: nhận int dương, từ chối 0, âm, float, bool | **PASS** |
| 9 | `test_decrease_stock_validation` | Xác thực giảm tồn kho: cho phép về 0, từ chối vượt tồn, float, bool | **PASS** |
| 10 | `test_inventory_value_is_price_times_quantity` | Kiểm tra công thức tính giá trị tồn kho `price * quantity` | **PASS** |
| 11 | `test_product_serialization_includes_type` | Kiểm tra `to_dict()` xuất đầy đủ `type` và `supplier_id` | **PASS** |
| 12 | `test_food_product_expiry_and_methods` | Kiểm tra `is_expired()`, `days_until_expiry()`, định dạng HSD | **PASS** |
| 13 | `test_electronic_product_warranty_and_methods` | Kiểm tra thuộc tính `warranty_months`, setter validation | **PASS** |
| 14 | `test_transaction_auto_id_and_fields` | Kiểm tra `StockTransaction` tự sinh UUID4, ISO timezone | **PASS** |
| 15 | `test_transaction_read_only_properties`| Đảm bảo các trường của `StockTransaction` là bất biến (read-only) | **PASS** |
| 16 | `test_transaction_invalid_type_rejected`| Từ chối loại giao dịch khác `IMPORT` / `EXPORT` | **PASS** |
| 17 | `test_transaction_serialization` | Kiểm tra `to_dict()` và định dạng tiếng Việt trong `__str__()` | **PASS** |

### 2. `tests/test_supplier.py` (14 tests) – Mô hình Nhà cung cấp & Dịch vụ NCC
Kiểm tra tầng quản lý đối tác cung ứng và toàn vẹn tham chiếu:

| STT | Tên ca kiểm thử | Mục đích kiểm tra | Kết quả |
| :---: | :--- | :--- | :---: |
| 1 | `test_valid_supplier_creation` | Tạo nhà cung cấp hợp lệ với đầy đủ 5 thuộc tính | **PASS** |
| 2 | `test_supplier_rejects_empty_id_or_name`| Từ chối mã hoặc tên nhà cung cấp rỗng | **PASS** |
| 3 | `test_supplier_phone_validation` | Validate số điện thoại (chứa chữ hoặc dưới 7 chữ số ném lỗi) | **PASS** |
| 4 | `test_supplier_email_validation` | Validate định dạng email theo regex chuẩn | **PASS** |
| 5 | `test_get_all_suppliers` | Lấy danh sách toàn bộ nhà cung cấp | **PASS** |
| 6 | `test_get_supplier_by_id_success_and_failure` | Lấy NCC theo ID, ném `KeyError` nếu không tìm thấy | **PASS** |
| 7 | `test_add_supplier_success` | Thêm mới nhà cung cấp thành công | **PASS** |
| 8 | `test_add_duplicate_supplier_rejected`| Từ chối thêm NCC có mã ID trùng lặp (`ValueError` - Q16) | **PASS** |
| 9 | `test_add_non_supplier_rejected` | Từ chối đối tượng không thuộc kiểu `Supplier` (`TypeError`) | **PASS** |
| 10 | `test_update_supplier_success` | Cập nhật tên, số điện thoại của nhà cung cấp | **PASS** |
| 11 | `test_update_supplier_missing_id` | Cập nhật NCC không tồn tại ném `KeyError` | **PASS** |
| 12 | `test_update_supplier_invalid_phone_or_email` | Cập nhật SĐT hoặc email sai quy cách ném `ValueError` | **PASS** |
| 13 | `test_delete_supplier_without_products_succeeds` | Xóa NCC thành công khi không có sản phẩm tham chiếu | **PASS** |
| 14 | `test_delete_supplier_referenced_by_product_fails`| Cấm xóa NCC khi còn sản phẩm trong kho đang liên kết (Q15) | **PASS** |

### 3. `tests/test_inventory.py` (23 tests) – Quản lý kho & Tầng lưu trữ
Kiểm tra nghiệp vụ CRUD sản phẩm và cơ chế ghi/đọc dữ liệu:

| STT | Tên ca kiểm thử | Mục đích kiểm tra | Kết quả |
| :---: | :--- | :--- | :---: |
| 1 | `test_save_to_json_creates_directories_and_atomic_replace` | Ghi file JSON tự tạo thư mục cha, tráo file nguyên tử (Q34) | **PASS** |
| 2 | `test_save_preserves_unicode_and_structure` | Bảo toàn tiếng Việt có dấu, lưu đủ 3 thực thể | **PASS** |
| 3 | `test_round_trip_restores_concrete_subclasses` | Khôi phục đúng lớp cụ thể (`Product`, `FoodProduct`, `ElectronicProduct`) | **PASS** |
| 4 | `test_missing_file_returns_empty_structure` | Tệp JSON không tồn tại trả về cấu trúc rỗng an toàn | **PASS** |
| 5 | `test_empty_file_returns_empty_structure` | Tệp JSON rỗng nội dung trả về cấu trúc rỗng an toàn | **PASS** |
| 6 | `test_malformed_json_raises_value_error`| Tệp JSON sai cú pháp ném `ValueError` và giữ nguyên bộ nhớ | **PASS** |
| 7 | `test_csv_export_7_columns_utf8_sig` | Xuất CSV 7 cột chuẩn Excel với encoding `utf-8-sig` (Q35) | **PASS** |
| 8 | `test_csv_empty_products_still_has_headers` | Danh mục rỗng vẫn xuất đủ 7 tiêu đề cột CSV | **PASS** |
| 9 | `test_get_all_returns_products` | Lấy toàn bộ danh sách sản phẩm | **PASS** |
| 10 | `test_get_product_by_id_success_and_keyerror` | Tìm SP theo ID, ném `KeyError` nếu không tồn tại (Q18) | **PASS** |
| 11 | `test_duplicate_id_is_rejected` | Từ chối đăng ký sản phẩm trùng mã ID (Q06) | **PASS** |
| 12 | `test_add_product_checks_supplier_existence` | Xác thực `supplier_id` phải tồn tại trong danh mục NCC (Q14) | **PASS** |
| 13 | `test_non_product_is_rejected` | Từ chối đối tượng không hợp lệ (`TypeError`) | **PASS** |
| 14 | `test_update_product_rejects_quantity` | Tuyệt đối cấm cập nhật `quantity` qua `update_product` (Q08) | **PASS** |
| 15 | `test_update_product_replaces_valid_fields` | Cập nhật thành công tên, giá; giữ nguyên số lượng tồn | **PASS** |
| 16 | `test_update_missing_product_raises_key_error` | Cập nhật SP không tồn tại ném `KeyError` | **PASS** |
| 17 | `test_delete_product_with_stock_is_rejected` | Từ chối xóa sản phẩm khi tồn kho `> 0` (Q19) | **PASS** |
| 18 | `test_delete_product_with_transaction_history_rejected` | Từ chối xóa sản phẩm khi đã có lịch sử giao dịch (Q20) | **PASS** |
| 19 | `test_delete_empty_product_without_history_succeeds` | Xóa thành công khi tồn kho = 0 và chưa có giao dịch | **PASS** |
| 20 | `test_search_is_case_insensitive_and_preserves_vietnamese` | Tìm kiếm không phân biệt hoa thường, bảo toàn dấu (Q21) | **PASS** |
| 21 | `test_search_by_supplier` | Tìm kiếm sản phẩm theo mã nhà cung cấp | **PASS** |
| 22 | `test_sort_by_price_and_quantity` | Sắp xếp theo đơn giá và số lượng (tăng/giảm dần - Q22) | **PASS** |
| 23 | `test_invalid_search_or_sort_field_is_rejected` | Từ chối tiêu chí tìm kiếm/sắp xếp không hỗ trợ | **PASS** |

### 4. `tests/test_stock.py` (14 tests) – Nghiệp vụ Nhập/Xuất & Giao dịch kho
Kiểm tra quy tắc xuất nhập kho, ràng buộc loại dữ liệu và cơ chế Rollback:

| STT | Tên ca kiểm thử | Mục đích kiểm tra | Kết quả |
| :---: | :--- | :--- | :---: |
| 1 | `test_import_increases_stock_and_records_transaction` | Nhập kho tăng tồn, ghi bản ghi `IMPORT` với UUID4 | **PASS** |
| 2 | `test_export_decreases_stock_and_records_transaction` | Xuất kho giảm tồn, ghi bản ghi `EXPORT` | **PASS** |
| 3 | `test_export_to_zero_is_permitted` | Cho phép xuất hết toàn bộ tồn kho về đúng 0 (Q24) | **PASS** |
| 4 | `test_export_cannot_exceed_stock` | Từ chối xuất vượt quá số lượng tồn hiện có (`ValueError` - Q23) | **PASS** |
| 5 | `test_zero_quantity_is_rejected` | Từ chối giao dịch với số lượng = 0 | **PASS** |
| 6 | `test_negative_quantity_is_rejected` | Từ chối giao dịch với số lượng âm | **PASS** |
| 7 | `test_non_integer_quantity_is_rejected`| Từ chối số lượng float (`TypeError`) | **PASS** |
| 8 | `test_boolean_quantity_is_rejected` | Từ chối số lượng kiểu bool (`TypeError` - Q23) | **PASS** |
| 9 | `test_unknown_product_is_rejected` | Giao dịch với mã SP không tồn tại ném `KeyError` | **PASS** |
| 10 | `test_history_can_be_filtered_by_product` | Lọc lịch sử giao dịch theo từng sản phẩm | **PASS** |
| 11 | `test_has_product_transactions_check`| Kiểm tra tồn tại giao dịch kho hỗ trợ xóa SP (Q20) | **PASS** |
| 12 | `test_import_expired_food_is_rejected` | Từ chối nhập kho thực phẩm đã hết hạn sử dụng (Q10) | **PASS** |
| 13 | `test_import_valid_food_succeeds` | Nhập kho thực phẩm còn hạn sử dụng thành công | **PASS** |
| 14 | `test_atomic_rollback_on_transaction_failure` | Tự động hoàn tác số lượng tồn kho khi lỗi ghi bản ghi (Q27) | **PASS** |

### 5. `tests/test_reports.py` (9 tests) – Báo cáo, Thống kê & Hạn dùng
Kiểm tra các hàm truy vấn phân tích kho hàng:

| STT | Tên ca kiểm thử | Mục đích kiểm tra | Kết quả |
| :---: | :--- | :--- | :---: |
| 1 | `test_total_inventory_value_returns_dict_with_expiry_warning` | Trả về dict tổng giá trị và cảnh báo giá trị hàng quá hạn (Q32) | **PASS** |
| 2 | `test_low_stock_default_and_threshold` | Lọc sản phẩm tồn kho `<= threshold` (mặc định 5 - Q29) | **PASS** |
| 3 | `test_low_stock_rejects_negative_threshold` | Từ chối ngưỡng tồn kho âm | **PASS** |
| 4 | `test_expiring_food_includes_expired_and_upcoming` | Lấy thực phẩm cận hạn trong vòng N ngày (mặc định 7 - Q30) | **PASS** |
| 5 | `test_expiry_status_three_tier_classification` | Phân loại chi tiết 3 nhóm: Đã hết hạn, Gần hết hạn, Còn hạn (Q31) | **PASS** |
| 6 | `test_expiry_status_can_filter_by_id` | Lọc trạng thái hạn dùng theo mã sản phẩm cụ thể | **PASS** |
| 7 | `test_expiring_rejects_negative_days` | Từ chối số ngày cảnh báo âm | **PASS** |
| 8 | `test_invalid_expiry_format_rejected_at_model_creation` | Chặn định dạng ngày sai chuẩn ngay tại constructor | **PASS** |
| 9 | `test_warranty_summary_and_filter` | Thống kê bảo hành thiết bị điện tử theo tháng và phân cấp (Q11) | **PASS** |

### 6. `tests/test_cli_integration.py` (7 tests) – Giao diện CLI & Luồng tích hợp
Kiểm tra điều hướng thực tế và quy trình thoát tự động lưu:

| STT | Tên ca kiểm thử | Mục đích kiểm tra | Kết quả |
| :---: | :--- | :--- | :---: |
| 1 | `test_build_app_context_wires_services_and_storage` | Khởi tạo `AppContext` kết nối đầy đủ 5 dịch vụ và storage | **PASS** |
| 2 | `test_report_menu_total_value_and_low_stock` | Điều hướng menu Báo cáo: in tổng giá trị tồn kho chuẩn xác | **PASS** |
| 3 | `test_stock_menu_routes_import_and_export` | Điều hướng menu Kho: thực hiện nhập và xuất kho thành công | **PASS** |
| 4 | `test_inspection_menu_expiry_and_status` | Điều hướng menu Kiểm tra: cảnh báo thực phẩm cận hạn | **PASS** |
| 5 | `test_supplier_menu_add_and_list` | Điều hướng menu Nhà cung cấp: thêm mới và hiển thị danh sách | **PASS** |
| 6 | `test_data_menu_save_and_load` | Điều hướng menu Dữ liệu: lưu JSON thủ công và xuất CSV | **PASS** |
| 7 | `test_exit_workflow_auto_save_success` | Thoát chương trình tự động lưu dữ liệu an toàn (Sequence 5) | **PASS** |

---

## III. KẾT QUẢ KIỂM THỬ TÍCH HỢP ĐẦU CUỐI (`run_integration_tests.py`)

Kịch bản kiểm thử tích hợp đầu cuối mô phỏng toàn bộ vòng đời hoạt động thực tế của một doanh nghiệp quản lý kho:

```
======================================================================
 BẮT ĐẦU CHẠY KIỂM THỬ TÍCH HỢP TOÀN DIỆN (END-TO-END SCENARIO)
======================================================================
PASS [1/10]: Tạo và đăng ký 2 Nhà cung cấp hợp lệ (SUP01, SUP02).
PASS [2/10]: Đăng ký 3 sản phẩm đa hình (Product, FoodProduct, ElectronicProduct).
PASS [3/10]: Nhập/xuất kho chính xác, ghi nhận 3 giao dịch và cho phép xuất về 0 (Q24).
PASS [4/10]: Đóng gói an toàn: cấm sửa quantity trực tiếp và qua update_product.
PASS [5/10]: Toàn vẹn tham chiếu và ràng buộc xóa hoạt động nghiêm ngặt.
PASS [6/10]: Từ chối giao dịch không hợp lệ, tồn kho được bảo toàn nguyên vẹn.
PASS [7/10]: Báo cáo tổng giá trị (800,000 đ), cảnh báo tồn kho và 3 mức HSD chuẩn xác.
PASS [8/10]: Lưu thành công 3 nhóm thực thể vào JSON với cơ chế Atomic Replace (Q34).
PASS [9/10]: Nạp và khôi phục 100% đối tượng đa hình và lịch sử giao dịch từ JSON.
PASS [10/10]: Xuất báo cáo CSV thành công gồm 7 cột chuẩn tương thích Excel (Q35).

======================================================================
 KẾT QUẢ: 10/10 KỊCH BẢN TÍCH HỢP ĐÃ VƯỢT QUA 100% THÀNH CÔNG!
======================================================================
```

---

## IV. PHÂN TÍCH CÁC TRƯỜNG HỢP BIÊN VÀ DỊ THƯỜNG (EDGE CASES)

1. **Bẫy kiểu Boolean trong Python (`isinstance(True, int) == True`):**
   - Đã kiểm tra và chặn đứng hoàn toàn: việc truyền `True`/`False` vào `quantity` khởi tạo, `increase_stock`, `decrease_stock`, `import_stock`, `export_stock` đều bị từ chối bằng `TypeError`.
2. **Xuất kho đưa tồn kho về đúng 0:**
   - Đã kiểm tra: Khi kho có 5 sản phẩm, xuất đúng 5 sản phẩm thành công đưa tồn về 0 (Q24). Xuất 6 sản phẩm bị chặn ngay lập tức mà không làm đổi số lượng.
3. **Thực phẩm hết hạn:**
   - Nhập kho thực phẩm đã quá hạn tính đến thời điểm hiện tại bị từ chối ngay lập tức với thông báo lỗi rõ ràng (Q10).
4. **Cơ chế Atomic Rollback:**
   - Giả lập lỗi phát sinh sau khi tăng/giảm số lượng tồn kho (lỗi ghi bản ghi giao dịch). Hệ thống đã tự động kích hoạt thao tác đảo ngược (`decrease_stock` sau khi nhập lỗi hoặc `increase_stock` sau khi xuất lỗi), khôi phục tồn kho chính xác 100% (Q27).
5. **Giao dịch file nguyên tử:**
   - Đảm bảo việc lưu trữ ghi ra tệp tạm `.tmp` trước, sau đó dùng `os.replace` tráo đổi nguyên tử, không để lại file rác và chống hỏng hóc file dữ liệu khi gặp sự cố đột ngột (Q34).
6. **Mở trực tiếp trên Microsoft Excel:**
   - Tệp CSV xuất ra mang tiền tố Byte Order Mark (`\xef\xbb\xbf`) của chuẩn `utf-8-sig`, bảo đảm mở trực tiếp trên Excel không bao giờ bị lỗi font tiếng Việt.

---

## V. KẾT LUẬN VÀ KÝ DUYỆT CHẤT LƯỢNG (QA SIGN-OFF)

- **Độ tin cậy mã nguồn:** Tuyệt đối (0 lỗi cú pháp, 0 cảnh báo linter, 100% unit tests pass).
- **Tính toàn vẹn nghiệp vụ:** Tuân thủ 100% 40 Quyết định kỹ thuật và 18 Use Cases.
- **Quyết định bàn giao:** **CHẤP THUẬN NGHIỆM THU CHÍNH THỨC (PASSED FOR PRODUCTION)**.

