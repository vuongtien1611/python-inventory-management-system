# Thiết Kế UML Sơ Đồ Lớp (Class Diagram) – v1.0

- **Hệ thống:** Product Inventory Management System
- **Chuẩn thiết kế:** Approved Design v1.0 (Khớp 40 quyết định thiết kế chính thức)
- **Tài liệu đối chiếu:** [API_CONTRACT.md](../API_CONTRACT.md), [TASK_ASSIGNMENT.md](../TASK_ASSIGNMENT.md)

---

## 1. SƠ ĐỒ LỚP TỔNG THỂ HỆ THỐNG (SYSTEM OVERVIEW CLASS DIAGRAM)

```mermaid
classDiagram
    %% Tầng Thực Thể (Domain Models)
    class Product {
        -_product_id: str
        -_name: str
        -_price: float
        -_quantity: int
        -_supplier_id: str
        +__init__(product_id: str, name: str, price: float, quantity: int, supplier_id: str)
        +product_id: str
        +name: str
        +price: float
        +quantity: int
        +supplier_id: str
        +increase_stock(amount: int) void
        +decrease_stock(amount: int) void
        +is_valid() bool
        +get_inventory_value() float
        +to_dict() dict
        +__str__() str
    }

    class FoodProduct {
        -_expiry_date: date
        +__init__(product_id: str, name: str, price: float, quantity: int, supplier_id: str, expiry_date: date)
        +expiry_date: date
        +is_valid() bool
        +is_expired(current_date: date) bool
        +days_until_expiry(current_date: date) int
        +to_dict() dict
        +__str__() str
    }

    class ElectronicProduct {
        -_warranty_months: int
        +__init__(product_id: str, name: str, price: float, quantity: int, supplier_id: str, warranty_months: int)
        +warranty_months: int
        +is_valid() bool
        +to_dict() dict
        +__str__() str
    }

    class Supplier {
        -_supplier_id: str
        -_name: str
        -_phone: str
        -_address: str
        -_email: str
        +__init__(supplier_id: str, name: str, phone: str, address: str, email: str)
        +supplier_id: str
        +name: str
        +phone: str
        +address: str
        +email: str
        +is_valid() bool
        +to_dict() dict
        +__str__() str
    }

    class StockTransaction {
        -_transaction_id: str
        -_product_id: str
        -_transaction_type: str
        -_quantity: int
        -_timestamp: str
        -_note: str
        +__init__(transaction_id: str, product_id: str, transaction_type: str, quantity: int, timestamp: str, note: str)
        +transaction_id: str
        +product_id: str
        +transaction_type: str
        +quantity: int
        +timestamp: str
        +note: str
        +to_dict() dict
        +__str__() str
    }

    %% Tầng Dịch Vụ Nghiệp Vụ (Services)
    class InventoryManager {
        -_products: dict~str, Product~
        +__init__()
        +add_product(product: Product, supplier_service: SupplierService) void
        +update_product(product_id: str, **fields) void
        +delete_product(product_id: str, stock_service: StockService) void
        +get_product_by_id(product_id: str) Product
        +get_all_products() list~Product~
        +search_product(keyword: str, by: str) list~Product~
        +sort_products(by: str, reverse: bool) list~Product~
    }

    class SupplierService {
        -_suppliers: dict~str, Supplier~
        +__init__()
        +add_supplier(supplier: Supplier) void
        +update_supplier(supplier_id: str, **fields) void
        +delete_supplier(supplier_id: str, inventory_manager: InventoryManager) void
        +get_supplier_by_id(supplier_id: str) Supplier
        +get_all_suppliers() list~Supplier~
        +has_supplier(supplier_id: str) bool
    }

    class StockService {
        -_inventory_manager: InventoryManager
        -_transactions: list~StockTransaction~
        +__init__(inventory_manager: InventoryManager)
        +import_stock(product_id: str, quantity: int, note: str) StockTransaction
        +export_stock(product_id: str, quantity: int, note: str) StockTransaction
        +get_transaction_history(product_id: str) list~StockTransaction~
        +has_product_transactions(product_id: str) bool
    }

    class ReportService {
        -_inventory_manager: InventoryManager
        +__init__(inventory_manager: InventoryManager)
        +get_total_inventory_value() dict
        +get_low_stock_products(threshold: int) list~Product~
        +get_expiring_food_products(days: int) list~FoodProduct~
        +check_food_expiry_status(product_id: str) list~dict~
        +get_warranty_summary(product_id: str) list~dict~
    }

    %% Tầng Giao Diện & Lưu Trữ (CLI & Storage)
    class Storage {
        <<utility / module>>
        +save_to_json(data: dict, file_path: str) bool
        +load_from_json(file_path: str) dict
        +export_to_csv(products: list~Product~, file_path: str) void
    }

    class AppContext {
        +inventory_manager: InventoryManager
        +stock_service: StockService
        +supplier_service: SupplierService
        +report_service: ReportService
        +storage: Storage
    }

    class InventoryCLI {
        +context: AppContext
        +__init__(context: AppContext)
        +display_main_menu() void
        +run() void
        +open_product_menu() void
        +open_supplier_menu() void
        +open_stock_menu() void
        +open_search_sort_menu() void
        +open_report_menu() void
        +open_inspection_menu() void
        +open_data_menu() void
    }

    %% Các mối quan hệ (Relationships)
    Product <|-- FoodProduct : Kế thừa (Inheritance)
    Product <|-- ElectronicProduct : Kế thừa (Inheritance)
    Product "*" --> "1" Supplier : Tham chiếu (supplier_id)

    InventoryManager "1" o-- "*" Product : Quản lý danh mục (Aggregation)
    SupplierService "1" o-- "*" Supplier : Quản lý nhà cung cấp (Aggregation)

    StockService "1" --> "1" InventoryManager : Tác động tồn kho (Uses)
    StockService "1" o-- "*" StockTransaction : Lưu lịch sử giao dịch (Aggregation)
    StockTransaction "*" --> "1" Product : Ghi nhận cho (product_id)

    ReportService "1" --> "1" InventoryManager : Đọc dữ liệu (Reads)

    AppContext "1" o-- "1" InventoryManager : Chứa tham chiếu
    AppContext "1" o-- "1" StockService : Chứa tham chiếu
    AppContext "1" o-- "1" SupplierService : Chứa tham chiếu
    AppContext "1" o-- "1" ReportService : Chứa tham chiếu
    AppContext "1" o-- "1" Storage : Chứa tham chiếu

    InventoryCLI "1" --> "1" AppContext : Điều phối dịch vụ (Uses)
    Storage ..> Product : Serialize/Deserialize
    Storage ..> Supplier : Serialize/Deserialize
    Storage ..> StockTransaction : Serialize/Deserialize
```

