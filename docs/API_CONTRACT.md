# Hợp đồng API Hệ Thống Quản Lý Kho Sản Phẩm (`API_CONTRACT.md`)

> **Trạng thái tài liệu:** **Approved Design v1.0 – 40 Decisions Confirmed**
> **Ngày phê duyệt chính thức:** 17/11/2026
> **Phiên bản:** 1.0 (Đã chốt 40 quyết định thiết kế kiến trúc và nghiệp vụ)
> **Áp dụng cho:** Toàn bộ 6 thành viên nhóm (Tiến, Lâm, Sơn, Chi, Minh, Tú).

---

## I. TỔNG HỢP 40 QUYẾT ĐỊNH THIẾT KẾ CHÍNH THỨC ĐÃ PHÊ DUYỆT

### Nhóm A – Phạm vi ứng dụng
- **Q01:** Hệ thống có một loại người dùng chung là Thủ kho / Người quản lý.
- **Q02:** Không đăng nhập, không mật khẩu, không phân quyền phức tạp.
- **Q03:** Chỉ quản lý một kho hàng duy nhất.
- **Q04:** Hỗ trợ 3 loại sản phẩm: `Product` thông thường, `FoodProduct` (thực phẩm) và `ElectronicProduct` (thiết bị điện tử).
- **Q05:** Tự động lưu dữ liệu an toàn khi thoát bình thường và hỗ trợ lưu thủ công từ menu.

### Nhóm B – Product và OOP
- **Q06:** Mã sản phẩm (`product_id`) do người dùng nhập từ bàn phím, chuẩn hóa `.strip()`, không được trùng.
- **Q07:** Đơn giá (`price`) được phép bằng 0 (hàng tặng/khuyến mãi), không chấp nhận giá âm (`price >= 0`).
- **Q08:** Sau khi tạo sản phẩm, số lượng tồn kho (`quantity`) chỉ được phép thay đổi thông qua nghiệp vụ nhập/xuất kho của `StockService`, không được sửa trực tiếp qua CRUD (`update_product()` cấm sửa `quantity`). Khi tạo mới, `quantity` khởi tạo bằng `0` (hoặc số lượng khởi tạo ban đầu theo quy định nhập kho).
- **Q09:** Ngày hết hạn của `FoodProduct` được xử lý nội bộ bằng `datetime.date` trong Python và lưu trữ chuỗi ISO `YYYY-MM-DD` trong file JSON.
- **Q10:** Nghiệp vụ nhập kho không cho phép nhập thêm thực phẩm đã hết hạn (`expiry_date < date.today()`). Hệ thống phải hiển thị cảnh báo lỗi rõ ràng.
- **Q11:** `ElectronicProduct` lưu `warranty_months: int` là số tháng bảo hành danh nghĩa của nhà sản xuất; hệ thống không tự tính ngày hết hạn bảo hành cố định từ ngày hiện tại.
- **Q12:** Giữ cấu trúc `Product`, `FoodProduct`, `ElectronicProduct` tối giản, chuẩn OOP, không thêm thuộc tính thừa.

### Nhóm C – Supplier
- **Q13:** Mỗi `Product` liên kết với đúng một `Supplier` thông qua `supplier_id`.
- **Q14:** Không cho phép thêm sản phẩm nếu `supplier_id` chưa tồn tại trong hệ thống.
- **Q15:** Không cho phép xóa `Supplier` khi vẫn còn ít nhất một `Product` trong kho tham chiếu đến `supplier_id` đó.
- **Q16:** Tách riêng toàn bộ CRUD nhà cung cấp thành `SupplierService` (`services/supplier_service.py`) do Minh phụ trách; `ReportService` chỉ thực hiện truy vấn và thống kê.

### Nhóm D – InventoryManager
- **Q17:** Quản lý danh mục sản phẩm nội bộ bằng cấu trúc `dict[str, Product]`, khóa chính là `product_id`.
- **Q18:** Phương thức `get_product_by_id(product_id)` ném ngoại lệ `KeyError` khi không tìm thấy mã sản phẩm (không trả về `None`).
- **Q19:** Không cho phép xóa sản phẩm nếu số lượng tồn kho vẫn lớn hơn 0 (`quantity > 0`).
- **Q20:** Không cho phép xóa sản phẩm nếu đã có lịch sử nhập/xuất kho (`StockTransaction`), kể cả khi tồn kho hiện tại bằng 0.
- **Q21:** Tìm kiếm theo tên sản phẩm không phân biệt chữ hoa/thường (`lower()`), nhưng bảo toàn nguyên vẹn dấu tiếng Việt.
- **Q22:** Hỗ trợ sắp xếp theo đơn giá (`price`) và số lượng (`quantity`), với hai chiều: tăng dần (`reverse=False`) và giảm dần (`reverse=True`).

