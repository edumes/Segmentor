# main_app.py

import tkinter as tk
from tkinter import filedialog
from moviepy.editor import VideoFileClip
import cv2
from PIL import Image, ImageTk
from video_utils import extract_segments  # Importa a função do outro módulo

class VideoSegmenterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Segmenter")
        self.root.geometry("800x600")
        
        self.file_path = None
        self.clip = None
        self.selected_times_default = []  # Times selected for default format
        self.selected_times_vertical = []  # Times selected for vertical format
        self.preview_images = []

        # Botão para upload de vídeo
        self.upload_btn = tk.Button(root, text="Upload Video", command=self.upload_video)
        self.upload_btn.pack()

        # Seção de pré-visualização de quadros
        self.preview_label = tk.Label(root, text="Preview Frames")
        self.preview_label.pack()

        # Canvas para quadros de visualização com scrollbar
        self.frame_canvas = tk.Canvas(root)
        self.frame_canvas.pack(fill=tk.BOTH, expand=True)

        # Frame dentro do canvas para layout de grade
        self.frame_grid = tk.Frame(self.frame_canvas)
        self.frame_canvas.create_window((0, 0), window=self.frame_grid, anchor="nw")

        # Configurar scrollbar vertical
        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.frame_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.frame_canvas.config(yscrollcommand=self.scrollbar.set)

        # Vincular funcionalidade de rolagem para o mouse
        self.frame_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Botão de extração
        self.extract_btn = tk.Button(root, text="Extract Segments", command=self.call_extract_segments, state=tk.DISABLED)
        self.extract_btn.pack()

    def upload_video(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")])
        if self.file_path:
            self.clip = VideoFileClip(self.file_path)
            self.display_preview_frames()
            self.extract_btn.config(state=tk.NORMAL)

    def display_preview_frames(self):
        # Limpar quadros anteriores e redefinir tempos selecionados
        self.selected_times_default.clear()
        self.selected_times_vertical.clear()
        for widget in self.frame_grid.winfo_children():
            widget.destroy()
        self.preview_images.clear()

        video_cap = cv2.VideoCapture(self.file_path)
        fps = video_cap.get(cv2.CAP_PROP_FPS)
        frames_to_capture = range(0, int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT)), int(fps * 60))

        # Definir colunas para o layout de grade
        columns = 4  # Ajuste para o número desejado de colunas

        for i, frame_number in enumerate(frames_to_capture):
            video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            success, frame = video_cap.read()
            if not success:
                break

            # Converter quadro para formato adequado para exibição no tkinter
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img = img.resize((350, 250))  # Tamanho maior da imagem
            img_tk = ImageTk.PhotoImage(img)
            self.preview_images.append(img_tk)  # Manter referência para evitar coleta de lixo

            # Criar um frame para cada preview com seus checkboxes
            preview_frame = tk.Frame(self.frame_grid)
            preview_frame.grid(row=i // columns, column=i % columns, padx=5, pady=5)

            # Label com a imagem
            img_label = tk.Label(preview_frame, image=img_tk)
            img_label.pack()

            # Frame para os checkboxes
            checkbox_frame = tk.Frame(preview_frame)
            checkbox_frame.pack()

            # Checkbox para formato default
            default_var = tk.BooleanVar()
            default_cb = tk.Checkbutton(checkbox_frame, text="Default", variable=default_var,
                                      command=lambda t=i: self.toggle_time_selection(t, "default"))
            default_cb.pack(side=tk.LEFT, padx=2)

            # Checkbox para formato vertical
            vertical_var = tk.BooleanVar()
            vertical_cb = tk.Checkbutton(checkbox_frame, text="Vertical", variable=vertical_var,
                                       command=lambda t=i: self.toggle_time_selection(t, "vertical"))
            vertical_cb.pack(side=tk.LEFT, padx=2)

        video_cap.release()

        # Atualizar a área de rolagem
        self.frame_grid.update_idletasks()
        self.frame_canvas.config(scrollregion=self.frame_canvas.bbox("all"))

    def toggle_time_selection(self, minute, format_type):
        if format_type == "default":
            if minute in self.selected_times_default:
                self.selected_times_default.remove(minute)
            else:
                self.selected_times_default.append(minute)
        else:  # vertical
            if minute in self.selected_times_vertical:
                self.selected_times_vertical.remove(minute)
            else:
                self.selected_times_vertical.append(minute)

    def call_extract_segments(self):
        if self.file_path and (self.selected_times_default or self.selected_times_vertical):
            extract_segments(self.file_path, self.selected_times_default, self.selected_times_vertical)

    def _on_mousewheel(self, event):
        self.frame_canvas.yview_scroll(-1 * (event.delta // 120), "units")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoSegmenterApp(root)
    root.mainloop()
