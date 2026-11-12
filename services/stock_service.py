"""Module xử lý nghiệp vụ nhập kho, xuất kho và theo dõi lịch sử giao dịch.

Người phụ trách: Thành viên 4 - Chi (nhánh `feature/stock-transactions`).

Lớp dự kiến triển khai:
- `StockService`

Các phương thức dự kiến:
- `import_stock()`
- `export_stock()`
- `get_transaction_history()`

Yêu cầu nghiệp vụ:
- Nhập kho làm tăng số lượng tồn kho của sản phẩm tương ứng.
- Xuất kho làm giảm số lượng tồn kho của sản phẩm tương ứng.
- Không cho phép xuất kho vượt quá số lượng tồn hiện tại.
- Không chấp nhận số lượng giao dịch không hợp lệ (<= 0 hoặc sai kiểu dữ liệu).
- Lưu đầy đủ thông tin mỗi giao dịch nhập/xuất thông qua `StockTransaction`.

TODO (Chi):
- [ ] Cài đặt lớp `StockService` liên kết với danh sách sản phẩm / `InventoryManager`.
- [ ] Cài đặt `import_stock()` kiểm tra số lượng hợp lệ, tăng tồn kho và ghi nhận `StockTransaction`.
- [ ] Cài đặt `export_stock()` kiểm tra tồn kho đủ trước khi trừ số lượng và ghi nhận giao dịch.
- [ ] Cài đặt `get_transaction_history()` để truy vấn toàn bộ hoặc lọc lịch sử giao dịch.
"""