### Nhóm E – StockService
- **Q23:** Số lượng nhập/xuất kho phải là số nguyên dương (`isinstance(quantity, int) and not isinstance(quantity, bool) and quantity > 0`).
- **Q24:** Cho phép xuất hết toàn bộ số lượng tồn kho về 0 (`quantity == product.quantity`).
- **Q25:** Mã giao dịch kho (`transaction_id`) được sinh tự động bằng `uuid.uuid4()`.
- **Q26:** Mỗi giao dịch kho bắt buộc lưu: loại giao dịch (`"IMPORT"` / `"EXPORT"`), thời điểm (`timestamp` định dạng ISO có múi giờ), số lượng (`quantity`), mã sản phẩm (`product_id`) và ghi chú (`note`).
- **Q27:** Tính nguyên tử (Atomic Consistency): Nếu quá trình ghi nhận giao dịch thất bại, phải hoàn tác (rollback) thay đổi tồn kho về trạng thái trước đó.
- **Q28:** Không cho phép chỉnh sửa hoặc xóa giao dịch đã ghi; lịch sử giao dịch chỉ hỗ trợ đọc (`read-only`).

### Nhóm F – Thống kê và Storage
- **Q29:** Ngưỡng cảnh báo sắp hết hàng mặc định là `threshold = 5` (cho phép tùy chỉnh tham số khi gọi hàm).
- **Q30:** Số ngày cảnh báo thực phẩm gần hết hạn mặc định là `days = 7` (cho phép tùy chỉnh tham số khi gọi hàm).
- **Q31:** Phân biệt rõ rệt giữa thực phẩm đã hết hạn (`is_expired() == True`) và thực phẩm cận hạn (`0 <= days_until_expiry <= days`).
- **Q32:** Tổng giá trị tồn kho tính toàn bộ sản phẩm trong kho; trường hợp có thực phẩm đã hết hạn, hệ thống đưa ra cảnh báo giá trị tồn rủi ro riêng.
- **Q33:** File JSON lưu trữ toàn bộ trạng thái hệ thống gồm 3 thực thể: `products`, `suppliers`, và `transactions`.
- **Q34:** Ghi file an toàn theo cơ chế nguyên tử (ghi ra file tạm trước rồi đổi tên thay thế file đích). Khi đọc JSON, nếu file hỏng hoặc dữ liệu không hợp lệ, tuyệt đối không ghi đè lên bộ nhớ hiện tại.
- **Q35:** Xuất file CSV báo cáo tồn kho gồm đầy đủ các cột: `product_id`, `name`, `product_type`, `price`, `quantity`, `inventory_value`, `supplier`.

### Nhóm G – CLI
- **Q36:** Khi người dùng nhập sai dữ liệu, hiển thị thông báo lỗi bằng tiếng Việt và cho phép nhập lại hoặc hủy để quay về menu.
- **Q37:** Khi thực hiện xóa sản phẩm hoặc xóa nhà cung cấp, CLI bắt buộc hỏi xác nhận Có/Không (`c/k`).
- **Q38:** CLI bắt mọi ngoại lệ nghiệp vụ (`ValueError`, `KeyError`), hiển thị thông báo lỗi tiếng Việt thân thiện, không in traceback lỗi cho người dùng.

### Nhóm H – UML
- **Q39:** Bộ tài liệu thiết kế UML bao gồm đầy đủ 4 loại sơ đồ: Use Case Diagram, Class Diagram, Activity Diagram, và Sequence Diagram.
- **Q40:** Bộ thiết kế UML chuẩn hóa trước theo API Contract v1.0; sau khi hoàn thiện code, nhóm sẽ rà soát để đảm bảo mã nguồn và thiết kế khớp 100%.

---

## II. KIẾN TRÚC PHÂN TẦNG VÀ PHỤ THUỘC MODULE

Hệ thống được tổ chức thành 4 tầng rõ rệt:

