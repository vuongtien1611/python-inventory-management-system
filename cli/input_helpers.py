"""Các hàm hỗ trợ nhập liệu, kiểm tra đầu vào và thông báo trên Console.

Người phụ trách: Thành viên 1 - Tiến (nhánh `feature/main-menu`).
"""


class UserExitSignal(Exception):
    """Ngoại lệ nội bộ báo hiệu kết thúc luồng nhập (EOF hoặc Ctrl+C)."""


def read_input_safe(prompt: str) -> str:
    """Đọc chuỗi đầu vào từ bàn phím và xử lý an toàn EOF / Ctrl+C.

    Args:
        prompt: Chuỗi nhắc hiển thị cho người dùng.

    Returns:
        Chuỗi người dùng đã nhập (đã loại bỏ khoảng trắng đầu/cuối).

    Raises:
        UserExitSignal: Khi gặp EOF (Ctrl+D / hết luồng nhập) hoặc Ctrl+C.
    """
    try:
        return input(prompt).strip()
    except EOFError as exc:
        print("\nĐã kết thúc luồng đầu vào (EOF). Đang thoát chương trình...")
        raise UserExitSignal from exc
    except KeyboardInterrupt as exc:
        print("\nĐã nhận tín hiệu ngắt (Ctrl+C). Đang thoát chương trình...")
        raise UserExitSignal from exc


def read_menu_choice(min_choice: int, max_choice: int, prompt: str = "Nhập lựa chọn của bạn: ") -> int:
    """Đọc và kiểm tra lựa chọn số nguyên nằm trong khoảng hợp lệ.

    Args:
        min_choice: Giá trị nhỏ nhất hợp lệ.
        max_choice: Giá trị lớn nhất hợp lệ.
        prompt: Chuỗi nhắc nhập liệu.

    Returns:
        Số nguyên hợp lệ người dùng đã chọn.

    Raises:
        UserExitSignal: Khi gặp EOF hoặc Ctrl+C.
    """
    while True:
        raw_value = read_input_safe(prompt)
        if not raw_value:
            print("Lỗi: Không được để trống lựa chọn. Vui lòng thử lại.")
            continue

        try:
            choice = int(raw_value)
        except ValueError:
            print("Lỗi: Vui lòng nhập một số nguyên hợp lệ, không nhập chữ.")
            continue

        if choice < min_choice or choice > max_choice:
            print(f"Lỗi: Lựa chọn ngoài phạm vi ({min_choice} - {max_choice}). Vui lòng nhập lại.")
            continue

        return choice


def confirm_action(prompt: str) -> bool:
    """Hỏi xác nhận Có/Không từ người dùng.

    Hỗ trợ các câu trả lời: `c`, `có`, `y`, `yes` (Có) hoặc `k`, `không`, `n`, `no` (Không).

    Args:
        prompt: Nội dung câu hỏi xác nhận.

    Returns:
        True nếu người dùng đồng ý, False nếu từ chối.

    Raises:
        UserExitSignal: Khi gặp EOF hoặc Ctrl+C.
    """
    yes_values = {"c", "co", "có", "y", "yes"}
    no_values = {"k", "khong", "không", "n", "no"}

    while True:
        answer = read_input_safe(prompt).lower()
        if answer in yes_values:
            return True
        if answer in no_values:
            return False
        print("Lỗi: Vui lòng nhập 'c' (Có) hoặc 'k' (Không).")


def read_sort_order() -> str | None:
    """Cho phép người dùng chọn thứ tự sắp xếp tăng dần hoặc giảm dần.

    Returns:
        `"asc"` nếu tăng dần, `"desc"` nếu giảm dần, hoặc `None` nếu chọn quay lại.

    Raises:
        UserExitSignal: Khi gặp EOF hoặc Ctrl+C.
    """
    print("\n--- Chọn thứ tự sắp xếp ---")
    print("  1. Tăng dần")
    print("  2. Giảm dần")
    print("  0. Quay lại")
    choice = read_menu_choice(0, 2, "Chọn thứ tự (0-2): ")
    if choice == 1:
        return "asc"
    if choice == 2:
        return "desc"
    return None


def notify_not_implemented(feature_name: str) -> None:
    """Hiển thị thông báo chuẩn khi chức năng chưa có service thực tế.

    Args:
        feature_name: Tên chức năng người dùng vừa chọn.
    """
    print(f"\n-> Đã chọn chức năng: {feature_name}")
    print("[CHƯA TRIỂN KHAI] Chức năng đang được thành viên phụ trách phát triển.")

