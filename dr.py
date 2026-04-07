import cv2
import os
import numpy as np
from tkinter import Tk, Button, Label, filedialog, messagebox
from PIL import Image, ImageTk

# ---------------------------
# Folder configuration
# ---------------------------
INPUT_FOLDER = "images"
OUTPUT_FOLDER = "output"

os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

image = None
cartoon = None
current_path = None

# ---------------------------
# Cartoonify function (Smooth cartoon, natural colors)
# ---------------------------
def cartoonify(img):
    img = cv2.resize(img, (600, 600))

    # 1- تطبيق Bilateral Filter متعدد للتنعيم مع الحفاظ على اللون
    color = img.copy()
    for _ in range(5):
        color = cv2.bilateralFilter(color, 9, 75, 75)

    # 2- اكتشاف الحواف بخفة لتجنب الخطوط القاسية
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        9, 5
    )

    # 3- تلطيف الحواف باستخدام Gaussian Blur خفيف
    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    edges = cv2.GaussianBlur(edges, (3, 3), 0)

    # 4- دمج الحواف مع الصورة الملونة
    cartoon_img = cv2.bitwise_and(color, edges)

    return cartoon_img

# ---------------------------
# GUI helper functions
# ---------------------------
def show_image(img, panel):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = img.resize((300, 300))
    img = ImageTk.PhotoImage(img)
    panel.config(image=img)
    panel.image = img

# ---------------------------
# Load image from images folder
# ---------------------------
def open_image():
    global image, current_path
    file_path = filedialog.askopenfilename(
        initialdir=INPUT_FOLDER,
        title="Select Image",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
    )
    if file_path:
        image = cv2.imread(file_path)
        current_path = file_path
        show_image(image, panel_original)

# ---------------------------
# Apply cartoon effect
# ---------------------------
def apply_cartoon():
    global cartoon
    if image is None:
        messagebox.showwarning("Warning", "Please select an image first")
        return
    cartoon = cartoonify(image)
    show_image(cartoon, panel_cartoon)

# ---------------------------
# Save processed image
# ---------------------------
def save_image():
    if cartoon is None:
        messagebox.showwarning("Warning", "No processed image to save")
        return
    filename = os.path.basename(current_path)
    save_path = os.path.join(OUTPUT_FOLDER, f"cartoon_{filename}")
    cv2.imwrite(save_path, cartoon)
    messagebox.showinfo("Saved", f"Image saved to:\n{save_path}")

# ---------------------------
# Process all images in folder
# ---------------------------
def batch_process():
    files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    if not files:
        messagebox.showwarning("Warning", "No images found in images folder")
        return
    for file in files:
        path = os.path.join(INPUT_FOLDER, file)
        img = cv2.imread(path)
        result = cartoonify(img)
        save_path = os.path.join(OUTPUT_FOLDER, f"cartoon_{file}")
        cv2.imwrite(save_path, result)
    messagebox.showinfo("Done", "All images processed and saved to output folder")

# ---------------------------
# GUI Layout
# ---------------------------
root = Tk()
root.title("Cartoon Image Studio")
root.geometry("700x500")

btn_open = Button(root, text="Open Image", command=open_image, width=20)
btn_open.pack(pady=5)

btn_cartoon = Button(root, text="Convert to Cartoon", command=apply_cartoon, width=20)
btn_cartoon.pack(pady=5)

btn_save = Button(root, text="Save Cartoon Image", command=save_image, width=20)
btn_save.pack(pady=5)

btn_batch = Button(root, text="Batch Process Folder", command=batch_process, width=20)
btn_batch.pack(pady=5)

panel_original = Label(root)
panel_original.pack(side="left", padx=10, pady=10)

panel_cartoon = Label(root)
panel_cartoon.pack(side="right", padx=10, pady=10)

root.mainloop()
