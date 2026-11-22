# Thiết Kế UML Lưu Đồ Hoạt Động (Activity Diagram) – v1.0

- **Hệ thống:** Product Inventory Management System
- **Chuẩn thiết kế:** Approved Design v1.0 (Khớp 40 quyết định thiết kế chính thức)
- **Tài liệu đối chiếu:** [API_CONTRACT.md](../API_CONTRACT.md), [TASK_ASSIGNMENT.md](../TASK_ASSIGNMENT.md)

---

## 1. LƯU ĐỒ HOẠT ĐỘNG: THÊM SẢN PHẨM MỚI (ADD PRODUCT)

Quy trình thể hiện việc kiểm tra mã sản phẩm không trùng (Q06), đơn giá không âm (Q07), kiểm tra sự tồn tại của nhà cung cấp (Q14), phân nhánh cho sản phẩm đặc thù và khởi tạo tồn kho bằng 0 (Q08):

```mermaid
flowchart TD
    Start(["● Bắt đầu: Thêm sản phẩm"]) --> InputBasic["Người dùng nhập: Mã SP, Tên, Đơn giá, Loại SP, Mã NCC"]

    InputBasic --> CheckBasicValid{"Dữ liệu hợp lệ?\n(Mã/Tên không rỗng,\nĐơn giá >= 0)"}
    CheckBasicValid -- "Không" --> ErrBasic["Thông báo lỗi: Mã/Tên không được rỗng hoặc Đơn giá âm"]
    ErrBasic --> AskRetry{"Người dùng muốn thử lại?\n(Q36)"}
    AskRetry -- "Có" --> InputBasic
    AskRetry -- "Không" --> EndFail(["● Kết thúc: Hủy thao tác"])

    CheckBasicValid -- "Hợp lệ" --> CheckDup{"Mã SP đã tồn tại\ntrong InventoryManager?\n(Q06)"}
    CheckDup -- "Đã tồn tại" --> ErrDup["Ném ValueError: Trùng mã sản phẩm"]
    ErrDup --> AskRetry

    CheckDup -- "Chưa tồn tại" --> CheckSup{"Mã NCC có tồn tại\ntrong SupplierService?\n(Q14)"}
    CheckSup -- "Không tồn tại" --> ErrSup["Ném ValueError: Nhà cung cấp chưa tồn tại trong hệ thống"]
    ErrSup --> AskRetry

    CheckSup -- "Hợp lệ" --> BranchType{"Loại sản phẩm được chọn?"}

    BranchType -- "Thực phẩm (FoodProduct)" --> InputExpiry["Nhập ngày hết hạn (YYYY-MM-DD)"]
    InputExpiry --> CheckExpiryValid{"Định dạng ngày\nhợp lệ? (Q09)"}
    CheckExpiryValid -- "Sai định dạng" --> ErrExpiry["Báo lỗi định dạng ngày không hợp lệ"]
    ErrExpiry --> InputExpiry
    CheckExpiryValid -- "Hợp lệ" --> CreateFood["Khởi tạo FoodProduct\n(quantity = 0, expiry_date)"]

    BranchType -- "Điện tử (ElectronicProduct)" --> InputWarranty["Nhập số tháng bảo hành (warranty_months)"]
    InputWarranty --> CheckWarrantyValid{"Số tháng >= 0?\n(Q11)"}
    CheckWarrantyValid -- "Số âm / Sai kiểu" --> ErrWarranty["Báo lỗi: Số tháng bảo hành phải là số nguyên >= 0"]
    ErrWarranty --> InputWarranty
    CheckWarrantyValid -- "Hợp lệ" --> CreateElec["Khởi tạo ElectronicProduct\n(quantity = 0, warranty_months)"]

    BranchType -- "Thông thường (Product)" --> CreateProd["Khởi tạo Product cơ sở\n(quantity = 0)"]

    CreateFood --> SaveManager["Lưu đối tượng vào InventoryManager\n(_products[product_id] = product)"]
    CreateElec --> SaveManager
    CreateProd --> SaveManager

    SaveManager --> ShowSuccess["Hiển thị thông báo: Thêm sản phẩm thành công!"]
    ShowSuccess --> EndSuccess(["● Kết thúc: Thành công"])
```

---

## 2. LƯU ĐỒ HOẠT ĐỘNG: CẬP NHẬT VÀ XÓA SẢN PHẨM (UPDATE & DELETE PRODUCT)

