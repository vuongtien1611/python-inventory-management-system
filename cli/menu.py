"""Module giao diện Console Menu và điều hướng chức năng chính.

Người phụ trách: Thành viên 1 - Tiến (nhánh `feature/main-menu`).

Giai đoạn khởi tạo:
- Hiển thị menu tối thiểu để kiểm tra ứng dụng khởi động và thoát bình thường.
- Các lựa chọn nghiệp vụ được đánh dấu TODO, chờ tích hợp khi các thành viên hoàn thành module.
"""


def display_menu() -> None:
    """Hiển thị menu chính của chương trình trên Console."""
    print("\n" + "=" * 50)
    print("  HỆ THỐNG QUẢN LÝ KHO SẢN PHẨM (PYTHON OOP)")
    print("=" * 50)
    print("1. Quản lý sản phẩm (TODO - Sơn)")
    print("2. Nhập / Xuất kho & Lịch sử giao dịch (TODO - Chi)")
    print("3. Quản lý nhà cung cấp & Thống kê (TODO - Minh)")
    print("4. Lưu / Đọc JSON & Xuất báo cáo CSV (TODO - Tú)")
    print("0. Thoát chương trình")
    print("=" * 50)


def main() -> None:
    """Vòng lặp chính xử lý điều hướng menu Console."""
    # TODO (Tiến): Khởi tạo và nạp dữ liệu từ Storage khi các module sẵn sàng.
    while True:
        display_menu()
        try:
            choice = input("Chọn chức năng (0-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nĐang thoát chương trình. Tạm biệt!")
            break

        if choice == "0":
            print("Đã thoát chương trình Quản lý Kho Sản Phẩm.")
            break
        elif choice == "1":
            # TODO (Tiến): Tích hợp menu con gọi InventoryManager (services/inventory_manager.py).
            print("[TODO] Chức năng quản lý sản phẩm chưa được triển khai.")
        elif choice == "2":
            # TODO (Tiến): Tích hợp menu con gọi StockService (services/stock_service.py).
            print("[TODO] Chức năng nhập/xuất kho chưa được triển khai.")
        elif choice == "3":
            # TODO (Tiến): Tích hợp menu con gọi Supplier & ReportService (services/report_service.py).
            print("[TODO] Chức năng nhà cung cấp & thống kê chưa được triển khai.")
        elif choice == "4":
            # TODO (Tiến): Tích hợp lưu/đọc JSON và xuất CSV từ storage/storage.py.
            print("[TODO] Chức năng lưu trữ JSON / xuất CSV chưa được triển khai.")
        else:
            print("Lựa chọn không hợp lệ. Vui lòng nhập số từ 0 đến 4.")

