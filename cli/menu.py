"""Module giao diện Console Menu và điều hướng chức năng chính.

Người phụ trách: Thành viên 1 - Tiến (nhánh `feature/main-menu`).

Kiến trúc:
- Tách riêng phần giao diện (`InventoryCLI`) với tầng nghiệp vụ (`services/`).
- Tiếp nhận lựa chọn, kiểm tra đầu vào qua `cli.input_helpers` và điều phối
  đến các service thông qua `AppContext`.
- Không dùng đệ quy để quay lại menu; toàn bộ điều hướng dùng vòng lặp `while`.
"""

from dataclasses import dataclass
from typing import Any, Callable

from cli.input_helpers import (
    UserExitSignal,
    confirm_action,
    notify_not_implemented,
    read_menu_choice,
    read_sort_order,
)

MenuOption = tuple[int, str, Callable[[], None]]


@dataclass
class AppContext:
    """Lưu trữ các tham chiếu service và storage phục vụ tích hợp hệ thống.

    Các thành phần được khởi tạo là `None` khi module tương ứng chưa hoàn thiện.
    Sau khi các thành viên thống nhất API và hoàn thành module, chỉ cần truyền
    hoặc khởi tạo các đối tượng service vào đây.
    """

    inventory_manager: Any = None
    stock_service: Any = None
    report_service: Any = None
    storage: Any = None


