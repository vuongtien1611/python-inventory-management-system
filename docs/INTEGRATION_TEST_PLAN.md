# Kịch bản kiểm thử tích hợp

Tài liệu ghép hệ thống với Tiến. Workflow Product → InventoryManager → StockService → JSON/CSV chạy bằng `run_integration_tests.py`. Các handler CLI cho báo cáo tổng giá trị, hàng sắp hết, hạn sử dụng/bảo hành và dữ liệu JSON/CSV đã nối service; một số luồng quản lý nhà cung cấp và giao dịch dạng `StockTransaction` vẫn còn TODO.

## Điều kiện trước khi chạy

- `Product`, `InventoryManager`, `StockService`, `ReportService` chạy cho các ca đã triển khai.
- Hoàn thiện CRUD nhà cung cấp, `StockTransaction` và các handler menu còn lại trước khi chạy các ca mở rộng.
- Dùng thư mục dữ liệu tạm, không ghi dữ liệu demo vào kho cá nhân.

## Các luồng đầu cuối

| ID | Luồng | Thao tác | Kết quả cần thấy |
|---|---|---|---|
| INT-01 | Tạo và lưu kho | Tạo một sản phẩm thường, thực phẩm và điện tử; gọi `save_to_json` | JSON UTF-8 có ba type tag và đúng thuộc tính riêng của từng loại |
| INT-02 | Nạp lại kho | Gọi `load_from_json`, thêm vào `InventoryManager`, liệt kê qua CLI | Đủ ba sản phẩm; subtype và dữ liệu hạn dùng/bảo hành được giữ |
| INT-03 | Nhập/xuất | Nhập 5 đơn vị, xuất 2 đơn vị, đọc lịch sử giao dịch | Tồn kho tăng rồi giảm đúng; có hai giao dịch |
| INT-04 | Ràng buộc xuất kho | Thử xuất nhiều hơn tồn kho | Service từ chối; số lượng tồn không đổi; CLI hiển thị lỗi và tiếp tục chạy |
| INT-05 | Báo cáo và CSV | Tính tổng giá trị, xem hàng sắp hết, xuất CSV | Tổng giá trị/nhóm cảnh báo chính xác; CSV có header và mở được bằng Excel |
| INT-06 | Dữ liệu JSON lỗi | Nạp JSON sai cú pháp qua menu dữ liệu | Báo lỗi dễ hiểu, không làm thoát chương trình |
| INT-07 | Tìm kiếm và sắp xếp | Tìm theo mã/tên/NCC, sắp xếp giá và lượng tồn hai chiều | Kết quả khớp danh sách đã nạp và thứ tự đã chọn |

## Trình tự buổi ghép với Tiến

1. Tiến nối `storage` vào `AppContext` và menu dữ liệu, dùng `inventory_manager.get_all_products()` làm nguồn xuất.
2. Chạy unittest trước, sau đó chạy INT-01 đến INT-07 từ môi trường dữ liệu tạm.
3. Script `run_integration_tests.py` chạy các ca tạo sản phẩm, nhập/xuất, lịch sử, JSON, CSV và chặn xuất vượt tồn.
4. Bổ sung/run các ca supplier CRUD, StockTransaction và toàn bộ menu sau khi các phần tương ứng được hoàn thiện; lưu stdout và ảnh chụp làm minh chứng.

Lệnh kiểm tra sau khi tích hợp:

```bash
python -m unittest discover -s tests -v
python main.py
```