### 2.1. Hoạt động Cập nhật Sản phẩm (Update Product)
Quy trình bảo đảm không cho phép cập nhật trực tiếp số lượng tồn kho `quantity` (Q08):

```mermaid
flowchart TD
    StartUpdate(["● Bắt đầu: Cập nhật sản phẩm"]) --> InputId["Người dùng nhập Mã SP cần cập nhật"]
    InputId --> CheckExist{"Sản phẩm có tồn tại\ntrong kho? (Q18)"}

    CheckExist -- "Không tồn tại" --> ErrNotFound["Ném KeyError: Không tìm thấy sản phẩm trong kho"]
    ErrNotFound --> AskRetryUp{"Người dùng thử lại?"}
    AskRetryUp -- "Có" --> InputId
    AskRetryUp -- "Không" --> EndFailUp(["● Kết thúc: Hủy thao tác"])

    CheckExist -- "Tìm thấy" --> InputFields["Nhập các trường cần sửa: Tên, Giá, Hạn dùng/Bảo hành, Mã NCC"]
    InputFields --> CheckQtyAttempt{"Người dùng có cố ý\nsửa số lượng (quantity) không? (Q08)"}

    CheckQtyAttempt -- "Có" --> ErrForbidQty["Ném ValueError: Cấm sửa trực tiếp số lượng tồn kho qua CRUD!\n(Số lượng chỉ được thay đổi qua Nhập/Xuất kho)"]
    ErrForbidQty --> InputFields

    CheckQtyAttempt -- "Không" --> ValidateNewFields{"Các trường mới\nhợp lệ? (Giá >= 0, NCC hợp lệ)"}
    ValidateNewFields -- "Không hợp lệ" --> ErrFields["Thông báo lỗi dữ liệu không hợp lệ"]
    ErrFields --> InputFields

    ValidateNewFields -- "Hợp lệ" --> ApplyUpdate["Cập nhật thuộc tính của Product\ntrong InventoryManager"]
    ApplyUpdate --> SuccessUp["Thông báo: Cập nhật sản phẩm thành công!"]
    SuccessUp --> EndSuccessUp(["● Kết thúc: Thành công"])
```

### 2.2. Hoạt động Xóa Sản phẩm (Delete Product)
Quy trình đảm bảo kiểm tra toàn diện 2 điều kiện tại tầng Service (tồn kho bằng 0 theo Q19 và chưa từng có lịch sử giao dịch theo Q20, độc lập không phụ thuộc cờ boolean từ tầng hiển thị), kết hợp hỏi xác nhận người dùng tại CLI (Q37):

```mermaid
flowchart TD
    StartDel(["● Bắt đầu: Xóa sản phẩm"]) --> InputDelId["Người dùng nhập Mã SP cần xóa tại CLI"]
    InputDelId --> PromptConfirm{"CLI yêu cầu xác nhận (Q37):\n'Bạn có chắc chắn muốn xóa sản phẩm này? (c/k)'"}
    
    PromptConfirm -- "Từ chối (k)" --> CancelDel["Thông báo: Đã hủy thao tác xóa sản phẩm"]
    CancelDel --> EndDelFail(["● Kết thúc: Hủy xóa"])

    PromptConfirm -- "Đồng ý (c)" --> CallService["CLI gọi Service:\nInventoryManager.delete_product(product_id, stock_service)"]
    
    CallService --> CheckDelExist{"Sản phẩm có tồn tại\ntrong kho? (Q18)"}
    CheckDelExist -- "Không tồn tại" --> ErrDelNotFound["Tầng Service ném KeyError: Mã sản phẩm không tồn tại"]
    ErrDelNotFound --> ShowErrCLI["CLI bắt lỗi và hiển thị thông báo tiếng Việt (Q38)"]
    ShowErrCLI --> EndDelFail

    CheckDelExist -- "Tồn tại" --> CheckStockQty{"Số lượng tồn kho\nquantity > 0? (Q19)"}
    CheckStockQty -- "Còn tồn kho (> 0)" --> ErrHasStock["Tầng Service ném ValueError: Không thể xóa khi tồn kho vẫn > 0!\n(Vui lòng xuất hết tồn kho về 0 trước khi xóa)"]
    ErrHasStock --> ShowErrCLI

    CheckStockQty -- "Tồn kho = 0" --> CheckHistory{"stock_service.has_product_transactions?\n(Đã từng phát sinh giao dịch nhập/xuất kho chưa? - Q20)"}
    CheckHistory -- "Đã có giao dịch" --> ErrHasHistory["Tầng Service ném ValueError: Không thể xóa sản phẩm đã có lịch sử giao dịch!\n(Nhằm bảo đảm tính toàn vẹn sổ sách kho)"]
    ErrHasHistory --> ShowErrCLI

    CheckHistory -- "Chưa có giao dịch" --> PerformDelete["Tầng Service xóa sản phẩm khỏi kho:\ndel _products[product_id]"]
    PerformDelete --> SuccessDel["CLI thông báo: Xóa sản phẩm khỏi danh mục thành công!"]
    SuccessDel --> EndDelSuccess(["● Kết thúc: Xóa thành công"])
```

