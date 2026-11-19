# Thiết Kế UML Sơ Đồ Tuần Tự (Sequence Diagram) – v1.0

- **Hệ thống:** Product Inventory Management System
- **Chuẩn thiết kế:** Approved Design v1.0 (Khớp 40 quyết định thiết kế chính thức)
- **Tài liệu đối chiếu:** [API_CONTRACT.md](../API_CONTRACT.md), [TASK_ASSIGNMENT.md](../TASK_ASSIGNMENT.md)

---

## 1. SƠ ĐỒ TUẦN TỰ: THÊM SẢN PHẨM MỚI (ADD PRODUCT)

Minh họa sự tương tác giữa CLI, `SupplierService`, `Product` entity và `InventoryManager`, kiểm tra mã nhà cung cấp tồn tại (Q14) và chống trùng mã sản phẩm (Q06):

```mermaid
sequenceDiagram
    autonumber
    actor User as Thủ kho
    participant CLI as InventoryCLI (Menu 1)
    participant SS as SupplierService
    participant P as Product / Subclasses
    participant IM as InventoryManager

    User->>CLI: Nhập thông tin SP (mã, tên, giá, mã NCC, loại SP,...)
    CLI->>SS: has_supplier(supplier_id)
    alt Mã nhà cung cấp chưa tồn tại (Q14)
        SS-->>CLI: False
        CLI-->>User: Báo lỗi: Nhà cung cấp chưa tồn tại trong hệ thống (Q14)
    else Mã nhà cung cấp hợp lệ
        SS-->>CLI: True
        CLI->>P: Khởi tạo đối tượng Product(...) với quantity = 0
        Note over P: Kiểm tra dữ liệu đầu vào (Giá >= 0, validate thuộc tính)
        CLI->>IM: add_product(product, supplier_service)
        IM->>IM: Kiểm tra product_id đã có trong _products chưa (Q06)
        alt Trùng mã sản phẩm (Q06)
            IM-->>CLI: Ném ValueError("Mã sản phẩm đã tồn tại")
            CLI-->>User: Hiển thị thông báo lỗi trùng mã, yêu cầu nhập lại
        else Mã sản phẩm hợp lệ
            IM->>IM: Lưu vào từ điển: _products[product_id] = product
            IM-->>CLI: Thêm thành công
            CLI-->>User: Thông báo: Thêm sản phẩm vào kho thành công!
        end
    end
```

---

## 2. SƠ ĐỒ TUẦN TỰ: NHẬP KHO (IMPORT STOCK)

Minh họa nghiệp vụ nhập kho, kiểm tra số nguyên dương (Q23), `get_product_by_id` ném `KeyError` (Q18), từ chối thực phẩm hết hạn (Q10) và sinh mã UUID (Q25):

