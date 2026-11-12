"""Module thống kê, báo cáo kho hàng và quản lý nghiệp vụ nhà cung cấp.

Người phụ trách: Thành viên 5 - Minh (nhánh `feature/supplier-reports`).

Lớp dự kiến triển khai:
- `ReportService` (và hỗ trợ quản lý danh sách `Supplier`).

Các chức năng dự kiến:
- Quản lý thông tin nhà cung cấp (thêm, xem, tìm kiếm nhà cung cấp).
- Tính tổng giá trị hàng tồn kho.
- Thống kê danh sách sản phẩm sắp hết hàng (theo ngưỡng tồn kho).
- Thống kê sản phẩm thực phẩm (`FoodProduct`) gần hết hạn sử dụng.
- Thống kê thông tin bảo hành của các thiết bị điện tử (`ElectronicProduct`).

TODO (Minh):
- [ ] Cài đặt chức năng quản lý danh sách nhà cung cấp (`Supplier`).
- [ ] Cài đặt lớp `ReportService` với các phương thức thống kê tổng giá trị tồn kho.
- [ ] Cài đặt thống kê sản phẩm sắp hết hàng.
- [ ] Cài đặt thống kê thực phẩm gần hết hạn.
- [ ] Cài đặt thống kê thông tin bảo hành thiết bị điện tử.
"""