---

## 2. SƠ ĐỒ LỚP CHI TIẾT TỪNG PHÂN HỆ

Nhằm hỗ trợ chèn vào tài liệu báo cáo Word và slide thuyết trình không bị co nhỏ kích thước, dưới đây là các sơ đồ lớp tách theo tầng nghiệp vụ:

### 2.1. Phân hệ Mô hình Thực thể (Domain Model Layer)
Minh họa tính kế thừa (`Product`, `FoodProduct`, `ElectronicProduct`), liên kết nhà cung cấp và lịch sử giao dịch:

```mermaid
classDiagram
    class Product {
        -_product_id: str
        -_name: str
        -_price: float
        -_quantity: int
        -_supplier_id: str
        +increase_stock(amount: int) void
        +decrease_stock(amount: int) void
        +is_valid() bool
        +get_inventory_value() float
        +to_dict() dict
        +__str__() str
    }

    class FoodProduct {
        -_expiry_date: date
        +is_valid() bool
        +is_expired(current_date: date) bool
        +days_until_expiry(current_date: date) int
        +to_dict() dict
        +__str__() str
    }

    class ElectronicProduct {
        -_warranty_months: int
        +is_valid() bool
        +to_dict() dict
        +__str__() str
    }

    class Supplier {
        -_supplier_id: str
        -_name: str
        -_phone: str
        -_address: str
        -_email: str
        +is_valid() bool
        +to_dict() dict
        +__str__() str
    }

    class StockTransaction {
        -_transaction_id: str
        -_product_id: str
        -_transaction_type: str
        -_quantity: int
        -_timestamp: str
        -_note: str
        +to_dict() dict
        +__str__() str
    }

    Product <|-- FoodProduct : Kế thừa (Inheritance)
    Product <|-- ElectronicProduct : Kế thừa (Inheritance)
    Product "*" --> "1" Supplier : Thuộc về (supplier_id)
    StockTransaction "*" --> "1" Product : Tác động (product_id)
```

