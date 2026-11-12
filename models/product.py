"""Module định nghĩa các lớp mô hình sản phẩm trong kho hàng.

Người phụ trách: Thành viên 2 - Lâm (nhánh `feature/product-models`).

Các lớp dự kiến triển khai:
- `Product`: Lớp cơ sở cho sản phẩm.
- `FoodProduct`: Lớp sản phẩm thực phẩm kế thừa từ `Product`.
- `ElectronicProduct`: Lớp sản phẩm điện tử kế thừa từ `Product`.

Các phương thức dự kiến:
- `__init__()`
- `__str__()`
- `is_valid()`
- `get_inventory_value()`

Yêu cầu thiết kế OOP:
- Thể hiện tính kế thừa (`FoodProduct`, `ElectronicProduct` kế thừa `Product`).
- Thể hiện tính đa hình thông qua ghi đè phương thức (`__str__`, `is_valid`, `get_inventory_value`, ...).
- Thể hiện tính đóng gói dữ liệu (thuộc tính private/protected kết hợp `@property` hoặc getter/setter).
- Kiểm tra tính hợp lệ của dữ liệu đầu vào.

TODO (Lâm):
- [ ] Thiết kế và cài đặt lớp cơ sở `Product` với đầy đủ `@property` / getter-setter và validation.
- [ ] Thiết kế và cài đặt lớp `FoodProduct` (thêm thuộc tính hạn sử dụng, ghi đè phương thức cần thiết).
- [ ] Thiết kế và cài đặt lớp `ElectronicProduct` (thêm thuộc tính thời gian bảo hành, ghi đè phương thức cần thiết).
- [ ] Export các lớp trong `models/__init__.py` sau khi hoàn thành để các module khác import thuận tiện.
"""

