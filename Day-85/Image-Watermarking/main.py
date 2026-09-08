from tkinter import *
from tkinter import filedialog, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont

original_image = None       # untouched uploaded image (for Reset)
current_image = None        # image with watermark(s) applied so far
click_position = (0, 0)
text_color = "black"        # default watermark color

def upload_image():
    global original_image, current_image
    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    original_image = Image.open(file_path)
    current_image = original_image.copy()
    refresh_display()

def refresh_display():
    tk_image = ImageTk.PhotoImage(current_image)
    image_label.config(image=tk_image)
    image_label.image = tk_image
    window.update_idletasks()
    window.geometry("")

def place_text_box_at(x, y):
    global click_position
    click_position = (x, y)
    watermark_entry.place(in_=image_label, x=x, y=y, anchor="w")
    update_entry_style()
    watermark_entry.focus()

def add_text_button_clicked():
    if current_image is None:
        return
    center_x = current_image.width // 2
    center_y = current_image.height // 2
    place_text_box_at(center_x, center_y)

def update_entry_style():
    try:
        font_size = int(font_size_entry.get())
    except ValueError:
        font_size = 24
    watermark_entry.config(fg=text_color, font=("Arial", font_size))

def start_drag(event):
    watermark_entry._drag_start_x = event.x
    watermark_entry._drag_start_y = event.y

def drag_text(event):
    global click_position
    x = watermark_entry.winfo_x() + (event.x - watermark_entry._drag_start_x)
    y = watermark_entry.winfo_y() + (event.y - watermark_entry._drag_start_y)
    watermark_entry.place(in_=image_label, x=x, y=y, anchor="w")
    click_position = (x, y)

def confirm_watermark(event):
    global current_image
    text = watermark_entry.get()
    if not text:
        return

    draw = ImageDraw.Draw(current_image)

    try:
        font_size = int(font_size_entry.get())
    except ValueError:
        font_size = 24

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    draw.text(click_position, text, fill=text_color, font=font)

    refresh_display()
    watermark_entry.delete(0, END)
    watermark_entry.place_forget()

def choose_color():
    global text_color
    color = colorchooser.askcolor(title="Choose watermark color")
    if color[1]:
        text_color = color[1]
        update_entry_style()

def font_size_changed(event):
    update_entry_style()

def save_image():
    if current_image is None:
        return
    save_path = filedialog.asksaveasfilename(defaultextension=".png")
    if save_path:
        current_image.save(save_path)

def reset_image():
    global current_image
    if original_image is not None:
        current_image = original_image.copy()
        refresh_display()
    watermark_entry.place_forget()  # also hide the entry box if reset is clicked mid-edit

window = Tk()
window.title("Watermark App")
window.minsize(width=300, height=150)

image_button = Button(text="Add Files", command=upload_image)
image_button.grid(column=0, row=0, padx=8, pady=10)

add_text_button = Button(text="Add Text", command=add_text_button_clicked)
add_text_button.grid(column=1, row=0, padx=8, pady=10)

color_button = Button(text="Choose Color", command=choose_color)
color_button.grid(column=2, row=0, padx=8, pady=10)

font_size_entry = Entry(window, width=5)
font_size_entry.insert(0, "24")
font_size_entry.grid(column=3, row=0, padx=8, pady=10)
font_size_entry.bind("<KeyRelease>", font_size_changed)

save_button = Button(text="Save", command=save_image)
save_button.grid(column=4, row=0, padx=8, pady=10)

reset_button = Button(text="Reset", command=reset_image)
reset_button.grid(column=5, row=0, padx=8, pady=10)

image_label = Label(window)
image_label.grid(column=0, row=1, columnspan=6, padx=20, pady=20)
# clicking directly on the image no longer does anything —
# the entry box only appears via the "Add Text" button

watermark_entry = Entry(window, borderwidth=1, bg="white")
watermark_entry.bind("<Return>", confirm_watermark)
watermark_entry.bind("<Button-1>", start_drag)
watermark_entry.bind("<B1-Motion>", drag_text)

window.mainloop()