# Tài Liệu Tổng Hợp Thiết Kế UML Hệ Thống Quản Lý Kho Sản Phẩm (v1.0)

- **Dự án:** Product Inventory Management System (`python-inventory-management-system`)
- **Đề tài:** Chủ đề 04 – Quản lý kho sản phẩm bằng Python OOP (Console CLI)
- **Chuẩn phê duyệt:** **Approved Design v1.0 – 40 Decisions Confirmed** (Ngày 17/11/2026)
- **Tài liệu tham chiếu:** [API_CONTRACT.md](../API_CONTRACT.md), [TASK_ASSIGNMENT.md](../TASK_ASSIGNMENT.md)

---

## 1. MỤC LỤC BỘ TÀI LIỆU THIẾT KẾ UML

Toàn bộ hệ thống thiết kế UML của dự án được chuẩn hóa thành 4 sơ đồ độc lập, chuyên sâu theo đúng chuẩn phân tích thiết kế phần mềm hướng đối tượng:

| STT | Tài liệu Sơ đồ | Đường dẫn liên kết | Mô tả nội dung chi tiết |
| :-: | :--- | :--- | :--- |
| 1 | **UML Class Diagram** | [CLASS_DIAGRAM.md](CLASS_DIAGRAM.md) | Sơ đồ lớp tổng thể hệ thống và sơ đồ phân rã từng tầng (Domain Model, Services, CLI/Storage), thể hiện đầy đủ thuộc tính, phương thức, quan hệ kế thừa, tập hợp, kết hợp và hiệp hội. |
| 2 | **UML Use Case Diagram** | [USE_CASE_DIAGRAM.md](USE_CASE_DIAGRAM.md) | Sơ đồ ca sử dụng chuẩn với 1 Actor duy nhất (Thủ kho/Người quản lý), System Boundary, 18 ca sử dụng chính (phân định rõ Lưu thủ công, Đọc JSON, Thoát chương trình), quan hệ `<<include>>`, `<<extend>>` và bảng đặc tả chi tiết từng ca sử dụng. |
| 3 | **UML Activity Diagram** | [ACTIVITY_DIAGRAM.md](ACTIVITY_DIAGRAM.md) | Lưu đồ hoạt động chi tiết cho 4 nghiệp vụ trọng tâm: (1) Thêm sản phẩm, (2) Cập nhật và Xóa sản phẩm, (3) Nhập kho, (4) Xuất kho có xử lý hoàn tác (rollback). |
| 4 | **UML Sequence Diagram** | [SEQUENCE_DIAGRAM.md](SEQUENCE_DIAGRAM.md) | Sơ đồ tuần tự thể hiện các thông điệp truyền giữa các đối tượng trong 5 luồng: (1) Thêm sản phẩm, (2) Nhập kho, (3) Xuất kho với toàn bộ nhánh `alt`, (4) Xóa sản phẩm kiểm tra ràng buộc, (5) Tự động lưu dữ liệu an toàn khi thoát. |

---

## 2. TÓM TẮT KIẾN TRÚC VÀ CÁC THAY ĐỔI CỐT LÕI (V1.0)

Dựa trên 40 quyết định thiết kế chính thức (Q01 – Q40), kiến trúc hệ thống đã được tinh chỉnh đạt độ chuẩn hóa cao:

```text
┌─────────────────────────────────────────────────────────────┐
│                 1. Presentation Layer (cli/)                │
│       main.py ──▶ cli/menu.py + cli/input_helpers.py        │
└──────────────────────────────┬──────────────────────────────┘
                               │ Phụ thuộc qua AppContext
┌──────────────────────────────▼──────────────────────────────┐
│                2. Business Logic Layer (services/)          │
│   ├── inventory_manager.py : Quản lý sản phẩm (Sơn)         │
│   ├── stock_service.py     : Nhập/xuất kho & Giao dịch (Chi)│
│   ├── supplier_service.py  : Quản lý nhà cung cấp (Minh)   │
│   └── report_service.py    : Thống kê & Cảnh báo (Minh)    │
└──────────────────────────────┬──────────────────────────────┘
                               │ Thao tác thực thể
┌──────────────────────────────▼──────────────────────────────┐
│                 3. Domain Model Layer (models/)             │
│   ├── product.py           : Product, Food, Electronic (Lâm)│
│   ├── supplier.py          : Supplier (Minh)                │
│   └── stock_transaction.py : StockTransaction (Chi)         │
└──────────────────────────────▲──────────────────────────────┘
                               │ Serialize / Deserialize
┌──────────────────────────────┴──────────────────────────────┐
│                 4. Persistence Layer (storage/)             │
│   storage.py : Lưu/đọc JSON 3 thực thể, xuất CSV (Tú)       │
└─────────────────────────────────────────────────────────────┘
```

