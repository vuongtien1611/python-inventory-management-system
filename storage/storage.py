"""Module đọc/ghi dữ liệu sản phẩm ra JSON và xuất báo cáo CSV.

Người phụ trách: Thành viên 6 - Tú (nhánh `feature/storage-testing`).

Các chức năng dự kiến:
- Lưu danh sách sản phẩm ra file JSON trong thư mục `data/`.
- Đọc dữ liệu từ file JSON và khôi phục đúng loại đối tượng (`Product`, `FoodProduct`, `ElectronicProduct`).
- Xuất danh sách sản phẩm hoặc báo cáo thống kê ra file CSV.

TODO (Tú):
- [ ] Thiết kế hàm hoặc lớp lưu trữ hỗ trợ ghi dữ liệu sản phẩm ra JSON (encoding UTF-8).
- [ ] Cài đặt đọc JSON và khôi phục đúng kiểu đối tượng kế thừa (`Product`, `FoodProduct`, `ElectronicProduct`).
- [ ] Xử lý các trường hợp ngoại lệ khi đọc/ghi file (file chưa tồn tại, file rỗng, JSON sai định dạng).
- [ ] Cài đặt chức năng xuất báo cáo ra định dạng CSV.
"""