class InventoryCLI:
    """Lớp điều khiển giao diện Console và điều hướng giữa các menu."""

    LINE_WIDTH = 50

    def __init__(self, context: AppContext | None = None) -> None:
        """Khởi tạo giao diện Console với ngữ cảnh tích hợp service."""
        self.context = context if context is not None else AppContext()

    def display_main_menu(self) -> None:
        """Hiển thị menu chính của Hệ thống Quản lý Kho Sản Phẩm."""
        print("\n" + "=" * self.LINE_WIDTH)
        print("          HỆ THỐNG QUẢN LÝ KHO SẢN PHẨM")
        print("=" * self.LINE_WIDTH)
        print()
        print("  1. Quản lý sản phẩm")
        print("  2. Quản lý nhà cung cấp")
        print("  3. Quản lý nhập / xuất kho")
        print("  4. Tìm kiếm và sắp xếp sản phẩm")
        print("  5. Thống kê và báo cáo")
        print("  6. Kiểm tra hạn sử dụng / bảo hành")
        print("  7. Quản lý dữ liệu (JSON / CSV)")
        print()
        print("  0. Thoát chương trình")
        print()
        print("=" * self.LINE_WIDTH)

    def display_submenu(self, title: str, options: list[MenuOption]) -> None:
        """Hiển thị một menu con theo tiêu đề và danh sách lựa chọn."""
        print("\n" + "-" * self.LINE_WIDTH)
        print(f"  {title}")
        print("-" * self.LINE_WIDTH)
        for key, label, _ in options:
            print(f"  {key}. {label}")
        print("  0. Quay lại menu chính")
        print("-" * self.LINE_WIDTH)

    def run_submenu(self, title: str, options: list[MenuOption]) -> None:
        """Chạy vòng lặp menu con cho đến khi người dùng chọn quay lại (0)."""
        max_choice = max(key for key, _, _ in options)
        handlers = {key: handler for key, _, handler in options}

        while True:
            self.display_submenu(title, options)
            choice = read_menu_choice(0, max_choice)
            if choice == 0:
                print("Đang quay lại menu chính...")
                break
            handlers[choice]()

    def run(self) -> None:
        """Chạy vòng lặp menu chính của chương trình."""
        main_handlers: dict[int, Callable[[], None]] = {
            1: self.open_product_menu,
            2: self.open_supplier_menu,
            3: self.open_stock_menu,
            4: self.open_search_sort_menu,
            5: self.open_report_menu,
            6: self.open_inspection_menu,
            7: self.open_data_menu,
        }

        try:
            while True:
                self.display_main_menu()
                choice = read_menu_choice(0, 7)
                if choice == 0:
                    if confirm_action("Bạn có chắc chắn muốn thoát chương trình? (c/k): "):
                        print("Đã thoát chương trình Quản lý Kho Sản Phẩm. Tạm biệt!")
                        break
                    print("Đã hủy thoát. Quay lại menu chính.")
                    continue

                main_handlers[choice]()
        except UserExitSignal:
            print("Chương trình đã dừng an toàn.")

    # ------------------------------------------------------------------
    # Các menu con (7 nhóm chức năng)
    # ------------------------------------------------------------------

    def open_product_menu(self) -> None:
        """Mở Menu 1 – Quản lý sản phẩm."""
        options: list[MenuOption] = [
            (1, "Thêm sản phẩm", self._handle_add_product),
            (2, "Cập nhật sản phẩm", self._handle_update_product),
            (3, "Xóa sản phẩm", self._handle_delete_product),
            (4, "Hiển thị danh sách sản phẩm", self._handle_list_products),
        ]
        self.run_submenu("MENU 1 – QUẢN LÝ SẢN PHẨM", options)

    def open_supplier_menu(self) -> None:
        """Mở Menu 2 – Quản lý nhà cung cấp."""
        options: list[MenuOption] = [
            (1, "Thêm nhà cung cấp", self._handle_add_supplier),
            (2, "Cập nhật nhà cung cấp", self._handle_update_supplier),
            (3, "Xóa nhà cung cấp", self._handle_delete_supplier),
            (4, "Hiển thị nhà cung cấp", self._handle_list_suppliers),
        ]
        self.run_submenu("MENU 2 – QUẢN LÝ NHÀ CUNG CẤP", options)

    def open_stock_menu(self) -> None:
        """Mở Menu 3 – Quản lý nhập / xuất kho."""
        options: list[MenuOption] = [
            (1, "Nhập kho", self._handle_import_stock),
            (2, "Xuất kho", self._handle_export_stock),
            (3, "Xem lịch sử giao dịch", self._handle_transaction_history),
        ]
        self.run_submenu("MENU 3 – QUẢN LÝ NHẬP / XUẤT KHO", options)

    def open_search_sort_menu(self) -> None:
        """Mở Menu 4 – Tìm kiếm và sắp xếp sản phẩm."""
        options: list[MenuOption] = [
            (1, "Tìm theo mã sản phẩm", self._handle_search_by_id),
            (2, "Tìm theo tên sản phẩm", self._handle_search_by_name),
            (3, "Tìm theo nhà cung cấp", self._handle_search_by_supplier),
            (4, "Sắp xếp theo giá", self._handle_sort_by_price),
            (5, "Sắp xếp theo số lượng tồn kho", self._handle_sort_by_quantity),
        ]
        self.run_submenu("MENU 4 – TÌM KIẾM VÀ SẮP XẾP SẢN PHẨM", options)

    def open_report_menu(self) -> None:
        """Mở Menu 5 – Thống kê và báo cáo."""
        options: list[MenuOption] = [
            (1, "Tổng giá trị tồn kho", self._handle_total_inventory_value),
            (2, "Sản phẩm sắp hết hàng", self._handle_low_stock_products),
            (3, "Thực phẩm gần hết hạn", self._handle_expiring_food_report),
        ]
        self.run_submenu("MENU 5 – THỐNG KÊ VÀ BÁO CÁO", options)

    def open_inspection_menu(self) -> None:
        """Mở Menu 6 – Kiểm tra hạn sử dụng / bảo hành."""
        options: list[MenuOption] = [
            (1, "Kiểm tra hạn sử dụng thực phẩm", self._handle_check_food_expiry),
            (2, "Kiểm tra thời hạn bảo hành thiết bị điện tử", self._handle_check_warranty),
        ]
        self.run_submenu("MENU 6 – KIỂM TRA SẢN PHẨM", options)

    def open_data_menu(self) -> None:
        """Mở Menu 7 – Quản lý dữ liệu (JSON / CSV)."""
        options: list[MenuOption] = [
            (1, "Lưu dữ liệu JSON", self._handle_save_json),
            (2, "Đọc dữ liệu JSON", self._handle_load_json),
            (3, "Xuất báo cáo CSV", self._handle_export_csv),
        ]
        self.run_submenu("MENU 7 – QUẢN LÝ DỮ LIỆU (JSON / CSV)", options)

    # ------------------------------------------------------------------
    # Điểm chờ tích hợp Service (chưa tự ý cài đặt nghiệp vụ thay thành viên)
    # ------------------------------------------------------------------

    def _require_service(self, service: Any, feature_name: str) -> bool:
        """Kiểm tra service đã sẵn sàng chưa; nếu chưa thì thông báo chờ triển khai."""
        if service is None:
            notify_not_implemented(feature_name)
            return False
        return True

    def _handle_add_product(self) -> None:
        self._require_service(self.context.inventory_manager, "Thêm sản phẩm")

    def _handle_update_product(self) -> None:
        self._require_service(self.context.inventory_manager, "Cập nhật sản phẩm")

    def _handle_delete_product(self) -> None:
        self._require_service(self.context.inventory_manager, "Xóa sản phẩm")

    def _handle_list_products(self) -> None:
        self._require_service(self.context.inventory_manager, "Hiển thị danh sách sản phẩm")

    def _handle_add_supplier(self) -> None:
        self._require_service(self.context.report_service, "Thêm nhà cung cấp")

    def _handle_update_supplier(self) -> None:
        self._require_service(self.context.report_service, "Cập nhật nhà cung cấp")

    def _handle_delete_supplier(self) -> None:
        self._require_service(self.context.report_service, "Xóa nhà cung cấp")

    def _handle_list_suppliers(self) -> None:
        self._require_service(self.context.report_service, "Hiển thị nhà cung cấp")

    def _handle_import_stock(self) -> None:
        self._require_service(self.context.stock_service, "Nhập kho")

    def _handle_export_stock(self) -> None:
        self._require_service(self.context.stock_service, "Xuất kho")

    def _handle_transaction_history(self) -> None:
        self._require_service(self.context.stock_service, "Xem lịch sử giao dịch")

    def _handle_search_by_id(self) -> None:
        self._require_service(self.context.inventory_manager, "Tìm theo mã sản phẩm")

    def _handle_search_by_name(self) -> None:
        self._require_service(self.context.inventory_manager, "Tìm theo tên sản phẩm")

    def _handle_search_by_supplier(self) -> None:
        self._require_service(self.context.inventory_manager, "Tìm theo nhà cung cấp")

    def _handle_sort_by_price(self) -> None:
        self._handle_sort_products("Sắp xếp sản phẩm theo giá")

    def _handle_sort_by_quantity(self) -> None:
        self._handle_sort_products("Sắp xếp sản phẩm theo số lượng tồn kho")

    def _handle_sort_products(self, feature_label: str) -> None:
        """Nhận thứ tự sắp xếp tăng/giảm dần trước khi gọi `InventoryManager`."""
        order = read_sort_order()
        if order is None:
            print("Đã hủy thao tác sắp xếp.")
            return
        order_text = "tăng dần" if order == "asc" else "giảm dần"
        self._require_service(
            self.context.inventory_manager,
            f"{feature_label} ({order_text})",
        )

    def _handle_total_inventory_value(self) -> None:
        self._require_service(self.context.report_service, "Tổng giá trị tồn kho")

    def _handle_low_stock_products(self) -> None:
        self._require_service(self.context.report_service, "Sản phẩm sắp hết hàng")

    def _handle_expiring_food_report(self) -> None:
        self._require_service(self.context.report_service, "Thực phẩm gần hết hạn")

    def _handle_check_food_expiry(self) -> None:
        self._require_service(self.context.report_service, "Kiểm tra hạn sử dụng thực phẩm")

    def _handle_check_warranty(self) -> None:
        self._require_service(
            self.context.report_service,
            "Kiểm tra thời hạn bảo hành thiết bị điện tử",
        )

    def _handle_save_json(self) -> None:
        self._require_service(self.context.storage, "Lưu dữ liệu JSON")

    def _handle_load_json(self) -> None:
        self._require_service(self.context.storage, "Đọc dữ liệu JSON")

    def _handle_export_csv(self) -> None:
        self._require_service(self.context.storage, "Xuất báo cáo CSV")


def build_app_context() -> AppContext:
    """Khởi tạo ngữ cảnh dịch vụ cho CLI.

    Khi các module trong `services/` và `storage/` hoàn thiện và thống nhất
    theo `docs/API_CONTRACT.md`, các đối tượng service sẽ được nạp tại đây.
    """
    return AppContext()


def main() -> None:
    """Điểm khởi chạy giao diện Console của ứng dụng."""
    cli = InventoryCLI(context=build_app_context())
    cli.run()
