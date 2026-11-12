"""Điểm khởi chạy chính của ứng dụng Quản lý Kho Sản Phẩm (Console CLI).

Người phụ trách: Thành viên 1 - Tiến (nhánh `feature/main-menu`).

Module này chỉ chịu trách nhiệm gọi hàm `main()` từ `cli.menu` và xử lý
an toàn khi người dùng ngắt chương trình bằng Ctrl+C (`KeyboardInterrupt`).
"""

from cli.menu import main


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nĐã nhận tín hiệu ngắt (Ctrl+C). Đang thoát chương trình an toàn.")