```mermaid
sequenceDiagram
    autonumber
    actor User as Thủ kho
    participant CLI as InventoryCLI (Menu 3)
    participant StkSvc as StockService
    participant IM as InventoryManager
    participant P as Product / FoodProduct
    participant TX as StockTransaction

    User->>CLI: Nhập Mã SP, Số lượng nhập, Ghi chú
    CLI->>StkSvc: import_stock(product_id, quantity, note)
    
    alt Số lượng không phải số nguyên dương (Q23)
        StkSvc-->>CLI: Ném ValueError("Số lượng nhập phải là số nguyên > 0")
        CLI-->>User: Báo lỗi: Số lượng nhập không hợp lệ
    else Số lượng hợp lệ
        StkSvc->>IM: get_product_by_id(product_id)
        alt Không tìm thấy sản phẩm (Q18)
            IM-->>StkSvc: Ném KeyError("Không tìm thấy mã SP")
            StkSvc-->>CLI: Truyền tiếp KeyError
            CLI-->>User: Báo lỗi: Mã sản phẩm không tồn tại trong kho
        else Tìm thấy sản phẩm
            IM-->>StkSvc: Trả về đối tượng Product
            alt Sản phẩm là FoodProduct và is_expired() == True (Q10)
                StkSvc-->>CLI: Ném ValueError("Cảnh báo! Không cho phép nhập thực phẩm đã hết hạn")
                CLI-->>User: Hiển thị cảnh báo từ chối nhập thực phẩm hết hạn
            else Sản phẩm hợp lệ để nhập
                StkSvc->>P: increase_stock(quantity)
                alt Tăng tồn kho thất bại (Tham số sai kiểu / số âm)
                    P-->>StkSvc: Ném ValueError (amount <= 0 hoặc bool)
                    StkSvc-->>CLI: Ném ValueError
                    CLI-->>User: Báo lỗi: Số lượng không hợp lệ, không thể tăng tồn kho
                else Tăng tồn kho thành công (stock_changed = True)
                    P-->>StkSvc: Cập nhật _quantity thành công
                    StkSvc->>TX: Khởi tạo StockTransaction(UUID, "IMPORT", qty, timestamp, ...)
                    alt Lưu giao dịch thành công (Q27)
                        StkSvc->>StkSvc: _transactions.append(transaction)
                        StkSvc-->>CLI: Trả về StockTransaction
                        CLI-->>User: Thông báo nhập kho thành công & In chi tiết
                    else Lưu giao dịch bị lỗi (Ngoại lệ hệ thống)
                        Note over StkSvc: Chỉ kích hoạt rollback vì ban đầu increase_stock đã thành công
                        StkSvc->>P: decrease_stock(quantity) (Hoàn tác tồn kho)
                        alt Hoàn tác thành công
                            P-->>StkSvc: Đã giảm tồn kho về mức ban đầu
                            StkSvc-->>CLI: Ném RuntimeError("Lỗi ghi nhận giao dịch, đã hoàn tác tồn kho an toàn")
                            CLI-->>User: Báo lỗi: Nhập kho thất bại, đã hoàn tác tồn kho an toàn!
                        else Hoàn tác gặp sự cố
                            P-->>StkSvc: Ném ngoại lệ khi decrease_stock
                            StkSvc-->>CLI: Ném RuntimeError("Giao dịch lỗi VÀ hoàn tác thất bại!")
                            CLI-->>User: Cảnh báo nghiêm trọng: Lỗi ghi giao dịch và hoàn tác gặp sự cố!
                        end
                    end
                end
            end
        end
    end
```

---

## 3. SƠ ĐỒ TUẦN TỰ: XUẤT KHO (EXPORT STOCK) VỚI CÁC NHÁNH ALT

Minh họa chi tiết toàn bộ các nhánh rẽ (`alt`) khi xuất kho: lỗi số lượng, `KeyError`, xuất vượt tồn, xuất hết về 0 (Q24) và hoàn tác rollback khi ghi nhận giao dịch thất bại (Q27):

```mermaid
sequenceDiagram
    autonumber
    actor User as Thủ kho
    participant CLI as InventoryCLI (Menu 3)
    participant StkSvc as StockService
    participant IM as InventoryManager
    participant P as Product
    participant TX as StockTransaction

    User->>CLI: Nhập Mã SP, Số lượng xuất, Ghi chú
    CLI->>StkSvc: export_stock(product_id, quantity, note)

    alt 1. Số lượng <= 0 hoặc sai kiểu dữ liệu (Q23)
        StkSvc-->>CLI: Ném ValueError("Số lượng xuất phải là số nguyên > 0")
        CLI-->>User: Hiển thị lỗi: Số lượng xuất phải là số nguyên dương
    else 2. Không tìm thấy sản phẩm trong kho (Q18)
        StkSvc->>IM: get_product_by_id(product_id)
        IM-->>StkSvc: Ném KeyError("Mã SP không tồn tại")
        StkSvc-->>CLI: Ném KeyError
        CLI-->>User: Hiển thị lỗi: Không tìm thấy sản phẩm trong kho
    else 3. Số lượng xuất vượt tồn kho hiện tại (Q23)
        StkSvc->>IM: get_product_by_id(product_id)
        IM-->>StkSvc: Trả về Product (product.quantity)
        Note over StkSvc: Kiểm tra: quantity > product.quantity
        StkSvc-->>CLI: Ném ValueError("Số lượng xuất vượt quá tồn kho hiện tại")
        CLI-->>User: Hiển thị lỗi: Không đủ hàng tồn để xuất
    else 4. Số lượng xuất hợp lệ (bao gồm xuất hết về 0 - Q24)
        StkSvc->>IM: get_product_by_id(product_id)
        IM-->>StkSvc: Trả về Product
        StkSvc->>P: decrease_stock(quantity)
        alt Giảm tồn kho thất bại (Số lượng âm hoặc vượt tồn)
            P-->>StkSvc: Ném ValueError
            StkSvc-->>CLI: Ném ValueError
            CLI-->>User: Báo lỗi: Không thể giảm tồn kho
        else Giảm tồn kho thành công (stock_changed = True)
            P-->>StkSvc: Cập nhật giảm _quantity thành công
            StkSvc->>TX: Khởi tạo StockTransaction(UUID, "EXPORT", qty, timestamp, ...)
            alt Ghi nhận giao dịch thành công (Q27)
                StkSvc->>StkSvc: _transactions.append(tx)
                StkSvc-->>CLI: Trả về tx thành công
                CLI-->>User: Thông báo: Xuất kho thành công! (In số dư tồn mới)
            else Ghi nhận giao dịch gặp sự cố (Rollback - Q27)
                Note over StkSvc: Chỉ kích hoạt rollback vì ban đầu decrease_stock đã thành công
                StkSvc->>P: increase_stock(quantity) (Hoàn tác tồn kho)
                alt Hoàn tác thành công
                    P-->>StkSvc: Đã tăng tồn kho về mức ban đầu
                    StkSvc-->>CLI: Ném RuntimeError("Lỗi ghi nhận, đã hoàn tác tồn kho an toàn")
                    CLI-->>User: Báo lỗi hệ thống: Giao dịch bị hủy, đã hoàn tác tồn kho an toàn!
                else Hoàn tác gặp sự cố
                    P-->>StkSvc: Ném ngoại lệ khi increase_stock
                    StkSvc-->>CLI: Ném RuntimeError("Giao dịch lỗi VÀ hoàn tác thất bại!")
                    CLI-->>User: Cảnh báo nghiêm trọng: Giao dịch bị hủy và hoàn tác gặp sự cố!
                end
            end
        end
    end
```