### 2.2. Phân hệ Dịch vụ Nghiệp vụ (Business Logic Services)
Minh họa sự phân tách rõ ràng giữa Quản lý sản phẩm, Nghiệp vụ kho, Quản lý nhà cung cấp và Báo cáo thống kê:

```mermaid
classDiagram
    class InventoryManager {
        -_products: dict~str, Product~
        +add_product(product, supplier_service) void
        +update_product(product_id, **fields) void
        +delete_product(product_id, stock_service) void
        +get_product_by_id(product_id) Product
        +get_all_products() list~Product~
        +search_product(keyword, by) list~Product~
        +sort_products(by, reverse) list~Product~
    }

    class StockService {
        -_inventory_manager: InventoryManager
        -_transactions: list~StockTransaction~
        +import_stock(product_id, quantity, note) StockTransaction
        +export_stock(product_id, quantity, note) StockTransaction
        +get_transaction_history(product_id) list~StockTransaction~
        +has_product_transactions(product_id) bool
    }

    class SupplierService {
        -_suppliers: dict~str, Supplier~
        +add_supplier(supplier) void
        +update_supplier(supplier_id, **fields) void
        +delete_supplier(supplier_id, inventory_manager) void
        +get_supplier_by_id(supplier_id) Supplier
        +get_all_suppliers() list~Supplier~
        +has_supplier(supplier_id) bool
    }

    class ReportService {
        -_inventory_manager: InventoryManager
        +get_total_inventory_value() dict
        +get_low_stock_products(threshold) list~Product~
        +get_expiring_food_products(days) list~FoodProduct~
        +check_food_expiry_status(product_id) list~dict~
        +get_warranty_summary(product_id) list~dict~
    }

    StockService "1" --> "1" InventoryManager : Tác động tồn kho
    ReportService "1" --> "1" InventoryManager : Đọc dữ liệu
    InventoryManager ..> SupplierService : Xác thực mã NCC
    InventoryManager ..> StockService : Kiểm tra giao dịch khi xóa
    SupplierService ..> InventoryManager : Kiểm tra liên kết khi xóa
```

---

## 3. BẢNG MÔ TẢ ĐẶC TẢ CÁC QUAN HỆ TRONG SƠ ĐỒ LỚP

| Quan hệ | Các lớp liên quan | Loại quan hệ | Diễn giải ngữ nghĩa OOP & Nghiệp vụ |
| :--- | :--- | :--- | :--- |
| **Kế thừa (Inheritance)** | `Product` & `FoodProduct`<br>`Product` & `ElectronicProduct` | Generalization (`<|--`) | `FoodProduct` và `ElectronicProduct` là các biến thể chuyên biệt của `Product`, kế thừa toàn bộ thuộc tính cơ sở và ghi đè đa hình các phương thức `is_valid()`, `__str__()`, `to_dict()`. |
| **Tập hợp (Aggregation)** | `InventoryManager` & `Product` | Aggregation (`o--`) | `InventoryManager` sở hữu tập hợp các sản phẩm trong kho (`_products`). Vòng đời của `Product` không hoàn toàn gắn cứng với một phiên `InventoryManager` vì đối tượng có thể được nạp/lưu độc lập qua JSON. |
| **Tập hợp (Aggregation)** | `SupplierService` & `Supplier` | Aggregation (`o--`) | `SupplierService` quản lý tập hợp các đối tượng `Supplier` trong từ điển `_suppliers`. |
| **Tập hợp (Aggregation)** | `StockService` & `StockTransaction` | Aggregation (`o--`) | `StockService` lưu giữ danh sách các đối tượng giao dịch `StockTransaction`. Các bản ghi giao dịch là bất biến (read-only). |
| **Hiệp hội (Association)** | `Product` & `Supplier` | Association (`-->`) | Mỗi `Product` liên kết với đúng 1 `Supplier` thông qua thuộc tính `_supplier_id` (bội số `*` đến `1`). |
| **Hiệp hội (Association)** | `StockService` & `InventoryManager` | Association (`-->`) | `StockService` nhận `InventoryManager` qua constructor (Dependency Injection) để cập nhật tồn kho khi có giao dịch nhập/xuất. |
| **Hiệp hội (Association)** | `ReportService` & `InventoryManager` | Association (`-->`) | `ReportService` nhận `InventoryManager` qua constructor để truy vấn danh sách sản phẩm phục vụ thống kê, không có quyền thay đổi dữ liệu sản phẩm. |
| **Phụ thuộc (Dependency)** | `Storage` & `Product`, `Supplier`, `StockTransaction` | Dependency (`..>`) | `Storage` chịu trách nhiệm serialize các thực thể thành JSON/CSV và deserialize từ JSON thành các thực thể cụ thể. |
| **Phụ thuộc (Dependency)** | `InventoryManager` & `SupplierService` | Dependency (`..>`) | `InventoryManager.add_product` nhận `SupplierService` để kiểm tra sự tồn tại hợp lệ của `supplier_id`. |
| **Phụ thuộc (Dependency)** | `InventoryManager` & `StockService` | Dependency (`..>`) | `InventoryManager.delete_product` nhận `StockService` để kiểm tra sản phẩm chưa từng có lịch sử giao dịch kho trước khi xóa. |
| **Phụ thuộc (Dependency)** | `SupplierService` & `InventoryManager` | Dependency (`..>`) | `SupplierService.delete_supplier` nhận `InventoryManager` để bảo đảm không có sản phẩm nào trong kho đang liên kết với nhà cung cấp cần xóa. |
| **Tập hợp (Aggregation)** | `AppContext` & các `Services` | Aggregation (`o--`) | `AppContext` đóng vai trò Service Container nắm giữ các instance dùng chung của toàn bộ hệ thống. |

