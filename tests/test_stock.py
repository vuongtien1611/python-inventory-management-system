"""Kiểm thử đơn vị cho nghiệp vụ nhập/xuất kho (`services/stock_service.py`).

Người phụ trách: Thành viên 6 - Tú (nhánh `feature/storage-testing`).

Các trường hợp kiểm thử dự kiến:
- Nhập kho làm tăng đúng số lượng tồn kho.
- Xuất kho làm giảm đúng số lượng tồn kho.
- Không cho phép xuất kho vượt quá số lượng tồn hiện tại.
- Từ chối số lượng giao dịch không hợp lệ (<= 0 hoặc sai kiểu).
- Ghi nhận đầy đủ lịch sử giao dịch vào `StockTransaction`.

TODO (Tú):
- [ ] Viết các test case cho `StockTransaction` và `StockService` sau khi Chi hoàn thành module.
"""

import unittest


if __name__ == "__main__":
    unittest.main()

