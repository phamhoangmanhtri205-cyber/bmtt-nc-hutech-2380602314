import tkinter as tk
from tkinter import messagebox

# --- THUẬT TOÁN MÃ HÓA RAIL FENCE CHUẨN ---
def encrypt_rail_fence(text, rails):
    if rails == 1:
        return text
    
    matrix = [['\n' for _ in range(len(text))] for _ in range(rails)]
    dir_down = False
    row, col = 0, 0
    
    for i in range(len(text)):
        if (row == 0) or (row == rails - 1):
            dir_down = not dir_down
        matrix[row][col] = text[i]
        col += 1
        row += 1 if dir_down else -1
        
    result = []
    for i in range(rails):
        for j in range(len(text)):
            if matrix[i][j] != '\n':
                result.append(matrix[i][j])
    return "".join(result)

# --- THUẬT TOÁN GIẢI MÃ RAIL FENCE CHUẨN ---
def decrypt_rail_fence(cipher, rails):
    if rails == 1:
        return cipher
        
    matrix = [['\n' for _ in range(len(cipher))] for _ in range(rails)]
    dir_down = None
    row, col = 0, 0
    
    for i in range(len(cipher)):
        if row == 0:
            dir_down = True
        if row == rails - 1:
            dir_down = False
        matrix[row][col] = '*'
        col += 1
        row += 1 if dir_down else -1
        
    index = 0
    for i in range(rails):
        for j in range(len(cipher)):
            if (matrix[i][j] == '*') and (index < len(cipher)):
                matrix[i][j] = cipher[index]
                index += 1
                
    result = []
    row, col = 0, 0
    for i in range(len(cipher)):
        if row == 0:
            dir_down = True
        if row == rails - 1:
            dir_down = False
        if matrix[row][col] != '\n':
            result.append(matrix[row][col])
            col += 1
        row += 1 if dir_down else -1
    return "".join(result)

# --- XỬ LÝ SỰ KIỆN TRÊN GIAO DIỆN ---
def handle_encrypt():
    text = entry_input.get()
    try:
        key = int(entry_key.get())
        if key <= 0: raise ValueError
    except ValueError:
        messagebox.showerror("Lỗi", "Số hàng (Key) phải là số nguyên dương!")
        return
    
    if not text:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập văn bản cần mã hóa!")
        return
        
    res = encrypt_rail_fence(text, key)
    entry_output.delete(0, tk.END)
    entry_output.insert(0, res)

def handle_decrypt():
    cipher = entry_input.get()
    try:
        key = int(entry_key.get())
        if key <= 0: raise ValueError
    except ValueError:
        messagebox.showerror("Lỗi", "Số hàng (Key) phải là số nguyên dương!")
        return
        
    if not cipher:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập văn bản cần giải mã!")
        return
        
    res = decrypt_rail_fence(cipher, key)
    entry_output.delete(0, tk.END)
    entry_output.insert(0, res)

# --- KHỞI TẠO CỬA SỔ UI ---
root = tk.Tk()
root.title("Rail Fence Cipher - UI")
root.geometry("500x320")
root.resizable(False, False)

# Tiêu đề chính
label_title = tk.Label(root, text="MÃ HÓA & GIẢI MÃ RAIL FENCE", font=("Arial", 14, "bold"), fg="#1e3d59")
label_title.pack(pady=15)

# Khung nhập liệu
frame = tk.Frame(root)
frame.pack(padx=20, pady=5, fill="x")

tk.Label(frame, text="Nhập chuỗi:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
entry_input = tk.Entry(frame, font=("Arial", 10), width=45)
entry_input.grid(row=0, column=1, pady=5, padx=10)

tk.Label(frame, text="Số hàng (Key):", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
entry_key = tk.Entry(frame, font=("Arial", 10), width=10)
entry_key.insert(0, "3") # Mặc định key = 3
entry_key.grid(row=1, column=1, sticky="w", pady=5, padx=10)

tk.Label(frame, text="Kết quả:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=15)
entry_output = tk.Entry(frame, font=("Arial", 10, "bold"), width=45, fg="green")
entry_output.grid(row=2, column=1, pady=15, padx=10)

# Khung chứa nút bấm
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

btn_encrypt = tk.Button(btn_frame, text="Mã hóa", font=("Arial", 10, "bold"), bg="#17b978", fg="white", width=12, command=handle_encrypt)
btn_encrypt.grid(row=0, column=0, padx=15)

btn_decrypt = tk.Button(btn_frame, text="Giải mã", font=("Arial", 10, "bold"), bg="#a6dcef", fg="black", width=12, command=handle_decrypt)
btn_decrypt.grid(row=0, column=1, padx=15)

# Gọi hàm chạy trực tiếp, ép Python bắt buộc phải mở giao diện
root.mainloop()