---

## 4. QUY TẮC BẢO VỆ TỒN KHO VÀ ĐÓNG GÓI THUỘC TÍNH `QUANTITY`

Nhằm bảo đảm tính toàn vẹn dữ liệu kế toán kho và tuân thủ các quyết định thiết kế (Q08, Q19, Q20, Q23, Q24, Q27), hệ thống áp dụng các quy tắc sau:

1. **`Product.quantity` là thuộc tính chỉ đọc (Read-Only Property):**
   - Biến thể hiện `_quantity` được đóng gói trong lớp `Product` và chỉ công khai qua `@property quantity` (getter).
   - Tuyệt đối không cung cấp setter công khai (`@quantity.setter`) cho thuộc tính này.
2. **`InventoryManager.update_product()` cấm thay đổi số lượng:**
   - Trong quá trình cập nhật sản phẩm (CRUD), `update_product(product_id, **fields)` kiểm tra nếu `fields` có chứa khóa `"quantity"`, hệ thống lập tức ném ngoại lệ `ValueError`. Số lượng tồn kho không được phép chỉnh sửa tùy tiện như các thông tin mô tả.
3. **Chỉ `StockService` điều phối thay đổi tồn kho:**
   - Mọi biến động tăng hoặc giảm tồn kho trong toàn bộ hệ thống bắt buộc phải được điều phối thông qua `StockService.import_stock()` (nhập kho) hoặc `StockService.export_stock()` (xuất kho).
4. **Kiểm tra hợp lệ trong `increase_stock()` và `decrease_stock()`:**
   - Cả hai phương thức `Product.increase_stock(amount: int)` và `Product.decrease_stock(amount: int)` đều thực hiện xác thực đầu vào nghiêm ngặt:
     - `amount` bắt buộc phải là số nguyên dương (`isinstance(amount, int) and not isinstance(amount, bool) and amount > 0`), từ chối giá trị kiểu boolean hoặc số âm/bằng 0.
     - `decrease_stock(amount)` kiểm tra `amount <= self._quantity` nhằm bảo đảm không bao giờ để tồn kho bị âm.
5. **Bản chất đóng gói trong ngôn ngữ Python (Encapsulation Convention vs. Absolute Authorization):**
   - Các phương thức thay đổi `quantity` (`increase_stock`, `decrease_stock`) và việc bảo vệ thuộc tính `_quantity` là cơ chế đóng gói ở mức thiết kế hướng đối tượng và hợp đồng giao diện API (API Contract & Invariant Enforcement).
   - Trong Python, theo triết lý *"we are all consenting adults here"*, ngôn ngữ không hỗ trợ các từ khóa truy cập nghiêm ngặt tuyệt đối như `private` ở mức phần cứng/hệ điều hành. Do đó, các phương thức này **không được xem là cơ chế phân quyền bảo mật tuyệt đối (absolute authorization / access control)**. Tính toàn vẹn của hệ thống dựa vào việc tuân thủ triệt để luồng điều phối của tầng Service và hợp đồng API Contract đã cam kết.

