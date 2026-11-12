# Product Inventory Management System (`python-inventory-management-system`)

## Giới thiệu đề tài

- **Đề tài:** Chủ đề 04 – Quản lý kho sản phẩm bằng Python OOP.
- **Hình thức:** Bài tập lớn nhóm 6 sinh viên, xây dựng ứng dụng quản lý kho sản phẩm chạy trên Console (CLI).
- **Trạng thái dự án:** **Đang khởi tạo** (mới hoàn thành bộ khung thư mục, tài liệu hướng dẫn và menu khởi động tối thiểu; các chức năng nghiệp vụ đang được đánh dấu `TODO`).

## Mục tiêu dự án

- Áp dụng lập trình hướng đối tượng (OOP) trong Python: kế thừa, đa hình, đóng gói dữ liệu và kiểm tra dữ liệu đầu vào.
- Tổ chức mã nguồn theo kiến trúc module rõ ràng (`models/`, `services/`, `storage/`, `cli/`, `tests/`) để 6 thành viên phát triển độc lập, dễ tích hợp và bảo trì.
- Hỗ trợ lưu trữ dữ liệu dạng JSON, xuất báo cáo CSV và kiểm thử đơn vị bằng `unittest`.
- Thực hành quy trình làm việc nhóm chuyên nghiệp với Git và GitHub (nhánh `feature/*`, Pull Request, code review).

## Công nghệ sử dụng

- **Ngôn ngữ:** Python 3.11+ (ưu tiên thư viện chuẩn, không sử dụng framework web hay SQL).
- **Phương pháp:** Lập trình hướng đối tượng (OOP).
- **Giao diện:** Console CLI.
- **Lưu trữ dữ liệu (dự kiến):** JSON (`json`).
- **Xuất báo cáo (dự kiến):** CSV (`csv`).
- **Kiểm thử:** `unittest` (thư viện chuẩn Python).
- **Quản lý phiên bản:** Git & GitHub.

## Danh sách thành viên và bảng phân công công việc

| STT | Thành viên | Vai trò | Nhánh Git (`branch`) | Module / Phạm vi phụ trách |
| :-: | :--- | :--- | :--- | :--- |
| 1 | **Tiến** | Trưởng nhóm, tích hợp & Console | `feature/main-menu` | `main.py`, `cli/menu.py`, quản lý cấu trúc, tích hợp module, tổng hợp `docs/` |
| 2 | **Lâm** | Lập trình hướng đối tượng | `feature/product-models` | `models/product.py` (`Product`, `FoodProduct`, `ElectronicProduct`) |
| 3 | **Sơn** | Quản lý sản phẩm | `feature/product-management` | `services/inventory_manager.py` (`InventoryManager`) |
| 4 | **Chi** | Nghiệp vụ kho | `feature/stock-transactions` | `models/stock_transaction.py`, `services/stock_service.py` (`StockTransaction`, `StockService`) |
| 5 | **Minh** | Nhà cung cấp & thống kê | `feature/supplier-reports` | `models/supplier.py`, `services/report_service.py` (`Supplier`, `ReportService`) |
| 6 | **Tú** | Lưu dữ liệu & kiểm thử | `feature/storage-testing` | `storage/storage.py`, `tests/` (JSON/CSV và bộ unit test) |

## Cấu trúc thư mục

```text
python-inventory-management-system/
│
├── main.py
├── README.md
├── .gitignore
├── requirements.txt
│
├── models/
│   ├── __init__.py
│   ├── product.py
│   ├── supplier.py
│   └── stock_transaction.py
│
├── services/
│   ├── __init__.py
│   ├── inventory_manager.py
│   ├── stock_service.py
│   └── report_service.py
│
├── storage/
│   ├── __init__.py
│   └── storage.py
│
├── cli/
│   ├── __init__.py
│   └── menu.py
│
├── tests/
│   ├── __init__.py
│   ├── test_product.py
│   ├── test_inventory.py
│   ├── test_stock.py
│   └── test_reports.py
│
├── data/
│   └── .gitkeep
│
├── docs/
│   ├── README.md
│   ├── uml/
│   │   └── .gitkeep
│   ├── flowcharts/
│   │   └── .gitkeep
│   ├── screenshots/
│   │   └── .gitkeep
│   └── reports/
│       └── .gitkeep
│
└── .github/
    ├── PULL_REQUEST_TEMPLATE.md
    └── CONTRIBUTING.md
```

## Hướng dẫn clone repository

```bash
git clone <URL-của-repository>
cd python-inventory-management-system
```

## Hướng dẫn chạy chương trình

Đảm bảo máy đã cài đặt Python 3.11 trở lên, sau đó chạy từ thư mục gốc của dự án:

```bash
python main.py
```

*(Trên một số hệ điều hành Linux/macOS, sử dụng `python3 main.py` nếu lệnh `python` chưa được liên kết.)*

## Hướng dẫn chạy kiểm thử

```bash
python -m unittest discover -s tests -v
```

*(Hoặc `python3 -m unittest discover -s tests -v`.)*

## Quy tắc làm việc với GitHub

- Nhánh chính: `main` (không push trực tiếp sau khi đã khởi tạo bộ khung).
- Mỗi thành viên làm việc trên nhánh riêng theo bảng phân công ở trên.
- Xem chi tiết quy trình tạo nhánh, quy ước commit và tạo Pull Request tại [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md).

## Danh sách chức năng dự kiến phát triển

- [ ] Mô hình hóa sản phẩm (`Product`, `FoodProduct`, `ElectronicProduct`) với đóng gói, kế thừa, đa hình và validate dữ liệu.
- [ ] Quản lý nhà cung cấp (`Supplier`).
- [ ] Quản lý danh mục sản phẩm CRUD, tìm kiếm (theo mã, tên, nhà cung cấp) và sắp xếp (theo giá, số lượng tăng/giảm dần).
- [ ] Nghiệp vụ nhập/xuất kho và lưu lịch sử giao dịch (`StockTransaction`, `StockService`).
- [ ] Thống kê tổng giá trị tồn kho, hàng sắp hết, thực phẩm gần hết hạn và bảo hành thiết bị điện tử (`ReportService`).
- [ ] Lưu/đọc dữ liệu sản phẩm bằng JSON (khôi phục đúng kiểu đối tượng) và xuất báo cáo CSV.
- [ ] Giao diện Console menu đầy đủ điều hướng các chức năng.
- [ ] Bộ kiểm thử `unittest` (tối thiểu 10 test case cho ràng buộc nghiệp vụ và lỗi dữ liệu).

