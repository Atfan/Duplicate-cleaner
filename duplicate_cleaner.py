import os
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

def find_duplicates(folder_path):
    filenames = defaultdict(list)
    for root, _, files in os.walk(folder_path):
        for file in files:
            filenames[file].append(os.path.join(root, file))
    duplicates = {name: paths for name, paths in filenames.items() if len(paths) > 1}
    return list(duplicates.items())

class DuplicateManagerGUI:
    def __init__(self, root, duplicates):
        self.root = root
        self.root.title("Менеджер дублікатів")
        self.duplicates = duplicates
        self.index = 0
        self.selected = set()
        self.image_refs = []
        self.root.minsize(800, 200)

        self.setup_ui()
        self.display_current_group()

    def setup_ui(self):
        # Заголовок
        self.title_label = tk.Label(self.root, text="", font=("Arial", 16))
        self.title_label.pack(pady=10)

        # Горизонтальний скролінг
        self.canvas = tk.Canvas(self.root, height=350)
        self.scroll_frame = tk.Frame(self.canvas)
        self.scrollbar = tk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.pack(fill="both", expand=True)
        self.scrollbar.pack(fill="x")

        # Лічильник вибраних
        self.counter_label = tk.Label(self.root, text="Вибрано: 0")
        self.counter_label.pack(pady=(5, 0))

        # Кнопки
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.delete_button = tk.Button(btn_frame, text="🗑 Видалити вибрані", command=self.delete_selected, state="disabled")
        self.delete_button.pack(side="left", padx=10)

        self.skip_button = tk.Button(btn_frame, text="⏭ Далі", command=self.next_group)
        self.skip_button.pack(side="left", padx=10)

    def display_current_group(self):
        # Очистка
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.image_refs.clear()
        self.selected.clear()

        if self.index >= len(self.duplicates):
            self.title_label.config(text="✅ Усі дублікати опрацьовані.")
            self.counter_label.config(text="")
            self.delete_button.config(state="disabled")
            self.skip_button.config(state="disabled")
            return

        filename, paths = self.duplicates[self.index]
        self.paths = []
        self.title_label.config(text=f"Дублікати: {filename}")

        for i, path in enumerate(paths):
            try:
                img = Image.open(path)
                img.thumbnail((250, 250))
                photo = ImageTk.PhotoImage(img)
                self.image_refs.append(photo)

                frame = tk.Frame(self.scroll_frame, padx=10, pady=10)
                img_label = tk.Label(frame, image=photo, borderwidth=2, relief="solid")
                img_label.pack()
                img_label.bind("<Button-1>", lambda e, idx=len(self.paths): self.toggle_selection(idx))

                path_label = tk.Label(frame, text=path, wraplength=250, justify="left", font=("Arial", 8))
                path_label.pack(pady=5)

                frame.pack(side="left", padx=5)

                # Додаємо лише після успішного завантаження
                self.paths.append(path)

            except Exception as e:
                print(f"⚠️ Неможливо завантажити {path}: {e}")

        if not self.paths:
            self.title_label.config(text=f"⚠️ Усі файли \"{filename}\" не вдалося завантажити як зображення.")
            self.skip_button.config(state="normal")
            self.delete_button.config(state="disabled")
        else:
            self.update_counter()


    def toggle_selection(self, index):
        if index in self.selected:
            self.selected.remove(index)
        else:
            self.selected.add(index)
        self.update_counter()

    def update_counter(self):
        count = len(self.selected)
        self.counter_label.config(text=f"Вибрано: {count}")
        self.delete_button.config(state="normal" if count else "disabled")

        for i, widget in enumerate(self.scroll_frame.winfo_children()):
            children = widget.winfo_children()
            if not children:
                continue
            label = children[0]
            if i in self.selected:
                label.config(borderwidth=4, relief="ridge", bg="lightblue")
            else:
                label.config(borderwidth=2, relief="solid", bg="SystemButtonFace")

    def delete_selected(self):
        to_delete = [self.paths[i] for i in self.selected]
        for path in to_delete:
            try:
                os.remove(path)
                print(f"🗑 Видалено: {path}")
            except Exception as e:
                print(f"⚠️ Не вдалося видалити {path}: {e}")
        self.index += 1
        self.display_current_group()

    def next_group(self):
        self.index += 1
        self.display_current_group()

def main():
    # Вибір папки
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Виберіть папку для перевірки")

    if not folder:
        print("❌ Папку не вибрано.")
        return

    duplicates = find_duplicates(folder)
    if not duplicates:
        messagebox.showinfo("Результат", "✅ Дублікатів не знайдено.")
        return

    print(f"🔁 Знайдено {len(duplicates)} груп дублікатів.")
    
    root.deiconify()  
    app = DuplicateManagerGUI(root, duplicates)
    root.mainloop()

if __name__ == "__main__":
    main()
