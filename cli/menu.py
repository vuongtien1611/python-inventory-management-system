"""Hệ thống Menu Console CLI hoàn chỉnh (Design Baseline v1.0).

Người phụ trách: Thành viên 1 - Tiến (nhánh `feature/main-menu`).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Callable

from cli.input_helpers import (
    UserExitSignal,
    confirm_action,
    read_input_safe,
    read_menu_choice,
)
from models.product import ElectronicProduct, FoodProduct, Product
from models.supplier import Supplier
from services.inventory_manager import InventoryManager
from services.report_service import ReportService
from services.stock_service import StockService
from services.supplier_service import SupplierService
from storage import storage as storage_module


@dataclass
class AppContext:
    """Service Container chứa các thể hiện dùng chung của toàn bộ hệ thống."""

    inventory_manager: InventoryManager
    supplier_service: SupplierService
    stock_service: StockService
    report_service: ReportService
    storage: Any = storage_module


class InventoryCLI:
    """Giao diện dòng lệnh (Console CLI) quản lý kho sản phẩm."""

    def __init__(self, context: AppContext) -> None:
        self.context = context
        self._running = True

    # ------------------------------------------------------------------ #
    #  TIỆN ÍCH NHẬP LIỆU VÀ HIỂN THỊ
    # ------------------------------------------------------------------ #

    @staticmethod
    def _read_int(prompt: str, default: int | None = None) -> int:
        while True:
            raw = read_input_safe(prompt)
            if not raw and default is not None:
                return default
            try:
                val = int(raw)
                return val
            except ValueError:
                print("Lỗi: Vui lòng nhập một số nguyên hợp lệ.")

    @staticmethod
    def _read_float(prompt: str, default: float | None = None) -> float:
        while True:
            raw = read_input_safe(prompt)
            if not raw and default is not None:
                return default
            try:
                val = float(raw)
                if val < 0:
                    print("Lỗi: Giá trị không được âm. Vui lòng nhập lại.")
                    continue
                return val
            except ValueError:
                print("Lỗi: Vui lòng nhập một số hợp lệ.")

    # ------------------------------------------------------------------ #
    #  VÒNG LẶP MENU CHÍNH
    # ------------------------------------------------------------------ #

    def run(self) -> None:
        """Khởi chạy vòng lặp menu chính của chương trình."""
        print("\n" + "=" * 65)
        print("  HỆ THỐNG QUẢN LÝ KHO HÀNG SẢN PHẨM (PYTHON OOP CLI v1.0)")
        print("=" * 65)

        while self._running:
            self.display_main_menu()
            try:
                choice = read_menu_choice(0, 7, "Chọn chức năng (0-7): ")
                if choice == 1:
                    self.open_product_menu()
                elif choice == 2:
                    self.open_supplier_menu()
                elif choice == 3:
                    self.open_stock_menu()
                elif choice == 4:
                    self.open_search_sort_menu()
                elif choice == 5:
                    self.open_report_menu()
                elif choice == 6:
                    self.open_inspection_menu()
                elif choice == 7:
                    self.open_data_menu()
                elif choice == 0:
                    if self.handle_exit():
                        break
            except UserExitSignal:
                print("\nĐã ngắt luồng nhập. Đang tiến hành quy trình thoát...")
                self.handle_exit(force_prompt=False)
                break

    def display_main_menu(self) -> None:
        """In danh sách các phân hệ chính."""
        print("\n" + "=" * 50)
        print("               MENU CHÍNH")
        print("=" * 50)
        print("  1. Quản lý danh mục sản phẩm (CRUD)")
        print("  2. Quản lý danh sách nhà cung cấp (CRUD)")
        print("  3. Nghiệp vụ Nhập / Xuất kho & Giao dịch")
        print("  4. Tìm kiếm & Sắp xếp sản phẩm")
        print("  5. Báo cáo & Thống kê tồn kho")
        print("  6. Kiểm tra Hạn sử dụng & Thời hạn bảo hành")
        print("  7. Quản lý dữ liệu hệ thống (JSON / CSV)")
        print("  0. Thoát chương trình")
        print("-" * 50)

    # ------------------------------------------------------------------ #
    #  PHÂN HỆ 1: QUẢN LÝ SẢN PHẨM (UC01 - UC04)
    # ------------------------------------------------------------------ #

    def open_product_menu(self) -> None:
        while True:
            print("\n--- PHÂN HỆ: QUẢN LÝ DANH MỤC SẢN PHẨM ---")
            print("  1. Thêm mới sản phẩm (Tiêu chuẩn / Thực phẩm / Điện tử)")
            print("  2. Cập nhật thông tin sản phẩm (Cấm sửa số lượng)")
            print("  3. Xóa sản phẩm (Ràng buộc tồn kho = 0 & chưa có giao dịch)")
            print("  4. Xem danh sách tất cả sản phẩm")
            print("  0. Quay lại Menu chính")
            choice = read_menu_choice(0, 4, "Chọn (0-4): ")
            if choice == 0:
                break
            elif choice == 1:
                self._handle_add_product()
            elif choice == 2:
                self._handle_update_product()
            elif choice == 3:
                self._handle_delete_product()
            elif choice == 4:
                self._handle_list_products()

    def _handle_add_product(self) -> None:
        print("\n--- THÊM MỚI SẢN PHẨM ---")
        p_id = read_input_safe("Nhập mã sản phẩm: ")
        if not p_id:
            print("Lỗi: Mã sản phẩm không được để trống.")
            return

        name = read_input_safe("Nhập tên sản phẩm: ")
        if not name:
            print("Lỗi: Tên sản phẩm không được để trống.")
            return

        price = self._read_float("Nhập giá sản phẩm: ")

        print("\nChọn loại sản phẩm:")
        print("  1. Sản phẩm tiêu chuẩn (Product)")
        print("  2. Thực phẩm có hạn sử dụng (FoodProduct)")
        print("  3. Thiết bị điện tử có bảo hành (ElectronicProduct)")
        prod_type_choice = read_menu_choice(1, 3, "Chọn loại (1-3): ")

        # Hiển thị danh sách nhà cung cấp để chọn
        sups = self.context.supplier_service.get_all_suppliers()
        sup_id = ""
        if sups:
            print("\nDanh sách nhà cung cấp hiện có:")
            for s in sups:
                print(f"  - [{s.supplier_id}] {s.name}")
            sup_id = read_input_safe("Nhập mã nhà cung cấp (Enter để bỏ trống): ")
        else:
            print("Thông báo: Chưa có nhà cung cấp trong hệ thống. Bạn có thể gán sau.")

        try:
            if prod_type_choice == 2:
                expiry = read_input_safe("Nhập ngày hết hạn (YYYY-MM-DD): ")
                product = FoodProduct(
                    product_id=p_id,
                    name=name,
                    price=price,
                    quantity=0,
                    supplier_id=sup_id,
                    expiry_date=expiry,
                )
            elif prod_type_choice == 3:
                warranty = self._read_int("Nhập số tháng bảo hành: ", default=0)
                product = ElectronicProduct(
                    product_id=p_id,
                    name=name,
                    price=price,
                    quantity=0,
                    supplier_id=sup_id,
                    warranty_months=warranty,
                )
            else:
                product = Product(
                    product_id=p_id,
                    name=name,
                    price=price,
                    quantity=0,
                    supplier_id=sup_id,
                )

            self.context.inventory_manager.add_product(
                product, supplier_service=self.context.supplier_service
            )
            print(f"-> Thêm sản phẩm thành công: {product}")
        except Exception as exc:
            print(f"LỖI: {exc}")

    def _handle_update_product(self) -> None:
        print("\n--- CẬP NHẬT THÔNG TIN SẢN PHẨM ---")
        p_id = read_input_safe("Nhập mã sản phẩm cần sửa: ")
        try:
            p = self.context.inventory_manager.get_product_by_id(p_id)
        except KeyError as exc:
            print(f"LỖI: {exc}")
            return

        print(f"Thông tin hiện tại: {p}")
        print("(Nhấn Enter để giữ nguyên giá trị cũ)")

        new_name = read_input_safe(f"Tên mới [{p.name}]: ")
        price_str = read_input_safe(f"Giá mới [{p.price:,.0f}]: ")
        sup_str = read_input_safe(f"Mã NCC mới [{p.supplier_id}]: ")

        fields: dict[str, Any] = {}
        if new_name:
            fields["name"] = new_name
        if price_str:
            try:
                fields["price"] = float(price_str)
            except ValueError:
                print("Lỗi: Giá nhập không hợp lệ.")
                return
        if sup_str:
            if not self.context.supplier_service.has_supplier(sup_str):
                print(f"Cảnh báo: Nhà cung cấp '{sup_str}' chưa tồn tại trong hệ thống!")
                if not confirm_action("Bạn có chắc chắn muốn gán mã này không? (c/k): "):
                    return
            fields["supplier_id"] = sup_str

        if isinstance(p, FoodProduct):
            exp_str = read_input_safe(f"HSD mới [{p.expiry_date.isoformat()}]: ")
            if exp_str:
                fields["expiry_date"] = exp_str
        elif isinstance(p, ElectronicProduct):
            war_str = read_input_safe(f"Bảo hành mới [{p.warranty_months} tháng]: ")
            if war_str:
                try:
                    fields["warranty_months"] = int(war_str)
                except ValueError:
                    print("Lỗi: Số tháng bảo hành phải là số nguyên.")
                    return

        try:
            self.context.inventory_manager.update_product(p_id, **fields)
            print("-> Cập nhật thông tin sản phẩm thành công!")
        except Exception as exc:
            print(f"LỖI: {exc}")

    def _handle_delete_product(self) -> None:
        print("\n--- XÓA SẢN PHẨM ---")
        p_id = read_input_safe("Nhập mã sản phẩm cần xóa: ")
        try:
            p = self.context.inventory_manager.get_product_by_id(p_id)
        except KeyError as exc:
            print(f"LỖI: {exc}")
            return

        print(f"Sản phẩm chuẩn bị xóa: {p}")
        if not confirm_action(f"Bạn có chắc chắn muốn xóa vĩnh viễn sản phẩm '{p_id}'? (c/k): "):
            print("Đã hủy thao tác xóa.")
            return

        try:
            self.context.inventory_manager.delete_product(
                p_id, stock_service=self.context.stock_service
            )
            print(f"-> Đã xóa thành công sản phẩm: {p_id}")
        except Exception as exc:
            print(f"LỖI TỪ TẦNG NGHIỆP VỤ: {exc}")

    def _handle_list_products(self) -> None:
        print("\n--- DANH SÁCH SẢN PHẨM TRONG KHO ---")
        products = self.context.inventory_manager.get_all_products()
        if not products:
            print("Kho hàng hiện đang trống.")
            return

        print("-" * 85)
        print(f"{'MÃ SP':<10} | {'TÊN SẢN PHẨM':<25} | {'LOẠI':<15} | {'ĐƠN GIÁ':<12} | {'TỒN':<6} | {'THÔNG TIN THÊM'}")
        print("-" * 85)
        for p in products:
            p_type = type(p).__name__
            extra = ""
            if isinstance(p, FoodProduct):
                extra = f"HSD: {p.expiry_date.isoformat()}"
            elif isinstance(p, ElectronicProduct):
                extra = f"BH: {p.warranty_months}T"
            print(f"{p.product_id:<10} | {p.name:<25} | {p_type:<15} | {p.price:>10,.0f} đ | {p.quantity:>4} | {extra}")
        print("-" * 85)
        print(f"Tổng cộng: {len(products)} sản phẩm.")

    # ------------------------------------------------------------------ #
    #  PHÂN HỆ 2: QUẢN LÝ NHÀ CUNG CẤP (UC07)
    # ------------------------------------------------------------------ #

    def open_supplier_menu(self) -> None:
        while True:
            print("\n--- PHÂN HỆ: QUẢN LÝ NHÀ CUNG CẤP ---")
            print("  1. Thêm mới nhà cung cấp")
            print("  2. Cập nhật thông tin nhà cung cấp")
            print("  3. Xóa nhà cung cấp (Ràng buộc không có sản phẩm liên kết)")
            print("  4. Xem danh sách nhà cung cấp")
            print("  0. Quay lại Menu chính")
            choice = read_menu_choice(0, 4, "Chọn (0-4): ")
            if choice == 0:
                break
            elif choice == 1:
                self._handle_add_supplier()
            elif choice == 2:
                self._handle_update_supplier()
            elif choice == 3:
                self._handle_delete_supplier()
            elif choice == 4:
                self._handle_list_suppliers()

    def _handle_add_supplier(self) -> None:
        print("\n--- THÊM NHÀ CUNG CẤP ---")
        s_id = read_input_safe("Nhập mã nhà cung cấp: ")
        name = read_input_safe("Nhập tên nhà cung cấp: ")
        phone = read_input_safe("Nhập số điện thoại: ")
        address = read_input_safe("Nhập địa chỉ: ")
        email = read_input_safe("Nhập email: ")

        try:
            sup = Supplier(
                supplier_id=s_id,
                name=name,
                phone=phone,
                address=address,
                email=email,
            )
            self.context.supplier_service.add_supplier(sup)
            print(f"-> Thêm nhà cung cấp thành công: {sup}")
        except Exception as exc:
            print(f"LỖI: {exc}")

    def _handle_update_supplier(self) -> None:
        print("\n--- CẬP NHẬT NHÀ CUNG CẤP ---")
        s_id = read_input_safe("Nhập mã nhà cung cấp cần sửa: ")
        try:
            sup = self.context.supplier_service.get_supplier_by_id(s_id)
        except KeyError as exc:
            print(f"LỖI: {exc}")
            return

        print(f"Thông tin hiện tại: {sup}")
        name = read_input_safe(f"Tên mới [{sup.name}]: ")
        phone = read_input_safe(f"SĐT mới [{sup.phone}]: ")
        address = read_input_safe(f"Địa chỉ mới [{sup.address}]: ")
        email = read_input_safe(f"Email mới [{sup.email}]: ")

        fields: dict[str, Any] = {}
        if name:
            fields["name"] = name
        if phone:
            fields["phone"] = phone
        if address:
            fields["address"] = address
        if email:
            fields["email"] = email

        try:
            self.context.supplier_service.update_supplier(s_id, **fields)
            print("-> Cập nhật nhà cung cấp thành công!")
        except Exception as exc:
            print(f"LỖI: {exc}")

    def _handle_delete_supplier(self) -> None:
        print("\n--- XÓA NHÀ CUNG CẤP ---")
        s_id = read_input_safe("Nhập mã nhà cung cấp cần xóa: ")
        try:
            sup = self.context.supplier_service.get_supplier_by_id(s_id)
        except KeyError as exc:
            print(f"LỖI: {exc}")
            return

        print(f"Nhà cung cấp: {sup}")
        if not confirm_action(f"Xác nhận xóa nhà cung cấp '{s_id}'? (c/k): "):
            print("Đã hủy thao tác xóa.")
            return

        try:
            self.context.supplier_service.delete_supplier(
                s_id, inventory_manager=self.context.inventory_manager
            )
            print(f"-> Đã xóa thành công nhà cung cấp: {s_id}")
        except Exception as exc:
            print(f"LỖI TỪ TẦNG NGHIỆP VỤ: {exc}")

    def _handle_list_suppliers(self) -> None:
        print("\n--- DANH SÁCH NHÀ CUNG CẤP ---")
        sups = self.context.supplier_service.get_all_suppliers()
        if not sups:
            print("Chưa có nhà cung cấp nào.")
            return
        for s in sups:
            print(f"  {s}")
        print(f"Tổng cộng: {len(sups)} nhà cung cấp.")

    # ------------------------------------------------------------------ #
    #  PHÂN HỆ 3: NGHIỆP VỤ KHO & GIAO DỊCH (UC08 - UC10)
    # ------------------------------------------------------------------ #

    def open_stock_menu(self) -> None:
        while True:
            print("\n--- PHÂN HỆ: NGHIỆP VỤ KHO & GIAO DỊCH ---")
            print("  1. Nhập kho sản phẩm (Tự sinh UUID, từ chối hàng hết hạn, Rollback)")
            print("  2. Xuất kho sản phẩm (Cho phép xuất hết về 0, Rollback an toàn)")
            print("  3. Xem lịch sử giao dịch (Toàn bộ hoặc lọc theo sản phẩm)")
            print("  0. Quay lại Menu chính")
            choice = read_menu_choice(0, 3, "Chọn (0-3): ")
            if choice == 0:
                break
            elif choice == 1:
                self._handle_import_stock()
            elif choice == 2:
                self._handle_export_stock()
            elif choice == 3:
                self._handle_transaction_history()

    def _handle_import_stock(self) -> None:
        print("\n--- NHẬP KHO SẢN PHẨM ---")
        p_id = read_input_safe("Nhập mã sản phẩm: ")
        try:
            p = self.context.inventory_manager.get_product_by_id(p_id)
            print(f"Sản phẩm: {p.name} | Tồn kho hiện tại: {p.quantity}")
        except KeyError as exc:
            print(f"LỖI: {exc}")
            return

        qty = self._read_int("Nhập số lượng cần nhập: ")
        note = read_input_safe("Ghi chú nhập kho: ")

        try:
            tx = self.context.stock_service.import_stock(p_id, qty, note)
            print(f"\n-> NHẬP KHO THÀNH CÔNG!")
            print(f"   Giao dịch: {tx}")
            print(f"   Tồn kho mới: {p.quantity}")
        except Exception as exc:
            print(f"LỖI NGHIỆP VỤ KHO: {exc}")

    def _handle_export_stock(self) -> None:
        print("\n--- XUẤT KHO SẢN PHẨM ---")
        p_id = read_input_safe("Nhập mã sản phẩm: ")
        try:
            p = self.context.inventory_manager.get_product_by_id(p_id)
            print(f"Sản phẩm: {p.name} | Tồn kho hiện tại: {p.quantity}")
        except KeyError as exc:
            print(f"LỖI: {exc}")
            return

        qty = self._read_int("Nhập số lượng cần xuất: ")
        note = read_input_safe("Ghi chú xuất kho: ")

        try:
            tx = self.context.stock_service.export_stock(p_id, qty, note)
            print(f"\n-> XUẤT KHO THÀNH CÔNG!")
            print(f"   Giao dịch: {tx}")
            print(f"   Tồn kho còn lại: {p.quantity}")
        except Exception as exc:
            print(f"LỖI NGHIỆP VỤ KHO: {exc}")

    def _handle_transaction_history(self) -> None:
        print("\n--- LỊCH SỬ GIAO DỊCH KHO HÀNG ---")
        p_id = read_input_safe("Nhập mã sản phẩm cần lọc (Enter để xem toàn bộ): ")
        filter_id = p_id if p_id else None
        history = self.context.stock_service.get_transaction_history(filter_id)

        if not history:
            print("Chưa có giao dịch kho nào phù hợp.")
            return

        print("-" * 90)
        for tx in history:
            print(f"  {tx}")
        print("-" * 90)
        print(f"Tổng số giao dịch: {len(history)}")

    # ------------------------------------------------------------------ #
    #  PHÂN HỆ 4: TÌM KIẾM & SẮP XẾP (UC05, UC06)
    # ------------------------------------------------------------------ #

    def open_search_sort_menu(self) -> None:
        while True:
            print("\n--- PHÂN HỆ: TÌM KIẾM & SẮP XẾP SẢN PHẨM ---")
            print("  1. Tìm kiếm theo Tên sản phẩm (không phân biệt hoa/thường, giữ dấu)")
            print("  2. Tìm kiếm theo Mã sản phẩm")
            print("  3. Tìm kiếm theo Nhà cung cấp")
            print("  4. Sắp xếp theo Đơn giá (Tăng / Giảm)")
            print("  5. Sắp xếp theo Số lượng tồn (Tăng / Giảm)")
            print("  0. Quay lại Menu chính")
            choice = read_menu_choice(0, 5, "Chọn (0-5): ")
            if choice == 0:
                break
            elif choice in {1, 2, 3}:
                by_map = {1: "name", 2: "id", 3: "supplier"}
                keyword = read_input_safe("Nhập từ khóa tìm kiếm: ")
                results = self.context.inventory_manager.search_product(keyword, by=by_map[choice])
                self._print_products_table(results, f"Kết quả tìm kiếm '{keyword}':")
            elif choice in {4, 5}:
                by_map = {4: "price", 5: "quantity"}
                print("Chọn thứ tự:")
                print("  1. Tăng dần")
                print("  2. Giảm dần")
                order_choice = read_menu_choice(1, 2, "Chọn thứ tự (1-2): ")
                rev = (order_choice == 2)
                sorted_list = self.context.inventory_manager.sort_products(by=by_map[choice], reverse=rev)
                self._print_products_table(sorted_list, "Danh sách sau khi sắp xếp:")

    def _print_products_table(self, products: list[Product], title: str) -> None:
        print(f"\n{title}")
        if not products:
            print("  (Không có sản phẩm nào phù hợp)")
            return
        print("-" * 80)
        print(f"{'MÃ SP':<10} | {'TÊN SẢN PHẨM':<25} | {'ĐƠN GIÁ':<12} | {'TỒN':<6} | {'NHÀ CUNG CẤP'}")
        print("-" * 80)
        for p in products:
            print(f"{p.product_id:<10} | {p.name:<25} | {p.price:>10,.0f} đ | {p.quantity:>4} | {p.supplier_id}")
        print("-" * 80)
        print(f"Tổng số: {len(products)} sản phẩm.")

    # ------------------------------------------------------------------ #
    #  PHÂN HỆ 5: BÁO CÁO & THỐNG KÊ (UC11, UC12)
    # ------------------------------------------------------------------ #

    def open_report_menu(self) -> None:
        while True:
            print("\n--- PHÂN HỆ: BÁO CÁO & THỐNG KÊ TỒN KHO ---")
            print("  1. Tổng giá trị hàng tồn kho (Thống kê rủi ro thực phẩm hết hạn)")
            print("  2. Danh sách sản phẩm sắp hết hàng (Theo ngưỡng tồn kho)")
            print("  0. Quay lại Menu chính")
            choice = read_menu_choice(0, 2, "Chọn (0-2): ")
            if choice == 0:
                break
            elif choice == 1:
                res = self.context.report_service.get_total_inventory_value()
                print("\n" + "=" * 50)
                print("        BÁO CÁO TỔNG GIÁ TRỊ TỒN KHO (Q32)")
                print("=" * 50)
                print(f"Tổng giá trị hàng tồn toàn kho : {res['total_value']:>15,.2f} VNĐ")
                if res['has_expired_food']:
                    print(f"CẢNH BÁO RỦI RO HÀNG HẾT HẠN:")
                    print(f"  - Số lượng mặt hàng quá hạn : {res['expired_food_count']:>5} sản phẩm")
                    print(f"  - Giá trị hàng quá hạn      : {res['expired_food_value']:>15,.2f} VNĐ")
                else:
                    print("Tình trạng an toàn: Không có thực phẩm nào bị quá hạn.")
                print("=" * 50)
            elif choice == 2:
                th = self._read_int("Nhập ngưỡng tồn kho cảnh báo [5]: ", default=5)
                low_stock = self.context.report_service.get_low_stock_products(th)
                self._print_products_table(low_stock, f"Sản phẩm có tồn kho <= {th}:")

    # ------------------------------------------------------------------ #
    #  PHÂN HỆ 6: KIỂM TRA HẠN DÙNG & BẢO HÀNH (UC13, UC14)
    # ------------------------------------------------------------------ #

    def open_inspection_menu(self) -> None:
        while True:
            print("\n--- PHÂN HỆ: KIỂM TRA HẠN DÙNG & BẢO HÀNH ---")
            print("  1. Cảnh báo thực phẩm cận hạn sử dụng (Mặc định trong vòng 7 ngày)")
            print("  2. Phân loại chi tiết trạng thái HSD toàn bộ thực phẩm")
            print("  3. Thống kê thông tin bảo hành thiết bị điện tử")
            print("  0. Quay lại Menu chính")
            choice = read_menu_choice(0, 3, "Chọn (0-3): ")
            if choice == 0:
                break
            elif choice == 1:
                days = self._read_int("Nhập số ngày sắp hết hạn cần kiểm tra [7]: ", default=7)
                expiring = self.context.report_service.get_expiring_food_products(days)
                print(f"\nThực phẩm có hạn dùng <= {days} ngày tới (hoặc đã hết hạn):")
                if not expiring:
                    print("  Không có thực phẩm nào cận hạn.")
                else:
                    for f in expiring:
                        print(f"  - [{f.product_id}] {f.name} | HSD: {f.expiry_date.isoformat()} (Còn: {f.days_until_expiry()} ngày) | Tồn: {f.quantity}")
            elif choice == 2:
                p_id = read_input_safe("Mã thực phẩm cần kiểm tra (Enter để xem tất cả): ")
                filter_id = p_id if p_id else None
                details = self.context.report_service.check_food_expiry_status(filter_id)
                print(f"\nChi tiết trạng thái hạn dùng thực phẩm (Q31):")
                if not details:
                    print("  Không có thực phẩm nào.")
                else:
                    print("-" * 75)
                    print(f"{'MÃ SP':<10} | {'TÊN THỰC PHẨM':<25} | {'HSD':<12} | {'CÒN LẠI':<10} | {'TRẠNG THÁI'}")
                    print("-" * 75)
                    for item in details:
                        days_str = f"{item['days_remaining']} ngày"
                        print(f"{item['product_id']:<10} | {item['name']:<25} | {item['expiry_date']:<12} | {days_str:<10} | {item['status']}")
                    print("-" * 75)
            elif choice == 3:
                p_id = read_input_safe("Mã thiết bị điện tử cần kiểm tra (Enter để xem tất cả): ")
                filter_id = p_id if p_id else None
                w_list = self.context.report_service.get_warranty_summary(filter_id)
                print(f"\nThông tin bảo hành thiết bị điện tử (Q11):")
                if not w_list:
                    print("  Không có thiết bị điện tử nào.")
                else:
                    print("-" * 80)
                    print(f"{'MÃ SP':<10} | {'TÊN THIẾT BỊ':<25} | {'BẢO HÀNH':<10} | {'PHÂN CẤP BẢO HÀNH'}")
                    print("-" * 80)
                    for w in w_list:
                        m_str = f"{w['warranty_months']} tháng"
                        print(f"{w['product_id']:<10} | {w['name']:<25} | {m_str:<10} | {w['warranty_tier']}")
                    print("-" * 80)

    # ------------------------------------------------------------------ #
    #  PHÂN HỆ 7: QUẢN LÝ DỮ LIỆU JSON / CSV (UC15 - UC17)
    # ------------------------------------------------------------------ #

    def open_data_menu(self) -> None:
        while True:
            print("\n--- PHÂN HỆ: QUẢN LÝ DỮ LIỆU HỆ THỐNG ---")
            print("  1. Lưu dữ liệu thủ công ra JSON (Ghi nguyên tử cả 3 nhóm)")
            print("  2. Nạp lại dữ liệu từ tệp JSON vào bộ nhớ")
            print("  3. Xuất danh sách sản phẩm ra tệp CSV (7 cột chuẩn)")
            print("  0. Quay lại Menu chính")
            choice = read_menu_choice(0, 3, "Chọn (0-3): ")
            if choice == 0:
                break
            elif choice == 1:
                self._handle_manual_save_json()
            elif choice == 2:
                self._handle_load_json()
            elif choice == 3:
                self._handle_export_csv()

    def _collect_system_state(self) -> dict[str, Any]:
        """Thu thập trạng thái toàn bộ 3 nhóm thực thể để lưu trữ."""
        return {
            "products": self.context.inventory_manager.get_all_products(),
            "suppliers": self.context.supplier_service.get_all_suppliers(),
            "transactions": self.context.stock_service.get_transaction_history(),
        }

    def _handle_manual_save_json(self) -> None:
        path = read_input_safe(f"Đường dẫn lưu JSON [{storage_module.DEFAULT_JSON_PATH}]: ")
        save_path = path if path else storage_module.DEFAULT_JSON_PATH
        try:
            data = self._collect_system_state()
            self.context.storage.save_to_json(data, save_path)
            print(f"-> Đã lưu dữ liệu 3 nhóm thực thể an toàn vào: {save_path}")
        except Exception as exc:
            print(f"LỖI LƯU DỮ LIỆU: {exc}")

    def _handle_load_json(self) -> None:
        path = read_input_safe(f"Đường dẫn nạp JSON [{storage_module.DEFAULT_JSON_PATH}]: ")
        load_path = path if path else storage_module.DEFAULT_JSON_PATH
        if not confirm_action("Cảnh báo: Dữ liệu hiện tại trong bộ nhớ sẽ được thay thế. Tiếp tục? (c/k): "):
            return

        try:
            data = self.context.storage.load_from_json(load_path)
            self.context.inventory_manager.replace_products(data.get("products", []))
            self.context.supplier_service = SupplierService(data.get("suppliers", []))
            self.context.stock_service.replace_transactions(data.get("transactions", []))
            print(f"-> Đã nạp thành công dữ liệu từ {load_path}:")
            print(f"   - Sản phẩm: {len(data.get('products', []))}")
            print(f"   - Nhà cung cấp: {len(data.get('suppliers', []))}")
            print(f"   - Lịch sử giao dịch: {len(data.get('transactions', []))}")
        except Exception as exc:
            print(f"LỖI NẠP DỮ LIỆU (Bộ nhớ được bảo toàn nguyên trạng): {exc}")

    def _handle_export_csv(self) -> None:
        path = read_input_safe(f"Đường dẫn xuất CSV [{storage_module.DEFAULT_CSV_PATH}]: ")
        export_path = path if path else storage_module.DEFAULT_CSV_PATH
        try:
            prods = self.context.inventory_manager.get_all_products()
            self.context.storage.export_to_csv(prods, export_path)
            print(f"-> Xuất báo cáo CSV thành công gồm 7 cột chuẩn vào: {export_path}")
        except Exception as exc:
            print(f"LỖI XUẤT CSV: {exc}")

    # ------------------------------------------------------------------ #
    #  THOÁT CHƯƠNG TRÌNH & TỰ ĐỘNG LƯU AN TOÀN (UC18, SEQUENCE 5)
    # ------------------------------------------------------------------ #

    def handle_exit(self, force_prompt: bool = True) -> bool:
        """Thực hiện quy trình thoát có bảo vệ dữ liệu theo Sequence 5.

        Returns:
            True nếu đồng ý dừng chương trình, False nếu hủy thoát.
        """
        if force_prompt:
            if not confirm_action("Bạn có chắc chắn muốn thoát khỏi hệ thống? (c/k): "):
                print("Đã hủy thao tác thoát. Quay lại Menu chính.")
                return False

        while True:
            try:
                print("Đang tự động lưu toàn bộ dữ liệu phiên làm việc...")
                data = self._collect_system_state()
                self.context.storage.save_to_json(data, storage_module.DEFAULT_JSON_PATH)
                print(f"-> Dữ liệu đã được lưu trữ an toàn vào {storage_module.DEFAULT_JSON_PATH}. Tạm biệt!")
                self._running = False
                return True
            except Exception as exc:
                print(f"\n[CẢNH BÁO] Tự động lưu dữ liệu thất bại: {exc}")
                print("Vui lòng chọn hướng xử lý:")
                print("  1. Thử lưu lại (Retry)")
                print("  2. Hủy thoát (Cancel Exit - quay lại ứng dụng)")
                print("  3. Xác nhận thoát không lưu (Force Exit)")
                err_choice = read_menu_choice(1, 3, "Chọn phương án (1-3): ")

                if err_choice == 1:
                    print("Đang thử lưu lại...")
                    continue
                elif err_choice == 2:
                    print("Đã hủy thoát. Bạn có thể kiểm tra ổ đĩa hoặc lưu thủ công.")
                    return False
                elif err_choice == 3:
                    if confirm_action("CẢNH BÁO: Dữ liệu chưa lưu có thể bị mất vĩnh viễn! Vẫn thoát? (c/k): "):
                        print("Đã thoát chương trình (không lưu các thay đổi mới).")
                        self._running = False
                        return True
                    else:
                        print("Đã hủy thoát không lưu. Quay lại Menu chính.")
                        return False


def build_app_context() -> AppContext:
    """Khởi tạo AppContext kết nối đầy đủ 5 dịch vụ thực tế và nạp dữ liệu ban đầu."""
    im = InventoryManager()
    sup = SupplierService()
    stk = StockService(im)
    rep = ReportService(im)

    # Nạp dữ liệu cũ nếu tệp JSON tồn tại
    try:
        data = storage_module.load_from_json(storage_module.DEFAULT_JSON_PATH)
        prods = data.get("products", [])
        sups = data.get("suppliers", [])
        txs = data.get("transactions", [])

        im.replace_products(prods)
        sup = SupplierService(sups)
        stk = StockService(im, txs)
        rep = ReportService(im)
    except Exception as exc:
        print(f"Thông báo: Khởi tạo hệ thống mới (Không nạp tệp cũ: {exc}).")

    return AppContext(
        inventory_manager=im,
        supplier_service=sup,
        stock_service=stk,
        report_service=rep,
        storage=storage_module,
    )


def main() -> None:
    """Điểm khởi nhập chính của ứng dụng quản lý kho."""
    context = build_app_context()
    cli = InventoryCLI(context)
    cli.run()


if __name__ == "__main__":
    main()
