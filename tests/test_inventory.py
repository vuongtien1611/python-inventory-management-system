"""Kiểm thử đơn vị cho chức năng quản lý sản phẩm (`services/inventory_manager.py`).

Người phụ trách: Thành viên 6 - Tú (nhánh `feature/storage-testing`).

Các trường hợp kiểm thử dự kiến:
- Thêm sản phẩm mới thành công và từ chối sản phẩm trùng mã.
- Cập nhật sản phẩm hợp lệ và xử lý khi mã không tồn tại hoặc dữ liệu sai.
- Xóa sản phẩm và kiểm tra ràng buộc dữ liệu liên quan trước khi xóa.
- Tìm kiếm theo mã, tên, nhà cung cấp (kể cả khi danh sách rỗng).
- Sắp xếp theo giá và số lượng (tăng dần / giảm dần).
- Lưu và đọc JSON qua `storage/storage.py`, khôi phục đúng loại đối tượng.

TODO (Tú):
- [ ] Viết các test case cho `InventoryManager` sau khi Sơn hoàn thành `services/inventory_manager.py`.
- [ ] Viết các test case lưu/đọc JSON và khôi phục đối tượng cho `storage/storage.py`.
"""

import unittest


if __name__ == "__main__":
    unittest.main()

