import os
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def find_duplicates(folder_path):
    filenames = defaultdict(list)
    for root, _, files in os.walk(folder_path):
        for file in files:
            filenames[file].append(os.path.join(root, file))
    duplicates = {name: paths for name, paths in filenames.items() if len(paths) > 1}
    return duplicates

def show_image(image_path):
    try:
        image_window = tk.Toplevel()
        image_window.title(f"Перегляд: {os.path.basename(image_path)}")

        img = Image.open(image_path)
        img.thumbnail((600, 600))  # змінити розмір для вікна
        photo = ImageTk.PhotoImage(img)

        label = tk.Label(image_window, image=photo)
        label.image = photo  # зберігаємо посилання
        label.pack()
        image_window.mainloop()
    except Exception as e:
        print(f"⚠️ Неможливо показати зображення: {e}")

def show_all_images(image_paths, title="Перегляд дублікатів"):
    try:
        preview_window = tk.Toplevel()
        preview_window.title(title)

        # Розрахунок висоти вікна (наприклад, 320 пікселів на 1 фото + запас)
        img_height = 320
        total_height = len(image_paths) * img_height
        max_height = preview_window.winfo_screenheight() - 100  # запас

        final_height = min(total_height, max_height)
        preview_window.geometry(f"350x{final_height}")  # ширина x висота

        container = tk.Frame(preview_window)
        container.pack(fill="both", expand=True)

        images = []

        for path in image_paths:
            try:
                img = Image.open(path)
                img.thumbnail((300, 300))
                photo = ImageTk.PhotoImage(img)
                images.append(photo)

                frame = tk.Frame(container, padx=10, pady=10)
                label = tk.Label(frame, image=photo)
                label.pack()
                text = tk.Label(frame, text=path, wraplength=280, justify="left")
                text.pack()
                frame.pack()
            except Exception as e:
                print(f"⚠️ Неможливо відкрити {path}: {e}")

        preview_window.images = images
    except Exception as e:
        print(f"⚠️ Помилка при відкритті зображень: {e}")
 

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
        print("✅ Дублікатів не знайдено.")
        return

    total_duplicates = sum(len(paths) for paths in duplicates.values())
    print(f"\n🔁 Знайдено {len(duplicates)} назв з дублями, всього дублікатів: {total_duplicates - len(duplicates)}")

    for filename, paths in duplicates.items():
        print(f"\n📁 {filename}:")
        for i, path in enumerate(paths, 1):
            print(f"  {i}. {path}")

       # показ фото одразу
        image_paths = [p for p in paths if p.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif"))]
        if image_paths:
            show_all_images(image_paths, title=f"Зображення: {filename}")

        try:
            choice = int(input(f"Який з файлів \"{filename}\" видалити? Введіть номер (або 0 щоб пропустити): "))
            if 1 <= choice <= len(paths):
                os.remove(paths[choice - 1])
                print("🗑️ Видалено:", paths[choice - 1])
            else:
                print("⏩ Пропущено.")
        except Exception as e:
            print("⚠️ Помилка:", e)

    print("\n✅ Додаток завершив роботу! \n\n")

if __name__ == "__main__":
    main()
