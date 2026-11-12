# Hướng dẫn đóng góp & Quy trình làm việc nhóm trên GitHub

Nhánh chính của dự án là `main`. Sau khi bộ khung dự án được khởi tạo, **không push trực tiếp lên nhánh `main`**.

## Phân công nhánh làm việc

| Thành viên | Nhánh (`branch`) | Module phụ trách |
| :--- | :--- | :--- |
| Tiến (Trưởng nhóm) | `feature/main-menu` | `main.py`, `cli/menu.py`, tích hợp & tài liệu |
| Lâm | `feature/product-models` | `models/product.py` |
| Sơn | `feature/product-management` | `services/inventory_manager.py` |
| Chi | `feature/stock-transactions` | `models/stock_transaction.py`, `services/stock_service.py` |
| Minh | `feature/supplier-reports` | `models/supplier.py`, `services/report_service.py` |
| Tú | `feature/storage-testing` | `storage/storage.py`, `tests/` |

## Quy trình làm việc chuẩn (9 bước)

1. **Clone repository** về máy cá nhân:
   ```bash
   git clone <URL-của-repository>
   cd python-inventory-management-system
   ```
2. **Cập nhật nhánh `main` mới nhất** trước khi bắt đầu làm việc:
   ```bash
   git checkout main
   git pull origin main
   ```
3. **Tạo branch riêng** theo bảng phân công:
   ```bash
   git checkout -b <ten-nhanh-cua-ban>
   ```
4. **Phạm vi chỉnh sửa:** Chỉ chỉnh sửa các module thuộc trách nhiệm của mình, trừ trường hợp đã trao đổi và thống nhất với nhóm.
5. **Commit với thông điệp rõ ràng** (tuân theo quy ước bên dưới):
   ```bash
   git add <cac-file-da-sua>
   git commit -m "feat: mo ta ngan gon thay doi"
   ```
6. **Push branch lên GitHub**:
   ```bash
   git push -u origin <ten-nhanh-cua-ban>
   ```
7. **Tạo Pull Request (PR)** vào nhánh `main` trên GitHub và điền đầy đủ thông tin theo mẫu `PULL_REQUEST_TEMPLATE.md`.
8. **Review & Merge:** Trưởng nhóm (Tiến) review mã nguồn, chạy kiểm thử và kiểm tra tích hợp trước khi merge vào `main`.
9. **Không push trực tiếp vào `main`** sau khi bộ khung đã được khởi tạo.

## Quy ước đặt tên Commit

Sử dụng tiền tố rõ ràng theo loại thay đổi:

- `feat: add product models`
- `feat: implement inventory CRUD`
- `feat: implement stock transactions`
- `feat: add supplier reports`
- `test: add inventory unit tests`
- `docs: update README`
- `fix: ...` (khi sửa lỗi)

## Tiêu chuẩn code

- Tuân thủ chuẩn **PEP 8** (`PascalCase` cho tên class, `snake_case` cho tên file, biến và hàm/phương thức).
- Đảm bảo chạy thử `python main.py` và `python -m unittest discover -s tests -v` không lỗi trước khi mở Pull Request.