```text
┌─────────────────────────────────────────────────────────────┐
│                 1. Presentation Layer (cli/)                │
│    main.py ──▶ cli/menu.py + cli/input_helpers.py           │
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

**Nguyên tắc phụ thuộc:**
- `models/` hoàn toàn độc lập, không import từ `services/`, `storage/` hay `cli/`.
- `services/` chỉ import `models/` và phối hợp với nhau qua Dependency Injection (ví dụ: `StockService` nhận `InventoryManager`).
- `storage/` import `models/` để khởi tạo thực thể khi đọc JSON.
- `cli/` chỉ tương tác với các service và storage thông qua `AppContext`, không chứa logic nghiệp vụ kho.

---

## III. CHI TIẾT GIAO DIỆN CÁC TẦNG MODEL & SERVICE

### 1. Tầng Thực Thể (`models/`)

#### 1.1. `models/product.py` (Lâm phụ trách)

##### Lớp `Product` (Lớp cơ sở)
- **Thuộc tính:**
  - `_product_id: str` (không rỗng, đã `.strip()`)
  - `_name: str` (không rỗng, đã `.strip()`)
  - `_price: float` (`price >= 0`, cho phép bằng 0 theo Q07)
  - `_quantity: int` (`quantity >= 0`, chỉ cập nhật qua `StockService` theo Q08)
  - `_supplier_id: str` (mã nhà cung cấp, liên kết 1-1 theo Q13)
- **Phương thức:**
  - `__init__(self, product_id: str, name: str, price: float, quantity: int = 0, supplier_id: str = "") -> None`
  - `@property` getter/setter cho `product_id`, `name`, `price`, `supplier_id` (setter kiểm tra validation nghiêm ngặt).
  - `@property` getter chỉ đọc cho `quantity` (tuyệt đối không có public setter để bảo vệ tính đóng gói; CRUD không được sửa đổi số lượng tồn kho theo Q08).
  - `increase_stock(self, amount: int) -> None`: Tăng tồn kho thêm `amount`. Bắt buộc kiểm tra `isinstance(amount, int) and not isinstance(amount, bool) and amount > 0` (ném `ValueError` nếu sai kiểu hoặc `<= 0`). Dành riêng cho `StockService` khi nhập kho hoặc rollback.
  - `decrease_stock(self, amount: int) -> None`: Giảm tồn kho đi `amount`. Bắt buộc kiểm tra `isinstance(amount, int) and not isinstance(amount, bool) and amount > 0` và `amount <= self._quantity` (ném `ValueError` nếu sai kiểu, `<= 0` hoặc vượt quá tồn kho hiện tại, bảo đảm không cho tồn kho âm). Dành riêng cho `StockService` khi xuất kho hoặc rollback.
  - *Lưu ý về bản chất đóng gói trong Python:* Việc bảo vệ `quantity` và các phương thức `increase_stock`/`decrease_stock` là cơ chế đóng gói ở mức thiết kế kiến trúc và hợp đồng API (API Contract Invariants). Do đặc thù ngôn ngữ Python không có cơ chế chặn truy cập tuyệt đối ở mức runtime (*"we are all consenting adults"*), các phương thức này không được xem là cơ chế phân quyền bảo mật tuyệt đối. Sự toàn vẹn tồn kho phụ thuộc vào việc tuân thủ triệt để luồng điều phối của `StockService` và hợp đồng này.
  - `is_valid(self) -> bool`: Kiểm tra hợp lệ dữ liệu đối tượng.
  - `get_inventory_value(self) -> float`: Trả về `round(self.price * self.quantity, 2)`.
  - `to_dict(self) -> dict[str, Any]`: Chuyển thành dict gồm `"type": "Product"`, `product_id`, `name`, `price`, `quantity`, `supplier_id`.
  - `__str__(self) -> str`: Định dạng hiển thị Console.

##### Lớp `FoodProduct(Product)` (Kế thừa từ `Product`)
- **Thuộc tính bổ sung:**
  - `_expiry_date: datetime.date` (xử lý kiểu `date` theo Q09, nhận từ chuỗi `YYYY-MM-DD` hoặc `date`).
- **Phương thức:**
  - `__init__(self, product_id: str, name: str, price: float, quantity: int = 0, supplier_id: str = "", expiry_date: str | datetime.date = "") -> None`
  - `@property` `expiry_date` getter/setter (chuyển đổi và kiểm tra format).
  - `is_valid(self) -> bool`: Ghi đè, kiểm tra thêm tính hợp lệ của ngày hết hạn.
  - `is_expired(self, current_date: datetime.date | None = None) -> bool`: Trả về `True` nếu đã quá hạn tính đến `current_date` (mặc định hôm nay).
  - `days_until_expiry(self, current_date: datetime.date | None = None) -> int`: Số ngày còn lại đến hạn.
  - `to_dict(self) -> dict[str, Any]`: Ghi đè, thêm trường `"type": "FoodProduct"` và `"expiry_date": "YYYY-MM-DD"`.
  - `__str__(self) -> str`: Hiển thị kèm hạn sử dụng và trạng thái hết hạn.

##### Lớp `ElectronicProduct(Product)` (Kế thừa từ `Product`)
- **Thuộc tính bổ sung:**
  - `_warranty_months: int` (số tháng bảo hành `>= 0` theo Q11).
- **Phương thức:**
  - `__init__(self, product_id: str, name: str, price: float, quantity: int = 0, supplier_id: str = "", warranty_months: int = 0) -> None`
  - `@property` `warranty_months` getter/setter (kiểm tra `>= 0`).
  - `is_valid(self) -> bool`: Ghi đè, kiểm tra tính hợp lệ của `warranty_months`.
  - `to_dict(self) -> dict[str, Any]`: Ghi đè, thêm trường `"type": "ElectronicProduct"` và `"warranty_months": int`.
  - `__str__(self) -> str`: Hiển thị kèm thời hạn bảo hành (tháng).

---

#### 1.2. `models/supplier.py` (Minh phụ trách)

##### Lớp `Supplier`
- **Thuộc tính:**
  - `_supplier_id: str` (mã nhà cung cấp, duy nhất theo Q16)
  - `_name: str` (tên nhà cung cấp)
  - `_phone: str` (số điện thoại)
  - `_address: str` (địa chỉ)
  - `_email: str` (email liên hệ)
- **Phương thức:**
  - `__init__(self, supplier_id: str, name: str, phone: str = "", address: str = "", email: str = "") -> None`
  - `@property` getter/setter cho các trường có validation.
  - `is_valid(self) -> bool`: Kiểm tra hợp lệ mã và tên không được rỗng.
  - `to_dict(self) -> dict[str, Any]`: Xuất dict để lưu trữ JSON.
  - `__str__(self) -> str`: Định dạng hiển thị thông tin nhà cung cấp.

---

#### 1.3. `models/stock_transaction.py` (Chi phụ trách)

##### Lớp `StockTransaction`
- **Thuộc tính:**
  - `_transaction_id: str` (sinh tự động bằng `uuid.uuid4()` theo Q25)
  - `_product_id: str` (mã sản phẩm giao dịch)
  - `_transaction_type: str` (`"IMPORT"` hoặc `"EXPORT"`)
  - `_quantity: int` (số lượng giao dịch `> 0`)
  - `_timestamp: str` (thời điểm giao dịch dạng ISO có timezone theo Q26)
  - `_note: str` (ghi chú giao dịch)
- **Phương thức:**
  - `__init__(self, transaction_id: str, product_id: str, transaction_type: str, quantity: int, timestamp: str, note: str = "") -> None`
  - `@property` getter chỉ đọc (read-only theo Q28).
  - `to_dict(self) -> dict[str, Any]`: Xuất dict để lưu trữ JSON.
  - `__str__(self) -> str`: Định dạng hiển thị lịch sử giao dịch.

---

### 2. Tầng Nghiệp Vụ (`services/`)

#### 2.1. `services/inventory_manager.py` (Sơn phụ trách)

##### Lớp `InventoryManager`
- **Cấu trúc lưu trữ:** `_products: dict[str, Product]` (theo Q17).
- **Phương thức chi tiết:**

| Tên phương thức | Tham số đầu vào | Kiểu trả về | Mô tả & Ràng buộc ngoại lệ |
| :--- | :--- | :--- | :--- |
| `__init__` | không có | `None` | Khởi tạo từ điển rỗng `_products = {}`. |
| `add_product` | `product: Product, supplier_service: SupplierService | None = None` | `None` | Kiểm tra: `product.is_valid()`, `product.product_id` chưa tồn tại trong `_products` (trùng ném `ValueError` theo Q06), và `supplier_id` phải tồn tại trong `supplier_service` (nếu có truyền, ném `ValueError` theo Q14). |
| `update_product` | `product_id: str, **fields` | `None` | Cập nhật thông tin `name`, `price`, `supplier_id`, `expiry_date`, `warranty_months`. **Tuyệt đối cấm cập nhật `quantity`** (ném `ValueError` nếu `fields` chứa `quantity` theo Q08). Ném `KeyError` nếu không tìm thấy `product_id`. |
| `delete_product` | `product_id: str, stock_service: StockService | None = None` | `None` | Ném `KeyError` nếu không tìm thấy sản phẩm. Ném `ValueError` nếu `product.quantity > 0` (theo Q19). Nếu có truyền `stock_service`, gọi `stock_service.has_product_transactions(product_id)`: ném `ValueError` nếu đã phát sinh giao dịch (theo Q20). Xác thực trực tiếp ở tầng service, không phụ thuộc vào boolean từ CLI. |
| `get_product_by_id` | `product_id: str` | `Product` | **Ném `KeyError` nếu không tìm thấy mã sản phẩm** (theo Q18, không trả về `None`). |
| `get_all_products` | không có | `list[Product]` | Trả về bản sao danh sách tất cả sản phẩm (trả về `[]` nếu kho rỗng). |
| `search_product` | `keyword: str, by: str = "name"` | `list[Product]` | `by` thuộc `{"id", "name", "supplier"}`. Nếu `by == "name"`, so sánh không phân biệt hoa/thường nhưng giữ nguyên dấu tiếng Việt (theo Q21). |
| `sort_products` | `by: str = "price", reverse: bool = False` | `list[Product]` | `by` thuộc `{"price", "quantity"}`. `reverse=False` là tăng dần, `reverse=True` là giảm dần (theo Q22). |

---

#### 2.2. `services/supplier_service.py` (Minh phụ trách – Module mới theo Q16)

##### Lớp `SupplierService`
- **Cấu trúc lưu trữ:** `_suppliers: dict[str, Supplier]` (khóa chính là `supplier_id`).
- **Phương thức chi tiết:**

| Tên phương thức | Tham số đầu vào | Kiểu trả về | Mô tả & Ràng buộc ngoại lệ |
| :--- | :--- | :--- | :--- |
| `__init__` | không có | `None` | Khởi tạo `_suppliers = {}`. |
| `add_supplier` | `supplier: Supplier` | `None` | Kiểm tra `supplier.is_valid()`, ném `ValueError` nếu `supplier_id` đã tồn tại (theo Q16). |
| `update_supplier` | `supplier_id: str, **fields` | `None` | Ném `KeyError` nếu `supplier_id` không tồn tại. Cập nhật các trường `name`, `phone`, `address`, `email`. |
| `delete_supplier` | `supplier_id: str, inventory_manager: InventoryManager | None = None` | `None` | Ném `KeyError` nếu không tìm thấy. Nếu có truyền `inventory_manager`, kiểm tra xem có bất kỳ sản phẩm nào có `p.supplier_id == supplier_id`: ném `ValueError` nếu đang bị tham chiếu (theo Q15). Ràng buộc toàn vẹn thực thi trực tiếp tại service. |
| `get_supplier_by_id`| `supplier_id: str` | `Supplier` | Ném `KeyError` nếu không tìm thấy. |
| `get_all_suppliers` | không có | `list[Supplier]` | Trả về danh sách tất cả nhà cung cấp (`[]` nếu rỗng). |
| `has_supplier` | `supplier_id: str` | `bool` | Kiểm tra nhanh sự tồn tại của nhà cung cấp. |

---

#### 2.3. `services/stock_service.py` (Chi phụ trách)

##### Lớp `StockService`
- **Thuộc tính & Lưu trữ:**
  - `_inventory_manager: InventoryManager` (nhận qua constructor)
  - `_transactions: list[StockTransaction]` (danh sách lịch sử, chỉ đọc theo Q28)
- **Phương thức chi tiết:**

| Tên phương thức | Tham số đầu vào | Kiểu trả về | Mô tả & Ràng buộc ngoại lệ |
| :--- | :--- | :--- | :--- |
| `__init__` | `inventory_manager: InventoryManager` | `None` | Lưu tham chiếu `InventoryManager` và khởi tạo `_transactions = []`. |
| `import_stock` | `product_id: str, quantity: int, note: str = ""` | `StockTransaction` | 1. Kiểm tra `isinstance(quantity, int) and not isinstance(quantity, bool) and quantity > 0` (theo Q23).<br>2. Gọi `inventory_manager.get_product_by_id(product_id)` (ném `KeyError` nếu không thấy).<br>3. Nếu là `FoodProduct` và `is_expired() == True`, từ chối nhập và ném `ValueError` (theo Q10).<br>4. Tăng số lượng qua `product.increase_stock(quantity)`.<br>5. Sinh UUID cho `transaction_id` (theo Q25), ghi nhận thời gian ISO.<br>6. Thêm vào `_transactions`. Nếu có lỗi xảy ra khi tạo giao dịch hoặc lưu trữ, thực hiện atomic rollback: gọi `product.decrease_stock(quantity)` để hoàn nguyên (theo Q27). |
| `export_stock` | `product_id: str, quantity: int, note: str = ""` | `StockTransaction` | 1. Kiểm tra `quantity` là số nguyên dương hợp lệ (theo Q23).<br>2. Lấy sản phẩm từ `inventory_manager` (KeyError nếu không thấy).<br>3. Kiểm tra `quantity <= product.quantity`. Nếu vượt tồn, ném `ValueError` (theo Q23). Cho phép xuất hết về 0 (theo Q24).<br>4. Giảm số lượng qua `product.decrease_stock(quantity)`.<br>5. Tạo và lưu `StockTransaction`. Nếu thất bại, thực hiện atomic rollback: gọi `product.increase_stock(quantity)` để hoàn nguyên số lượng tồn kho (theo Q27). |
| `get_transaction_history` | `product_id: str | None = None` | `list[StockTransaction]` | Trả về danh sách giao dịch (toàn bộ hoặc lọc theo `product_id`). Danh sách chỉ đọc (theo Q28). |
| `has_product_transactions` | `product_id: str` | `bool` | Kiểm tra xem sản phẩm đã từng phát sinh giao dịch nào chưa (hỗ trợ Q20 cho `delete_product`). |

---

#### 2.4. `services/report_service.py` (Minh phụ trách)

##### Lớp `ReportService`
- **Thuộc tính & Lưu trữ:**
  - `_inventory_manager: InventoryManager` (nhận qua constructor)
  - Không quản lý CRUD nhà cung cấp (đã tách sang `SupplierService` theo Q16).
- **Phương thức chi tiết:**

| Tên phương thức | Tham số đầu vào | Kiểu trả về | Mô tả & Ràng buộc ngoại lệ |
| :--- | :--- | :--- | :--- |
| `__init__` | `inventory_manager: InventoryManager` | `None` | Lưu tham chiếu `InventoryManager`. |
| `get_total_inventory_value` | không có | `dict[str, float]` | Trả về dict: `{"total_value": float, "expired_food_value": float}`. Tính tổng giá trị toàn bộ kho, đồng thời phân tách rõ giá trị của các thực phẩm đã hết hạn để cảnh báo riêng (theo Q32). |
| `get_low_stock_products` | `threshold: int = 5` | `list[Product]` | Kiểm tra `threshold >= 0`. Trả về danh sách sản phẩm có `0 <= quantity <= threshold` (theo Q29). |
| `get_expiring_food_products` | `days: int = 7` | `list[FoodProduct]` | Kiểm tra `days >= 0`. Trả về danh sách thực phẩm cận hạn (hạn còn `<= days` ngày) nhưng **chưa hết hạn** (theo Q30, Q31). |
| `check_food_expiry_status` | `product_id: str | None = None` | `list[dict[str, Any]]` | Phân loại rõ ràng 3 trạng thái: `"ĐÃ HẾT HẠN"`, `"CẬN HẠN"`, `"CÒN HẠN"` kèm số ngày còn lại (theo Q31). |
| `get_warranty_summary` | `product_id: str | None = None` | `list[dict[str, Any]]` | Thống kê danh sách thiết bị điện tử kèm thời hạn bảo hành danh nghĩa (`warranty_months`), không tự ý kết luận còn/hết bảo hành (theo Q11). |

---

### 3. Tầng Lưu Trữ (`storage/storage.py` – Tú phụ trách)

Toàn bộ nghiệp vụ đọc/ghi file được tập trung tại `storage/storage.py` (dưới dạng các hàm module utility hoặc lớp `Storage` tĩnh theo Q33, Q34, Q35):

- **Cấu trúc File JSON (`data/inventory_data.json`):**
```json
{
  "products": [
    {
      "type": "Product",
      "product_id": "SP001",
      "name": "Bút bi",
      "price": 5000.0,
      "quantity": 100,
      "supplier_id": "NCC01"
    },
    {
      "type": "FoodProduct",
      "product_id": "TP001",
      "name": "Sữa tươi",
      "price": 12000.0,
      "quantity": 20,
      "supplier_id": "NCC02",
      "expiry_date": "2026-12-31"
    },
    {
      "type": "ElectronicProduct",
      "product_id": "DT001",
      "name": "Chuột không dây",
      "price": 250000.0,
      "quantity": 15,
      "supplier_id": "NCC03",
      "warranty_months": 24
    }
  ],
  "suppliers": [
    {
      "supplier_id": "NCC01",
      "name": "Công ty Văn Phòng Phẩm A",
      "phone": "0912345678",
      "address": "Hà Nội",
      "email": "contact@vppa.vn"
    }
  ],
  "transactions": [
    {
      "transaction_id": "c1a2b3c4-...",
      "product_id": "SP001",
      "transaction_type": "IMPORT",
      "quantity": 100,
      "timestamp": "2026-11-17T10:00:00+07:00",
      "note": "Nhập hàng đợt 1"
    }
  ]
}
```

- **Hàm `save_to_json(data: dict, file_path: str = "data/inventory_data.json") -> bool`:**
  - Nhận dict gồm `products`, `suppliers`, `transactions`.
  - Thực hiện ghi ra file tạm (ví dụ `data/inventory_data.json.tmp`) với `encoding="utf-8"`, `indent=2`, `ensure_ascii=False`.
  - Dùng `os.replace` để tráo đổi file nguyên tử (Atomic replace), bảo đảm không làm hỏng file dữ liệu cũ nếu quá trình ghi bị ngắt (theo Q34).
  - Trả về `True` nếu lưu thành công, `False` hoặc ném ngoại lệ nếu lỗi.
- **Hàm `load_from_json(file_path: str = "data/inventory_data.json") -> dict`:**
  - Đọc file tạm vào bộ nhớ. Nếu file chưa tồn tại, trả về cấu trúc rỗng `{"products": [], "suppliers": [], "transactions": []}`.
  - Kiểm tra cú pháp JSON và các trường bắt buộc; khôi phục đúng loại đối tượng kế thừa thông qua trường `"type"` (`Product`, `FoodProduct`, `ElectronicProduct`).
  - Kiểm tra toàn vẹn tham chiếu (kiểm tra `supplier_id` và mã trùng). Nếu phát hiện dữ liệu lỗi, ném `ValueError` và giữ nguyên trạng thái bộ nhớ hiện tại (theo Q34).
- **Hàm `export_to_csv(products: list[Product], file_path: str = "data/inventory_report.csv") -> None`:**
  - Xuất bảng sản phẩm với `encoding="utf-8-sig"` (tương thích mở trực tiếp trên Excel).
  - Các cột bắt buộc theo Q35: `product_id`, `name`, `product_type`, `price`, `quantity`, `inventory_value`, `supplier`.

---

### 4. Tầng Giao Diện Console (`cli/` – Tiến phụ trách)

#### 4.1. Lớp `AppContext`
Đóng vai trò Service Locator / Container quản lý vòng đời và truyền phụ thuộc:
```python
@dataclass
class AppContext:
    inventory_manager: InventoryManager
    stock_service: StockService
    supplier_service: SupplierService
    report_service: ReportService
    storage: Any
```

#### 4.2. Lớp `InventoryCLI`
- Khởi tạo nhận `context: AppContext`.
- Điều hướng menu vòng lặp `while` an toàn, bắt ngoại lệ `KeyError` và `ValueError`, in thông báo tiếng Việt theo Q38.
- Xử lý xác nhận xóa sản phẩm và xóa nhà cung cấp theo Q37.
- Cơ chế tự động lưu dữ liệu: Trước khi kết thúc vòng lặp tại `main()`, tự động gọi `save_to_json()` để bảo toàn dữ liệu theo Q05.