---

## 4. SƠ ĐỒ TUẦN TỰ: XÓA SẢN PHẨM (DELETE PRODUCT)

Minh họa việc kiểm tra ràng buộc xóa hoàn toàn tại tầng Service (`InventoryManager` tự kiểm tra `quantity == 0` và gọi `StockService.has_product_transactions` theo Q19, Q20, không phụ thuộc cờ boolean từ CLI), kết hợp hỏi xác nhận người dùng (Q37):

```mermaid
sequenceDiagram
    autonumber
    actor User as Thủ kho
    participant CLI as InventoryCLI (Menu 1)
    participant IM as InventoryManager
    participant P as Product (Entity)
    participant StkSvc as StockService

    User->>CLI: Chọn chức năng Xóa SP, nhập product_id
    CLI->>User: Yêu cầu xác nhận (Q37): "Bạn có chắc chắn muốn xóa sản phẩm này? (c/k)"
    alt Người dùng từ chối ("k")
        User-->>CLI: Nhập "k"
        CLI-->>User: Thông báo: Đã hủy thao tác xóa sản phẩm
    else Người dùng đồng ý ("c")
        User-->>CLI: Nhập "c"
        CLI->>IM: delete_product(product_id, stock_service)
        
        Note over IM: Tầng Service tự kiểm tra toàn bộ ràng buộc (Q18, Q19, Q20)
        IM->>IM: get_product_by_id(product_id)
        alt 1. Không tìm thấy mã sản phẩm (Q18)
            IM-->>CLI: Ném KeyError("Mã sản phẩm không tồn tại")
            CLI-->>User: Hiển thị lỗi: Không tìm thấy sản phẩm cần xóa
        else 2. Tìm thấy sản phẩm
            IM->>P: Kiểm tra product.quantity
            alt Tồn kho vẫn lớn hơn 0 (product.quantity > 0) (Q19)
                IM-->>CLI: Ném ValueError("Không thể xóa sản phẩm khi tồn kho vẫn > 0")
                CLI-->>User: Hiển thị lỗi: Vui lòng xuất hết tồn kho về 0 trước khi xóa
            else Tồn kho = 0
                IM->>StkSvc: has_product_transactions(product_id)
                alt Đã từng phát sinh giao dịch nhập/xuất kho (Q20)
                    StkSvc-->>IM: True
                    IM-->>CLI: Ném ValueError("Không thể xóa sản phẩm đã có lịch sử giao dịch")
                    CLI-->>User: Hiển thị lỗi: Không được xóa sản phẩm đã có lịch sử giao dịch sổ kho
                else Chưa từng có giao dịch
                    StkSvc-->>IM: False
                    IM->>IM: Xóa khỏi từ điển: del _products[product_id]
                    IM-->>CLI: Xóa thành công
                    CLI-->>User: Thông báo: Xóa sản phẩm khỏi danh mục thành công!
                end
            end
        end
    end
```

