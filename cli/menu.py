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
    read_input_safe,
    read_menu_choice,
    read_sort_order,
)
from models.product import Product
from services.inventory_manager import InventoryManager
from services.report_service import ReportService
from services.stock_service import StockService
from storage import storage as storage_module

MenuOption = tuple[int, str, Callable[[], None]]
_ACTION_FAILED = object()


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

    @staticmethod
    def _read_int(prompt: str, default: int | None = None) -> int:
        while True:
            raw = read_input_safe(prompt)
            if not raw and default is not None:
                return default
            try:
                return int(raw)
            except ValueError:
                print("Vui lòng nhập một số nguyên hợp lệ.")

    @staticmethod
    def _run_action(action: Callable[[], Any]) -> Any:
        try:
            return action()
        except (ValueError, KeyError, TypeError, OSError) as exc:
            print(f"Lỗi: {exc}")
            return _ACTION_FAILED

    @staticmethod
    def _print_products(products: list[Any]) -> None:
        if not products:
            print("Không có dữ liệu phù hợp.")
            return
        for product in products:
            print(product)

    def _handle_add_product(self) -> None:
        manager = self.context.inventory_manager
        if not self._require_service(manager, "Thêm sản phẩm"):
            return
        product_id = read_input_safe("Mã sản phẩm: ")
        name = read_input_safe("Tên sản phẩm: ")
        price = self._read_int("Đơn giá: ")
        quantity = self._read_int("Số lượng tồn: ")
        supplier = read_input_safe("Nhà cung cấp: ")
        result = self._run_action(lambda: manager.add_product(Product(product_id, name, price, quantity, supplier)))
        if result is not _ACTION_FAILED and manager.get_product_by_id(product_id):
            print("Đã thêm sản phẩm.")

    def _handle_update_product(self) -> None:
        manager = self.context.inventory_manager
        if not self._require_service(manager, "Cập nhật sản phẩm"):
            return
        product_id = read_input_safe("Mã sản phẩm cần cập nhật: ")
        product = manager.get_product_by_id(product_id)
        if product is None:
            print("Không tìm thấy sản phẩm.")
            return
        name = read_input_safe(f"Tên [{product.name}]: ")
        price_raw = read_input_safe(f"Đơn giá [{product.price}]: ")
        quantity_raw = read_input_safe(f"Số lượng [{product.quantity}]: ")
        supplier = read_input_safe(f"Nhà cung cấp [{product.supplier}]: ")
        fields: dict[str, Any] = {}
        if name: fields["name"] = name
        try:
            if price_raw: fields["price"] = int(price_raw)
            if quantity_raw: fields["quantity"] = int(quantity_raw)
        except ValueError:
            print("Đơn giá và số lượng phải là số nguyên.")
            return
        if supplier: fields["supplier"] = supplier
        if self._run_action(lambda: manager.update_product(product_id, **fields)) is not _ACTION_FAILED:
            print("Đã cập nhật sản phẩm.")

    def _handle_delete_product(self) -> None:
        manager = self.context.inventory_manager
        if self._require_service(manager, "Xóa sản phẩm"):
            product_id = read_input_safe("Mã sản phẩm cần xóa: ")
            if self._run_action(lambda: manager.delete_product(product_id)) is not _ACTION_FAILED:
                print("Đã xóa sản phẩm.")

    def _handle_list_products(self) -> None:
        if self._require_service(self.context.inventory_manager, "Hiển thị danh sách sản phẩm"):
            self._print_products(self.context.inventory_manager.get_all_products())

    def _handle_add_supplier(self) -> None:
        self._require_service(self.context.report_service, "Thêm nhà cung cấp")

    def _handle_update_supplier(self) -> None:
        self._require_service(self.context.report_service, "Cập nhật nhà cung cấp")

    def _handle_delete_supplier(self) -> None:
        self._require_service(self.context.report_service, "Xóa nhà cung cấp")

    def _handle_list_suppliers(self) -> None:
        self._require_service(self.context.report_service, "Hiển thị nhà cung cấp")

    def _handle_import_stock(self) -> None:
        service = self.context.stock_service
        if self._require_service(service, "Nhập kho"):
            product_id = read_input_safe("Mã sản phẩm: ")
            quantity = self._read_int("Số lượng nhập: ")
            note = read_input_safe("Ghi chú: ")
            result = self._run_action(lambda: service.import_stock(product_id, quantity, note))
            if result is not _ACTION_FAILED: print("Đã nhập kho.")

    def _handle_export_stock(self) -> None:
        service = self.context.stock_service
        if self._require_service(service, "Xuất kho"):
            product_id = read_input_safe("Mã sản phẩm: ")
            quantity = self._read_int("Số lượng xuất: ")
            note = read_input_safe("Ghi chú: ")
            result = self._run_action(lambda: service.export_stock(product_id, quantity, note))
            if result is not _ACTION_FAILED: print("Đã xuất kho.")

    def _handle_transaction_history(self) -> None:
        service = self.context.stock_service
        if self._require_service(service, "Xem lịch sử giao dịch"):
            for transaction in service.get_transaction_history(): print(transaction)

    def _handle_search_by_id(self) -> None:
        self._search("id", "Tìm theo mã sản phẩm")

    def _handle_search_by_name(self) -> None:
        self._search("name", "Tìm theo tên sản phẩm")

    def _handle_search_by_supplier(self) -> None:
        self._search("supplier", "Tìm theo nhà cung cấp")

    def _search(self, by: str, label: str) -> None:
        manager = self.context.inventory_manager
        if self._require_service(manager, label):
            keyword = read_input_safe("Từ khóa: ")
            products = self._run_action(lambda: manager.search_product(keyword, by=by))
            if products is not _ACTION_FAILED: self._print_products(products)

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
        manager = self.context.inventory_manager
        if not self._require_service(manager, f"{feature_label} ({order_text})"):
            return
        by = "quantity" if "số lượng" in feature_label.lower() else "price"
        products = self._run_action(lambda: manager.sort_products(by=by, reverse=(order == "desc")))
        if products is not _ACTION_FAILED: self._print_products(products)

    def _handle_total_inventory_value(self) -> None:
        service = self.context.report_service
        if self._require_service(service, "Tổng giá trị tồn kho"):
            value = self._run_action(service.get_total_inventory_value)
            if value is not _ACTION_FAILED: print(f"Tổng giá trị tồn kho: {value:,.0f} VNĐ")

    def _handle_low_stock_products(self) -> None:
        service = self.context.report_service
        if self._require_service(service, "Sản phẩm sắp hết hàng"):
            threshold = self._read_int("Ngưỡng tồn kho [5]: ", 5)
            products = self._run_action(lambda: service.get_low_stock_products(threshold))
            if products is not _ACTION_FAILED: self._print_products(products)

    def _handle_expiring_food_report(self) -> None:
        service = self.context.report_service
        if self._require_service(service, "Thực phẩm gần hết hạn"):
            days = self._read_int("Số ngày sắp hết hạn [7]: ", 7)
            products = self._run_action(lambda: service.get_expiring_food_products(days))
            if products is not _ACTION_FAILED: self._print_products(products)

    def _handle_check_food_expiry(self) -> None:
        service = self.context.report_service
        if self._require_service(service, "Kiểm tra hạn sử dụng thực phẩm"):
            product_id = read_input_safe("Mã sản phẩm (Enter để xem tất cả): ") or None
            results = self._run_action(lambda: service.check_food_expiry_status(product_id))
            if results is not _ACTION_FAILED:
                for item in results: print(item)

    def _handle_check_warranty(self) -> None:
        service = self.context.report_service
        if self._require_service(service, "Kiểm tra thời hạn bảo hành thiết bị điện tử"):
            product_id = read_input_safe("Mã sản phẩm (Enter để xem tất cả): ") or None
            results = self._run_action(lambda: service.get_warranty_summary(product_id))
            if results is not _ACTION_FAILED:
                for item in results: print(item)

    def _handle_save_json(self) -> None:
        if self._require_service(self.context.storage, "Lưu dữ liệu JSON"):
            path = read_input_safe("Đường dẫn JSON [data/products.json]: ") or "data/products.json"
            result = self._run_action(lambda: self.context.storage.save_to_json(self.context.inventory_manager.get_all_products(), path))
            if result is not _ACTION_FAILED: print(f"Đã lưu dữ liệu JSON: {path}")

    def _handle_load_json(self) -> None:
        if self._require_service(self.context.storage, "Đọc dữ liệu JSON"):
            path = read_input_safe("Đường dẫn JSON [data/products.json]: ") or "data/products.json"
            products = self._run_action(lambda: self.context.storage.load_from_json(path))
            if products is not _ACTION_FAILED:
                self.context.inventory_manager.replace_products(products)
                print(f"Đã nạp {len(products)} sản phẩm.")

    def _handle_export_csv(self) -> None:
        if self._require_service(self.context.storage, "Xuất báo cáo CSV"):
            path = read_input_safe("Đường dẫn CSV [data/inventory_report.csv]: ") or "data/inventory_report.csv"
            result = self._run_action(lambda: self.context.storage.export_to_csv(self.context.inventory_manager.get_all_products(), path))
            if result is not _ACTION_FAILED: print(f"Đã xuất CSV: {path}")


def build_app_context() -> AppContext:
    """Khởi tạo ngữ cảnh dịch vụ cho CLI.

    Khi các module trong `services/` và `storage/` hoàn thiện và thống nhất
    theo `docs/API_CONTRACT.md`, các đối tượng service sẽ được nạp tại đây.
    """
    manager = InventoryManager()
    try:
        manager.replace_products(storage_module.load_from_json())
    except (OSError, ValueError) as exc:
        print(f"Không thể nạp dữ liệu kho: {exc}")
    return AppContext(
        inventory_manager=manager,
        stock_service=StockService(manager),
        report_service=ReportService(manager),
        storage=storage_module,
    )


def main() -> None:
    """Điểm khởi chạy giao diện Console của ứng dụng."""
    cli = InventoryCLI(context=build_app_context())
    cli.run()