---

## 3. LƯU ĐỒ HOẠT ĐỘNG: NHẬP KHO (IMPORT STOCK)

Quy trình thể hiện việc xác thực số nguyên dương (Q23), từ chối thực phẩm đã hết hạn (Q10), tạo giao dịch UUID (Q25), bảo toàn tính nguyên tử (Q27) và lưu lịch sử bất biến (Q28):

```mermaid
flowchart TD
    StartImport(["● Bắt đầu: Nhập kho"]) --> InputImportData["Người dùng nhập: Mã SP, Số lượng nhập, Ghi chú"]

    InputImportData --> CheckValidInt{"Số lượng nhập là số nguyên\ndương hợp lệ? (quantity > 0, not bool)\n(Q23)"}
    CheckValidInt -- "Không hợp lệ" --> ErrInt["Ném ValueError: Số lượng nhập phải là số nguyên > 0"]
    ErrInt --> AskRetryImp{"Thử lại?"}
    AskRetryImp -- "Có" --> InputImportData
    AskRetryImp -- "Không" --> EndImpFail(["● Kết thúc: Hủy nhập kho"])

    CheckValidInt -- "Hợp lệ" --> CheckProductExist{"Sản phẩm có tồn tại\ntrong InventoryManager? (Q18)"}
    CheckProductExist -- "Không tồn tại" --> ErrProdNotFound["Ném KeyError: Mã sản phẩm không tồn tại trong kho"]
    ErrProdNotFound --> AskRetryImp

    CheckProductExist -- "Tồn tại" --> CheckFoodExpired{"Sản phẩm là FoodProduct\nvà đã hết hạn (is_expired)? (Q10)"}
    CheckFoodExpired -- "Đã hết hạn" --> ErrExpired["Ném ValueError: Cảnh báo! Không cho phép nhập thêm thực phẩm đã hết hạn vào kho"]
    ErrExpired --> EndImpFail

    CheckFoodExpired -- "Hợp lệ" --> CallIncreaseStock["StockService gọi:\nproduct.increase_stock(quantity)"]
    CallIncreaseStock --> CheckIncSuccess{"Tăng tồn kho\nthành công?\n(stock_changed = True)"}
    CheckIncSuccess -- "Thất bại" --> ErrIncFailed["Ném ngoại lệ: Lỗi khi tăng tồn kho (chưa thay đổi dữ liệu)"]
    ErrIncFailed --> EndImpFail

    CheckIncSuccess -- "Thành công" --> CreateTransaction["Khởi tạo StockTransaction:\n- transaction_id = str(uuid.uuid4()) (Q25)\n- type = 'IMPORT'\n- timestamp = now(timezone) (Q26)\n- quantity, product_id, note"]

    CreateTransaction --> TrySaveTx{"Lưu giao dịch vào danh sách\n_transactions thành công? (Q27)"}
    TrySaveTx -- "Thất bại / Lỗi hệ thống" --> TryRollback["HOÀN TÁC (ROLLBACK):\nStockService gọi product.decrease_stock(quantity)"]
    TryRollback --> CheckRollbackSuccess{"Hoàn tác tồn kho\nthành công?"}
    CheckRollbackSuccess -- "Thành công" --> ErrRollbackOk["Báo lỗi: Ghi nhận giao dịch thất bại. Tồn kho đã được hoàn tác an toàn bằng decrease_stock!"]
    ErrRollbackOk --> EndImpFail
    CheckRollbackSuccess -- "Thất bại / Lỗi" --> ErrRollbackFail["Báo lỗi nghiêm trọng: Ghi nhận giao dịch thất bại VÀ hoàn tác tồn kho gặp sự cố!\nDữ liệu có thể không nhất quán, cần kiểm tra lại."]
    ErrRollbackFail --> EndImpFail

    TrySaveTx -- "Thành công" --> ShowImpSuccess["Hiển thị: Nhập kho thành công!\n(In chi tiết mã giao dịch, tồn kho mới)"]
    ShowImpSuccess --> EndImpSuccess(["● Kết thúc: Thành công"])
```

