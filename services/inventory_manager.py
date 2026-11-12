"""Module quản lý danh mục sản phẩm trong kho (CRUD, tìm kiếm, sắp xếp).

Người phụ trách: Thành viên 3 - Sơn (nhánh `feature/product-management`).

Lớp dự kiến triển khai:
- `InventoryManager`

Các phương thức dự kiến:
- `add_product()`
- `update_product()`
- `delete_product()`
- `get_all_products()`
- `search_product()`
- `sort_products()`

Yêu cầu nghiệp vụ:
- Không được thêm sản phẩm trùng mã.
- Kiểm tra tính hợp lệ của dữ liệu trước khi cập nhật.
- Kiểm tra dữ liệu liên quan trước khi xóa sản phẩm.
- Hỗ trợ tìm kiếm theo mã sản phẩm, tên sản phẩm hoặc nhà cung cấp.
- Hỗ trợ sắp xếp theo giá và số lượng (tăng dần / giảm dần).
- Xử lý an toàn khi danh sách sản phẩm đang rỗng.

TODO (Sơn):
- [ ] Cài đặt lớp `InventoryManager` quản lý danh sách đối tượng sản phẩm.
- [ ] Cài đặt `add_product()` có kiểm tra trùng mã và tính hợp lệ của sản phẩm.
- [ ] Cài đặt `update_product()` có kiểm tra tồn tại và dữ liệu mới trước khi cập nhật.
- [ ] Cài đặt `delete_product()` có kiểm tra ràng buộc liên quan trước khi xóa.
- [ ] Cài đặt `get_all_products()`, `search_product()` và `sort_products()` xử lý tốt trường hợp danh sách rỗng.
"""

