# Lưu đồ hoạt động Menu chính & Sơ đồ kiến trúc tổng quan

Tài liệu thiết kế cho phần giao diện Console và tích hợp hệ thống (Phụ trách: Thành viên 1 – Tiến, nhánh `feature/main-menu`).

---

## 1. Lưu đồ hoạt động của Menu chính

```mermaid
flowchart TD
    A(["Bắt đầu chương trình (main.py)"]) --> B["Khởi tạo AppContext & InventoryCLI"]
    B --> C["Hiển thị Menu chính (0 - 7)"]
    C --> D["Nhập lựa chọn từ bàn phím"]

    D -->|"EOF / Ctrl+C"| Z(["Kết thúc chương trình an toàn"])
    D -->|"Không phải số hoặc ngoài 0 - 7"| E["Thông báo lỗi nhập liệu"]
    E --> C

    D -->|"Chọn 1 - 7"| F["Mở Menu con tương ứng (1..7)"]
    F --> G["Hiển thị các mục chức năng của Menu con"]
    G --> H["Nhập lựa chọn trong Menu con"]

    H -->|"EOF / Ctrl+C"| Z
    H -->|"Sai định dạng / ngoài phạm vi"| I["Thông báo lỗi và yêu cầu nhập lại"]
    I --> G

    H -->|"Chọn 0 (Quay lại)"| C
    H -->|"Chọn chức năng hợp lệ"| J{"Service tương ứng đã sẵn sàng?"}

    J -->|"Chưa (service is None)"| K["Hiển thị: [CHƯA TRIỂN KHAI] Chức năng đang được thành viên phụ trách phát triển."]
    K --> G

    J -->|"Đã sẵn sàng"| L["Gọi Service xử lý & hiển thị kết quả"]
    L --> G

    D -->|"Chọn 0 (Thoát)"| M["Hỏi xác nhận thoát (c/k)"]
    M -->|"EOF / Ctrl+C"| Z
    M -->|"Không hợp lệ"| M
    M -->|"Không (k)"| C
    M -->|"Có (c)"| Z
```

---

## 2. Sơ đồ kiến trúc tổng quan các tầng (`main.py → cli/ → services/ → models/` & `storage/`)

> **Lưu ý:** Sơ đồ dưới đây chỉ mô tả **kiến trúc phân tầng tổng quan** giữa các package, **không thay thế UML Class Diagram đầy đủ** (thuộc tính, phương thức, quan hệ kế thừa/kết hợp chi tiết của toàn bộ hệ thống sẽ được tổng hợp riêng trong `docs/uml/`).

```mermaid
flowchart LR
    MAIN["main.py\n(Điểm khởi chạy)"] --> CLI["cli/\n(menu.py, input_helpers.py)\nGiao diện Console & Kiểm tra nhập"]

    CLI -->|"Điều phối CRUD / Tìm / Sắp xếp"| INV["services/inventory_manager.py\n(InventoryManager)"]
    CLI -->|"Điều phối Nhập / Xuất kho"| STK["services/stock_service.py\n(StockService)"]
    CLI -->|"Điều phối Nhà cung cấp & Báo cáo"| RPT["services/report_service.py\n(ReportService)"]
    CLI -->|"Lưu / Đọc JSON & Xuất CSV"| STG["storage/storage.py\n(JSON / CSV Storage)"]

    INV -->|"Quản lý"| PROD["models/product.py\n(Product, FoodProduct, ElectronicProduct)"]
    STK -->|"Cập nhật tồn kho qua"| INV
    STK -->|"Tạo & lưu"| TX["models/stock_transaction.py\n(StockTransaction)"]
    RPT -->|"Đọc dữ liệu sản phẩm từ"| INV
    RPT -->|"Quản lý"| SUP["models/supplier.py\n(Supplier)"]
    STG -->|"Serialize / Deserialize"| PROD
```