### Các điểm điều chỉnh kiến trúc so với bản sơ thảo ban đầu:
1. **Tách riêng `SupplierService` (Q16):** Đưa toàn bộ chức năng CRUD nhà cung cấp ra khỏi `ReportService` thành một service độc lập (`services/supplier_service.py`), do Minh phụ trách. `ReportService` chỉ thuần túy làm nhiệm vụ truy vấn, thống kê và cảnh báo.
2. **Khẳng định `get_product_by_id()` ném `KeyError` (Q18):** Không trả về `None` khi không tìm thấy sản phẩm.
3. **Quy tắc bảo vệ số lượng tồn kho (Q08, Q19, Q20):** 
   - Đóng gói chặt chẽ `Product.quantity` thành thuộc tính chỉ đọc (`@property quantity`, không có public setter); biến động tồn kho bắt buộc qua `increase_stock()` / `decrease_stock()` do `StockService` kiểm soát.
   - `update_product()` cấm sửa trực tiếp `quantity` (ném `ValueError`).
   - `delete_product(product_id, stock_service)` kiểm tra trực tiếp ở tầng service: chỉ cho phép xóa khi `quantity == 0` VÀ `stock_service.has_product_transactions(product_id)` là `False`, không dựa dẫm vào cờ boolean từ phía gọi CLI.
   - Tương tự, `delete_supplier(supplier_id, inventory_manager)` kiểm tra ràng buộc toàn vẹn trực tiếp tại service để cấm xóa khi còn sản phẩm liên kết.
4. **Nghiệp vụ kho nguyên tử (Q23, Q25, Q27):** 
   - `transaction_id` sinh bằng UUID.
   - Số lượng nhập/xuất bắt buộc là số nguyên dương (từ chối `bool`).
   - Nếu quá trình ghi nhận giao dịch gặp sự cố, hệ thống tự động rollback số lượng tồn kho về ban đầu.
5. **Lưu trữ JSON toàn diện và an toàn (Q05, Q33, Q34):** 
   - JSON lưu đủ 3 thực thể: `products`, `suppliers`, `transactions`.
   - Cơ chế ghi file an toàn nguyên tử (ghi ra file tạm rồi tráo đổi `os.replace`).
   - Tự động sao lưu dữ liệu khi người dùng chọn thoát ứng dụng.

---

## 3. HƯỚNG DẪN XUẤT ẢNH VECTOR ĐỘ PHÂN GIẢI CAO (SVG / PNG)

Để phục vụ đóng cuốn Báo cáo bài tập lớn (Word/PDF) và thiết kế Slide thuyết trình bảo vệ đồ án:

1. **Xem trực tiếp trên GitHub / Markdown Preview:**
   - Các file `CLASS_DIAGRAM.md`, `USE_CASE_DIAGRAM.md`, `ACTIVITY_DIAGRAM.md`, `SEQUENCE_DIAGRAM.md` đều sử dụng cú pháp Mermaid chuẩn, được GitHub và VS Code render tự động sắc nét trên mọi thiết bị.
2. **Xuất file ảnh chất lượng cao:**
   - **Cách 1 (Mermaid Live Editor):** Truy cập [mermaid.live](https://mermaid.live/), dán đoạn mã Mermaid trong từng file và chọn **Download SVG** (cho bản in báo cáo) hoặc **Download PNG (4K)** (cho slide trình chiếu).
   - **Cách 2 (PlantUML):** Đối với Sơ đồ Ca sử dụng, sử dụng đoạn mã PlantUML có sẵn trong [USE_CASE_DIAGRAM.md](USE_CASE_DIAGRAM.md) tại [PlantText](https://www.planttext.com/) để tải về bản vẽ vector chuẩn UML 2.5.
   - Lưu trữ các ảnh đã xuất vào thư mục [docs/uml/](../uml/) hoặc [docs/reports/](../reports/).

---

## 4. KẾ HOẠCH ĐỒNG BỘ VỚI MÃ NGUỒN (CODE SYNC)

- **Trước 20/11/2026:** 5 thành viên (Lâm, Sơn, Chi, Minh, Tú) triển khai mã nguồn trên các nhánh `feature/*` tuân thủ 100% hợp đồng API Contract v1.0 và sơ đồ lớp trong [CLASS_DIAGRAM.md](CLASS_DIAGRAM.md).
- **Từ 21/11/2026 – 23/11/2026:** Tiến tích hợp toàn bộ các service vào `cli/menu.py` và `AppContext`.
- **Ngày 24/11/2026:** Rà soát lại toàn bộ sơ đồ UML đối chiếu với mã nguồn hoàn thiện, chụp ảnh màn hình CLI thực tế vào [docs/screenshots/](../screenshots/), hoàn tất báo cáo bài tập lớn sẵn sàng nghiệm thu trước **25/11/2026**.