---

## 5. SƠ ĐỒ TUẦN TỰ: TỰ ĐỘNG LƯU DỮ LIỆU KHI THOÁT ỨNG DỤNG (AUTO-SAVE ON EXIT)

Minh họa luồng thoát ứng dụng, xác nhận người dùng, thu thập trạng thái 3 thực thể (Q33) và ghi file an toàn nguyên tử (Q05, Q34), kèm cơ chế xử lý khi lưu thất bại (cho phép thử lại, hủy thoát, hoặc thoát không lưu):

```mermaid
sequenceDiagram
    autonumber
    actor User as Thủ kho
    participant CLI as InventoryCLI
    participant Ctx as AppContext
    participant IM as InventoryManager
    participant SS as SupplierService
    participant StkSvc as StockService
    participant Storage as Storage Utility
    participant Disk as Hệ thống File (Disk)

    User->>CLI: Chọn "0. Thoát chương trình"
    CLI->>User: Yêu cầu xác nhận: "Bạn có chắc chắn muốn thoát? (c/k)"
    User-->>CLI: Nhập "c" (Đồng ý thoát)
    
    loop Quy trình lưu an toàn (Hỗ trợ thử lại nếu lỗi)
        Note over CLI, Ctx: Thu thập trạng thái 3 thực thể (Q05, Q33)
        CLI->>Ctx: Chuẩn bị dữ liệu sao lưu
        Ctx->>IM: get_all_products()
        IM-->>Ctx: list[Product]
        Ctx->>SS: get_all_suppliers()
        SS-->>Ctx: list[Supplier]
        Ctx->>StkSvc: get_transaction_history()
        StkSvc-->>Ctx: list[StockTransaction]

        Ctx->>Storage: save_to_json(data={"products", "suppliers", "transactions"})
        Storage->>Disk: Ghi dữ liệu vào file tạm (inventory_data.json.tmp)
        alt Lưu thành công (Ghi file tạm & os.replace nguyên tử - Q34)
            Storage->>Disk: os.replace(tmp_file, "data/inventory_data.json")
            Storage-->>Ctx: True (Thành công)
            Ctx-->>CLI: Lưu thành công
            CLI-->>User: In thông báo: Dữ liệu đã được tự động lưu an toàn. Tạm biệt!
            CLI->>CLI: Dừng chương trình an toàn (Exit)
        else Lưu thất bại (Lỗi ổ đĩa / Thiếu quyền ghi file)
            Storage-->>Ctx: False / Raise OSError
            Ctx-->>CLI: Báo lỗi lưu dữ liệu
            CLI-->>User: Cảnh báo: Tự động lưu thất bại! Chọn cách xử lý: (1) Thử lưu lại | (2) Hủy thoát | (3) Thoát không lưu
            alt Lựa chọn 1: Thử lưu lại (Retry)
                User-->>CLI: Chọn (1) Thử lưu lại
                Note over CLI: Tiếp tục vòng lặp thử lưu lại lần nữa
            else Lựa chọn 2: Hủy thoát (Cancel Exit)
                User-->>CLI: Chọn (2) Hủy thoát
                CLI-->>User: Đã hủy thoát. Quay lại menu chính để kiểm tra hoặc lưu thủ công.
                Note over CLI: Quay lại menu chính, không dừng chương trình
            else Lựa chọn 3: Thoát không lưu (Force Exit)
                User-->>CLI: Chọn (3) Thoát không lưu
                CLI->>User: Xác nhận: "Cảnh báo: Dữ liệu chưa lưu sẽ bị mất! Bạn có chắc chắn? (c/k)"
                alt Xác nhận thoát không lưu ("c")
                    User-->>CLI: Nhập "c"
                    CLI-->>User: Đã thoát chương trình (không lưu thay đổi).
                    CLI->>CLI: Dừng chương trình (Exit without save)
                else Hủy bỏ ("k")
                    User-->>CLI: Nhập "k"
                    CLI-->>User: Đã hủy thao tác. Quay lại menu chính.
                end
            end
        end
    end
```

