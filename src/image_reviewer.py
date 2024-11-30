import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ImageReviewer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]
        self.current_index = 0

        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title("Revisor de Imágenes")

        # Crear marco para mostrar el nombre del archivo
        self.filename_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.filename_label.pack(pady=5)

        # Crear marco para la imagen
        self.image_label = tk.Label(self.root)
        self.image_label.pack()

        # Botones
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.next_button = ttk.Button(btn_frame, text="Siguiente", command=self.next_image)
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(btn_frame, text="Eliminar", command=self.delete_image)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        # Mostrar primera imagen
        self.show_image()

        self.root.mainloop()

    def show_image(self):
        if not self.image_files:
            self.filename_label.config(text="No hay más imágenes en la carpeta.")
            self.image_label.config(image="", text="No hay más imágenes.")
            self.next_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            return

        # Actualizar la imagen
        current_image_path = os.path.join(self.folder_path, self.image_files[self.current_index])
        img = Image.open(current_image_path)
        img.thumbnail((800, 600))
        self.tk_image = ImageTk.PhotoImage(img)

        self.image_label.config(image=self.tk_image)
        self.image_label.image = self.tk_image

        # Actualizar el nombre del archivo
        current_filename = self.image_files[self.current_index]
        self.filename_label.config(text=f"Mostrando: {current_filename}")

    def next_image(self):
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.show_image()
        else:
            self.filename_label.config(text="Has llegado al final de las imágenes.")

    def delete_image(self):
        if self.image_files:
            current_image_path = os.path.join(self.folder_path, self.image_files[self.current_index])
            os.remove(current_image_path)
            del self.image_files[self.current_index]

            if self.current_index >= len(self.image_files):
                self.current_index -= 1

            self.show_image()

# Cambia "ruta_de_tu_carpeta" por la ruta de tu carpeta con imágenes
folder_path = "../data/raw/hardhat"
app = ImageReviewer(folder_path)