---

## 4. LƯU ĐỒ HOẠT ĐỘNG: XUẤT KHO (EXPORT STOCK)

Quy trình nghiệp vụ xuất kho kiểm tra tồn kho đủ, cho phép xuất hết về 0 (Q24), hoàn tác tự động nếu xảy ra lỗi ghi nhận giao dịch (Q27):

```mermaid
flowchart TD
    StartExport(["● Bắt đầu: Xuất kho"]) --> InputExportData["Người dùng nhập: Mã SP, Số lượng xuất, Ghi chú"]

    InputExportData --> CheckExpInt{"Số lượng xuất là số nguyên\ndương hợp lệ? (quantity > 0, not bool)\n(Q23)"}
    CheckExpInt -- "Không hợp lệ" --> ErrExpInt["Ném ValueError: Số lượng xuất phải là số nguyên > 0"]
    ErrExpInt --> AskRetryExp{"Thử lại?"}
    AskRetryExp -- "Có" --> InputExportData
    AskRetryExp -- "Không" --> EndExpFail(["● Kết thúc: Hủy xuất kho"])

    CheckExpInt -- "Hợp lệ" --> CheckExpProdExist{"Sản phẩm có tồn tại\ntrong InventoryManager? (Q18)"}
    CheckExpProdExist -- "Không tồn tại" --> ErrExpNotFound["Ném KeyError: Mã sản phẩm không tồn tại trong kho"]
    ErrExpNotFound --> AskRetryExp

    CheckExpProdExist -- "Tồn tại" --> CheckStockAdequate{"Số lượng xuất <= product.quantity?\n(Kiểm tra tồn kho đủ - Q23, Q24)"}
    CheckStockAdequate -- "Vượt tồn kho" --> ErrOverStock["Ném ValueError: Số lượng xuất vượt quá tồn kho hiện tại!\n(Tồn hiện tại: product.quantity)"]
    ErrOverStock --> AskRetryExp

    CheckStockAdequate -- "Tồn kho đủ (cho phép về 0)" --> CallDecreaseStock["StockService gọi:\nproduct.decrease_stock(quantity)"]
    CallDecreaseStock --> CheckDecSuccess{"Giảm tồn kho\nthành công?\n(stock_changed = True)"}
    CheckDecSuccess -- "Thất bại" --> ErrDecFailed["Ném ngoại lệ: Lỗi khi giảm tồn kho (chưa thay đổi dữ liệu)"]
    ErrDecFailed --> EndExpFail

    CheckDecSuccess -- "Thành công" --> CreateExpTx["Khởi tạo StockTransaction:\n- transaction_id = str(uuid.uuid4()) (Q25)\n- type = 'EXPORT'\n- timestamp = now(timezone) (Q26)\n- quantity, product_id, note"]

    CreateExpTx --> TrySaveExpTx{"Lưu giao dịch vào danh sách\n_transactions thành công? (Q27)"}
    TrySaveExpTx -- "Thất bại / Lỗi hệ thống" --> TryExpRollback["HOÀN TÁC (ROLLBACK):\nStockService gọi product.increase_stock(quantity)"]
    TryExpRollback --> CheckExpRollbackSuccess{"Hoàn tác tồn kho\nthành công?"}
    CheckExpRollbackSuccess -- "Thành công" --> ErrExpRollbackOk["Báo lỗi: Ghi nhận giao dịch thất bại. Tồn kho đã được hoàn tác an toàn bằng increase_stock!"]
    ErrExpRollbackOk --> EndExpFail
    CheckExpRollbackSuccess -- "Thất bại / Lỗi" --> ErrExpRollbackFail["Báo lỗi nghiêm trọng: Ghi nhận giao dịch thất bại VÀ hoàn tác tồn kho gặp sự cố!\nDữ liệu có thể không nhất quán, cần kiểm tra lại."]
    ErrExpRollbackFail --> EndExpFail

    TrySaveExpTx -- "Thành công" --> ShowExpSuccess["Hiển thị: Xuất kho thành công!\n(In chi tiết mã giao dịch, tồn kho còn lại)"]
    ShowExpSuccess --> EndExpSuccess(["● Kết thúc: Thành công"])
```

