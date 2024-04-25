from PIL import ImageGrab, Image
import tkinter as tk
from tkinter import filedialog, simpledialog, scrolledtext, messagebox
import os
import keyboard
import pytesseract
from io import BytesIO
from easyocr import Reader

# ường dẫn đến thư viện chứa nn
tessdata_path = r'C:\Program Files\Tesseract-OCR\tessdata'

# đường dẫn đến file nn
language_file_path = os.path.join(tessdata_path, 'vie.traineddata')

# thiết lập đường dẫn
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.languages_dir = tessdata_path
pytesseract.pytesseract.langs = ['vi']

class ScreenshotApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cắt ảnh")
        self.root.geometry("1920x1080")
        self.root.attributes("-alpha", 0.4)
        self.canvas = tk.Canvas(self.root, bg="white", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.dialog_hidden = False
        self.previous_rect = None

        self.canvas.bind("<ButtonPress-1>", self.on_click_press)
        self.canvas.bind("<B1-Motion>", self.on_click_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_click_release)

        keyboard.add_hotkey('shift+`', self.on_shift_backtick)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.run_main_loop()

    def run_main_loop(self):
        self.root.mainloop()

    def on_click_press(self, event):
        if self.dialog_hidden:
            return

        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        if self.previous_rect:
            self.canvas.delete(self.previous_rect)

        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)

    def on_click_drag(self, event):
        if self.dialog_hidden:
            return

        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def clear_canvas(self):
        if self.rect:
            self.canvas.delete(self.rect)
            self.previous_rect = None

    def on_click_release(self, event):
        if self.dialog_hidden:
            return

        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)

        self.canvas.coords(self.rect, self.start_x, self.start_y, end_x, end_y)

        x, y, width, height = self.canvas.coords(self.rect)
        x, y = self.root.winfo_rootx() + x, self.root.winfo_rooty() + y

        self.root.withdraw()

        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))

        self.save_cropped_image(screenshot)

        if self.dialog_hidden:
            self.root.deiconify()

        self.clear_canvas()

    def save_cropped_image(self, image):
        # chuyển hinhft  thành mảng bytes
        img_bytes_io = BytesIO()
        image.save(img_bytes_io, format="PNG")
        img_bytes = img_bytes_io.getvalue()

        # đọc chữ từ hình ảnh
        text = self.read_text_from_image(img_bytes)
        self.show_text_dialog(text)

    def read_text_from_image(self, img_bytes):
        try:
            reader = Reader(['vi'])
            result = reader.readtext(img_bytes)
            text = ' '.join([box[1] for box in result])
            return text
        except Exception as e:
            print(f"Lỗi khi đọc văn bản từ hình ảnh: {e}")
            return ""

    def delete_image(self, filename):
        try:
            os.remove(filename)
            print(f"Đã xóa hình ảnh {filename} sau khi đọc xong văn bản.")
        except Exception as e:
            print(f"Lỗi khi xóa hình ảnh {filename}: {e}")

    def show_text_dialog(self, text):
        top = tk.Toplevel(self.root)
        top.title("Text from Image")
        top.geometry("400x300")

        # hôộp thoại hển thi vb có thể chỉnh sửa đc
        text_widget = scrolledtext.ScrolledText(top, wrap=tk.WORD, width=40, height=10)
        text_widget.pack(expand=True, fill=tk.BOTH)
        text_widget.insert(tk.END, text)

        def on_copy():
            # tự động sao chép văn bản vào clipboard khi nhấp nút Copy
            top.clipboard_clear()
            top.clipboard_append(text_widget.get("1.0", tk.END))
            top.update()

        copy_button = tk.Button(top, text="Copy", command=on_copy)
        copy_button.pack(pady=10)

    def on_close(self):
        keyboard.unhook_all()
        self.root.destroy()

    def on_shift_backtick(self):
        if self.root.state() == "withdrawn":
            self.root.deiconify()
            self.dialog_hidden = False

            print("Hộp thoại đã được hiển thị.")
        else:
            self.dialog_hidden = True
            print("Hộp thoại đã được ẩn.")

if __name__ == "__main__":
    app = ScreenshotApp()
