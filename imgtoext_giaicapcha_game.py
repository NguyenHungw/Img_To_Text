import tkinter as tk
import pyautogui
import cv2
from PIL import Image, ImageTk
import pytesseract
import numpy as np
import re


def recognize_image():
    global capture_in_progress

    if not capture_in_progress:
        # Chụp ảnh màn hình
        screenshot = pyautogui.screenshot()

        # Lấy các thông số từ hộp thoại
        x = int(entry_x.get())
        y = int(entry_y.get())
        w = int(entry_w.get())
        h = int(entry_h.get())

        # Kiểm tra và cắt ảnh theo khu vực chỉ định
        if x >= 0 and y >= 0 and w > 0 and h > 0:
            cropped_image = screenshot.crop((x, y, x + w, y + h))

            # Thực hiện nhận dạng chữ và số từ ảnh cắt
            result = recognize_text(cropped_image)

            # Hiển thị kết quả
            if result is not None:
                total_value = calculate_result(result)
                result_label.configure(text="" + str(total_value))
                copy_button.configure(state=tk.NORMAL)
            else:
                result_label.configure(text="Không nhận dạng được số!")

            # Reset kết quả về 0
            total.set(0)

            # Hiển thị ảnh cắt lên giao diện
            display_image(cropped_image)

            # Cập nhật trạng thái chụp ảnh
            capture_in_progress = True
    else:
        # Reset trạng thái chụp ảnh
        capture_in_progress = False
        total.set(0)  # Reset kết quả về 0


def recognize_text(image):
    # Chuyển đổi ảnh từ PIL Image sang OpenCV array
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Áp dụng các bộ lọc khác nhau để cải thiện chất lượng hình ảnh
    image_filtered = cv2.medianBlur(image_cv, 3)  # Bộ lọc trung vị
    # image_filtered = cv2.GaussianBlur(image_cv, (5, 5), 0)  # Bộ lọc Gaussian

    # Chuyển đổi lại thành ảnh PIL Image
    image_pil = Image.fromarray(cv2.cvtColor(image_filtered, cv2.COLOR_BGR2RGB))

    try:
        # Sử dụng pytesseract để nhận dạng chữ và số từ hình ảnh
        result = pytesseract.image_to_string(image_pil, lang="eng", config='--psm 11')

        return result
    except (ValueError, IndexError):
        # Xử lý khi không thể nhận dạng
        return None


def calculate_result(result):
    # Xóa khoảng trắng trong kết quả nhận dạng
    result = result.replace(" ", "")

    # Lọc các ký tự không hợp lệ
    result = re.sub(r'[^0-9+\-*/]', '', result)

    # Tách và cộng các số
    numbers = result.split('+')
    if len(numbers) == 2:
        number1 = int(numbers[0].strip())
        number2 = int(numbers[1].strip())
        total_value = total.get() + number1 + number2
        total.set(total_value)
        return total_value
    else:
        return None


def copy_result():
    # Sao chép kết quả vào clipboard
    result = result_label.cget("text")
    window.clipboard_clear()
    window.clipboard_append(result)


def display_image(image):
    # Chuyển đổi ảnh PIL thành đối tượng ImageTk
    photo = ImageTk.PhotoImage(image)

    # Hiển thị ảnh trên giao diện
    image_label.configure(image=photo)
    image_label.image = photo


# Tạo cửa sổ giao diện
window = tk.Tk()
window.title("Giải Captcha")

# Tạo các điều khiển nhập liệu
entry_x = tk.Entry(window)
entry_x.pack()
entry_y = tk.Entry(window)
entry_y.pack()
entry_w = tk.Entry(window)
entry_w.pack()
entry_h = tk.Entry(window)
entry_h.pack()

# Biến lưu trữ tổng kết quả
total = tk.IntVar()
total.set(0)

# Biến lưu trữ trạng thái chụp ảnh
capture_in_progress = False

# Tạo nút chụp và kết quả
capture_button = tk.Button(window, text="Chụp", command=recognize_image)
capture_button.pack()

result_label = tk.Label(window, text="Kết quả: ")
result_label.pack()

# Hiển thị tổng kết quả
total_label = tk.Label(window, textvariable=total)
total_label.pack()

# Tạo nút sao chép
copy_button = tk.Button(window, text="Copy", state=tk.DISABLED, command=copy_result)
copy_button.pack()

# Hiển thị ảnh
image_label = tk.Label(window)
image_label.pack()
id_discord = tk.Label(window,text="Hwajin#2873")
id_discord.pack()
# Cấu hình pytesseract để sử dụng Tesseract OCR engine
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Chạy giao diệnco
window.mainloop()
