"""Module thống kê, báo cáo kho hàng và quản lý nghiệp vụ nhà cung cấp.

Người phụ trách: Thành viên 5 - Minh (nhánh `feature/supplier-reports`).

Lớp triển khai:
- ``ReportService``: Cung cấp các chức năng:
  • Quản lý danh sách nhà cung cấp (CRUD ``Supplier``).
  • Tính tổng giá trị hàng tồn kho.
  • Thống kê sản phẩm sắp hết hàng (theo ngưỡng tồn kho).
  • Thống kê thực phẩm (``FoodProduct``) gần hết hạn / đã hết hạn.
  • Thống kê thông tin bảo hành của thiết bị điện tử (``ElectronicProduct``).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

# Import models — các lớp do Lâm (product.py) và Minh (supplier.py) xây dựng.
# Vì các thành viên khác có thể chưa hoàn thành code, ta import có xử lý lỗi
# để module vẫn load được trong quá trình phát triển song song.
try:
    from models.product import Product, FoodProduct, ElectronicProduct
except ImportError:  # pragma: no cover
    # Fallback: tạo placeholder khi models chưa được triển khai bởi Lâm.
    Product = None  # type: ignore[assignment, misc]
    FoodProduct = None  # type: ignore[assignment, misc]
    ElectronicProduct = None  # type: ignore[assignment, misc]

from models.supplier import Supplier


class ReportService:
    """Lớp cung cấp dịch vụ thống kê, báo cáo kho hàng
    và quản lý danh sách nhà cung cấp.

    Attributes:
        inventory_manager: Đối tượng ``InventoryManager`` (do Sơn xây dựng)
            dùng để truy xuất ``get_all_products()`` và
            ``get_product_by_id()``.
        _suppliers (dict[str, Supplier]): Danh sách nhà cung cấp quản lý
            nội bộ, key là ``supplier_id``.
    """

    def __init__(
        self,
        inventory_manager: Any,
        suppliers: list[Supplier] | None = None,
    ) -> None:
        """Khởi tạo ReportService.

        Args:
            inventory_manager: Đối tượng ``InventoryManager`` cung cấp
                ``get_all_products()`` và ``get_product_by_id()``.
            suppliers: Danh sách ``Supplier`` ban đầu (tùy chọn).

        Raises:
            TypeError: Nếu ``inventory_manager`` là ``None``.
        """
        if inventory_manager is None:
            raise TypeError(
                "inventory_manager không được là None. "
                "Hãy truyền đối tượng InventoryManager hợp lệ."
            )
        self._inventory_manager = inventory_manager
        self._suppliers: dict[str, Supplier] = {}
        if suppliers:
            for s in suppliers:
                if isinstance(s, Supplier) and s.is_valid():
                    self._suppliers[s.supplier_id] = s

    # ================================================================== #
    #  PHẦN 1: QUẢN LÝ NHÀ CUNG CẤP (CRUD — Menu 2)
    # ================================================================== #

    def add_supplier(self, supplier: Supplier) -> None:
        """Thêm một nhà cung cấp vào danh sách.

        Args:
            supplier: Đối tượng ``Supplier`` cần thêm.

        Raises:
            TypeError: Nếu ``supplier`` không phải là instance của ``Supplier``.
            ValueError: Nếu ``supplier`` không hợp lệ hoặc ``supplier_id``
                        đã tồn tại trong danh sách.
        """
        if not isinstance(supplier, Supplier):
            raise TypeError(
                "Đối tượng truyền vào phải là instance của lớp Supplier."
            )
        if not supplier.is_valid():
            raise ValueError(
                "Thông tin nhà cung cấp không hợp lệ. "
                "Vui lòng kiểm tra lại dữ liệu."
            )
        if supplier.supplier_id in self._suppliers:
            raise ValueError(
                f"Mã nhà cung cấp '{supplier.supplier_id}' đã tồn tại. "
                "Không thể thêm trùng mã."
            )
        self._suppliers[supplier.supplier_id] = supplier

    def update_supplier(self, supplier_id: str, **fields: Any) -> None:
        """Cập nhật thông tin nhà cung cấp theo ``supplier_id``.

        Hỗ trợ cập nhật các trường: ``name``, ``phone``, ``address``,
        ``email``. Trường ``supplier_id`` không được phép thay đổi.

        Args:
            supplier_id: Mã nhà cung cấp cần cập nhật.
            **fields: Các trường cần cập nhật (ví dụ
                      ``name="ABC"``, ``phone="0912345678"``).

        Raises:
            KeyError: Nếu ``supplier_id`` không tồn tại.
            ValueError: Nếu giá trị cập nhật không hợp lệ hoặc cố gắng
                        thay đổi ``supplier_id``.
        """
        if supplier_id not in self._suppliers:
            raise KeyError(
                f"Không tìm thấy nhà cung cấp với mã '{supplier_id}'."
            )
        if "supplier_id" in fields:
            raise ValueError("Không được phép thay đổi mã nhà cung cấp.")

        supplier = self._suppliers[supplier_id]
        allowed_fields = {"name", "phone", "address", "email"}
        invalid_fields = set(fields.keys()) - allowed_fields
        if invalid_fields:
            raise ValueError(
                f"Trường không hợp lệ: {', '.join(invalid_fields)}. "
                f"Các trường được phép cập nhật: {', '.join(sorted(allowed_fields))}."
            )

        # Lưu giá trị cũ để rollback nếu có lỗi
        old_values: dict[str, Any] = {}
        for key in fields:
            old_values[key] = getattr(supplier, key)

        try:
            for key, value in fields.items():
                setattr(supplier, key, value)
        except (TypeError, ValueError) as err:
            # Rollback: khôi phục giá trị cũ
            for key, old_val in old_values.items():
                try:
                    setattr(supplier, key, old_val)
                except Exception:  # pragma: no cover
                    pass
            raise ValueError(
                f"Cập nhật nhà cung cấp thất bại: {err}"
            ) from err

    def delete_supplier(self, supplier_id: str) -> None:
        """Xóa nhà cung cấp khỏi danh sách.

        Kiểm tra xem có sản phẩm nào trong kho đang tham chiếu đến
        nhà cung cấp này không. Nếu có, từ chối xóa.

        Args:
            supplier_id: Mã nhà cung cấp cần xóa.

        Raises:
            KeyError: Nếu ``supplier_id`` không tồn tại.
            ValueError: Nếu nhà cung cấp đang được sản phẩm trong kho
                        tham chiếu.
        """
        if supplier_id not in self._suppliers:
            raise KeyError(
                f"Không tìm thấy nhà cung cấp với mã '{supplier_id}'."
            )

        # Kiểm tra sản phẩm liên kết — sử dụng get_all_products() từ
        # InventoryManager (do Sơn xây dựng).
        try:
            all_products = self._inventory_manager.get_all_products()
        except Exception:
            # Nếu InventoryManager chưa sẵn sàng, cho phép xóa
            all_products = []

        linked_products = []
        for product in all_products:
            # Thuộc tính supplier trên Product lưu supplier_id hoặc tên NCC
            product_supplier = getattr(product, "supplier", "") or ""
            product_supplier_id = getattr(product, "supplier_id", "") or ""
            if supplier_id in (product_supplier, product_supplier_id):
                linked_products.append(product)

        if linked_products:
            product_names = ", ".join(
                getattr(p, "name", getattr(p, "product_id", "?"))
                for p in linked_products
            )
            raise ValueError(
                f"Không thể xóa nhà cung cấp '{supplier_id}' vì đang có "
                f"{len(linked_products)} sản phẩm liên kết: {product_names}. "
                "Hãy xóa hoặc chuyển đổi nhà cung cấp cho các sản phẩm này "
                "trước khi xóa."
            )

        del self._suppliers[supplier_id]

    def get_all_suppliers(self) -> list[Supplier]:
        """Trả về danh sách tất cả nhà cung cấp.

        Returns:
            Bản sao danh sách các đối tượng ``Supplier``. Trả về ``[]``
            nếu chưa có nhà cung cấp nào.
        """
        return list(self._suppliers.values())

    def get_supplier_by_id(self, supplier_id: str) -> Supplier | None:
        """Tìm nhà cung cấp theo mã.

        Args:
            supplier_id: Mã nhà cung cấp cần tìm.

        Returns:
            Đối tượng ``Supplier`` nếu tìm thấy, ``None`` nếu không.
        """
        return self._suppliers.get(supplier_id)

    # ================================================================== #
    #  PHẦN 2: THỐNG KÊ & BÁO CÁO (Menu 5 & Menu 6)
    # ================================================================== #

    def get_total_inventory_value(self) -> float:
        """Tính tổng giá trị hàng tồn kho.

        Sử dụng ``product.get_inventory_value()`` (do Lâm xây dựng
        trong ``models/product.py``) cho từng sản phẩm, sau đó cộng
        tổng lại.

        Returns:
            Tổng giá trị tồn kho (``float``). Trả về ``0.0`` nếu kho
            rỗng.
        """
        try:
            all_products = self._inventory_manager.get_all_products()
        except Exception:
            return 0.0

        if not all_products:
            return 0.0

        total = 0.0
        for product in all_products:
            try:
                total += product.get_inventory_value()
            except (AttributeError, TypeError):
                # Bỏ qua sản phẩm không có phương thức get_inventory_value
                continue
        return total

    def get_low_stock_products(self, threshold: int = 5) -> list[Any]:
        """Trả về danh sách sản phẩm có tồn kho thấp (sắp hết hàng).

        Args:
            threshold: Ngưỡng tồn kho tối đa để coi là sắp hết hàng.
                       Mặc định là ``5``.

        Returns:
            Danh sách ``Product`` có ``quantity <= threshold``.

        Raises:
            ValueError: Nếu ``threshold`` không phải số nguyên hoặc < 0.
        """
        if not isinstance(threshold, int) or isinstance(threshold, bool):
            raise ValueError(
                f"Ngưỡng tồn kho phải là số nguyên (int), "
                f"nhận được: {type(threshold).__name__}."
            )
        if threshold < 0:
            raise ValueError(
                f"Ngưỡng tồn kho không được âm (nhận được: {threshold})."
            )

        try:
            all_products = self._inventory_manager.get_all_products()
        except Exception:
            return []

        result = []
        for product in all_products:
            try:
                qty = product.quantity
                if isinstance(qty, int) and qty <= threshold:
                    result.append(product)
            except AttributeError:
                continue
        return result

    def get_expiring_food_products(self, days: int = 7) -> list[Any]:
        """Trả về danh sách thực phẩm sắp hết hạn trong ``days`` ngày tới
        hoặc đã hết hạn.

        Args:
            days: Số ngày tới để kiểm tra (mặc định ``7``).

        Returns:
            Danh sách ``FoodProduct`` có hạn sử dụng <= ``days`` ngày
            kể từ hôm nay (bao gồm cả sản phẩm đã hết hạn).

        Raises:
            ValueError: Nếu ``days`` không phải số nguyên hoặc < 0.
        """
        if not isinstance(days, int) or isinstance(days, bool):
            raise ValueError(
                f"Số ngày phải là số nguyên (int), "
                f"nhận được: {type(days).__name__}."
            )
        if days < 0:
            raise ValueError(
                f"Số ngày không được âm (nhận được: {days})."
            )

        try:
            all_products = self._inventory_manager.get_all_products()
        except Exception:
            return []

        today = date.today()
        deadline = today + timedelta(days=days)
        result = []

        for product in all_products:
            # Chỉ xét FoodProduct (kiểm tra bằng tên class để tương thích
            # khi FoodProduct chưa được import thành công)
            if not self._is_food_product(product):
                continue
            try:
                expiry = self._parse_expiry_date(product)
                if expiry is None:
                    continue
                if expiry <= deadline:
                    result.append(product)
            except Exception:
                # Bỏ qua sản phẩm có ngày hết hạn không xử lý được
                continue
        return result

    def check_food_expiry_status(
        self, product_id: str | None = None
    ) -> list[dict[str, Any]]:
        """Kiểm tra và phân loại trạng thái hạn sử dụng của thực phẩm.

        Phân loại thành 3 trạng thái:
        - ``"Còn hạn"``: hạn sử dụng > 7 ngày kể từ hôm nay.
        - ``"Gần hết hạn"``: hạn sử dụng trong vòng 0–7 ngày.
        - ``"Đã hết hạn"``: hạn sử dụng đã qua.

        Args:
            product_id: Nếu cung cấp, chỉ kiểm tra sản phẩm có mã này.
                        Nếu ``None``, kiểm tra tất cả thực phẩm.

        Returns:
            Danh sách ``dict`` chứa thông tin trạng thái, mỗi phần tử gồm:
            ``{"product_id", "name", "expiry_date", "days_remaining",
            "status"}``.
        """
        try:
            all_products = self._inventory_manager.get_all_products()
        except Exception:
            return []

        today = date.today()
        result = []

        for product in all_products:
            if not self._is_food_product(product):
                continue
            if product_id is not None:
                pid = getattr(product, "product_id", None)
                if pid != product_id:
                    continue

            try:
                expiry = self._parse_expiry_date(product)
                if expiry is None:
                    continue

                days_remaining = (expiry - today).days

                if days_remaining < 0:
                    status = "Đã hết hạn"
                elif days_remaining <= 7:
                    status = "Gần hết hạn"
                else:
                    status = "Còn hạn"

                expiry_str = getattr(product, "expiry_date", "")
                if isinstance(expiry_str, date):
                    expiry_str = expiry_str.isoformat()

                result.append({
                    "product_id": getattr(product, "product_id", ""),
                    "name": getattr(product, "name", ""),
                    "expiry_date": str(expiry_str),
                    "days_remaining": days_remaining,
                    "status": status,
                })
            except Exception:
                # Bỏ qua sản phẩm có lỗi khi xử lý ngày
                continue

        return result

    def get_warranty_summary(
        self, product_id: str | None = None
    ) -> list[dict[str, Any]]:
        """Thống kê thông tin bảo hành của thiết bị điện tử.

        Args:
            product_id: Nếu cung cấp, chỉ thống kê sản phẩm có mã này.
                        Nếu ``None``, thống kê tất cả ``ElectronicProduct``.

        Returns:
            Danh sách ``dict`` chứa thông tin bảo hành, mỗi phần tử gồm:
            ``{"product_id", "name", "warranty_months", "warranty_years",
            "warranty_status"}``.
        """
        try:
            all_products = self._inventory_manager.get_all_products()
        except Exception:
            return []

        result = []

        for product in all_products:
            if not self._is_electronic_product(product):
                continue
            if product_id is not None:
                pid = getattr(product, "product_id", None)
                if pid != product_id:
                    continue

            try:
                warranty_months = getattr(product, "warranty_months", 0)
                if not isinstance(warranty_months, int):
                    warranty_months = 0

                warranty_years = round(warranty_months / 12, 1)

                if warranty_months <= 0:
                    warranty_status = "Không có bảo hành"
                elif warranty_months <= 6:
                    warranty_status = "Bảo hành ngắn hạn"
                elif warranty_months <= 24:
                    warranty_status = "Bảo hành tiêu chuẩn"
                else:
                    warranty_status = "Bảo hành dài hạn"

                result.append({
                    "product_id": getattr(product, "product_id", ""),
                    "name": getattr(product, "name", ""),
                    "warranty_months": warranty_months,
                    "warranty_years": warranty_years,
                    "warranty_status": warranty_status,
                })
            except Exception:
                continue

        return result

    # ================================================================== #
    #  PHẦN 3: HÀM TRỢ GIÚP NỘI BỘ (private)
    # ================================================================== #

    @staticmethod
    def _is_food_product(product: Any) -> bool:
        """Kiểm tra ``product`` có phải là ``FoodProduct`` không.

        Kiểm tra bằng ``isinstance`` nếu ``FoodProduct`` đã được import
        thành công, nếu không thì dựa vào tên lớp.
        """
        if FoodProduct is not None:
            return isinstance(product, FoodProduct)
        return type(product).__name__ == "FoodProduct"

    @staticmethod
    def _is_electronic_product(product: Any) -> bool:
        """Kiểm tra ``product`` có phải là ``ElectronicProduct`` không.

        Kiểm tra bằng ``isinstance`` nếu ``ElectronicProduct`` đã được
        import thành công, nếu không thì dựa vào tên lớp.
        """
        if ElectronicProduct is not None:
            return isinstance(product, ElectronicProduct)
        return type(product).__name__ == "ElectronicProduct"

    @staticmethod
    def _parse_expiry_date(product: Any) -> date | None:
        """Phân tích giá trị ``expiry_date`` từ ``product`` thành ``date``.

        Hỗ trợ cả ``str`` (định dạng ``YYYY-MM-DD``) và ``datetime.date``.

        Args:
            product: Đối tượng sản phẩm có thuộc tính ``expiry_date``.

        Returns:
            Đối tượng ``date`` nếu phân tích thành công, ``None`` nếu
            không có hoặc không hợp lệ.
        """
        expiry_raw = getattr(product, "expiry_date", None)
        if expiry_raw is None:
            return None
        if isinstance(expiry_raw, date):
            return expiry_raw
        if isinstance(expiry_raw, str):
            expiry_raw = expiry_raw.strip()
            if not expiry_raw:
                return None
            try:
                return datetime.strptime(expiry_raw, "%Y-%m-%d").date()
            except ValueError:
                return None
        return None
