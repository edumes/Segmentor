import tkinter as tk
from tkinter import filedialog
from moviepy.editor import VideoFileClip
import cv2
from PIL import Image, ImageTk
from video_utils import extract_segments

class VideoSegmenterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Segmenter")
        
        # Configure dark theme colors
        self.root.configure(bg='#2b2b2b')
        self.style = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'activebackground': '#3b3b3b',
            'activeforeground': '#ffffff',
            'highlightbackground': '#2b2b2b',
            'highlightcolor': '#4b4b4b'
        }

        self.root.state('zoomed')
        
        self.file_path = None
        self.clip = None
        self.selected_times_default = []
        self.selected_times_vertical = []
        self.preview_images = []

        self.upload_btn = tk.Button(root, text="Upload Video", command=self.upload_video, **self.style)
        self.upload_btn.pack()

        self.preview_label = tk.Label(root, text="Preview Frames", **self.style)
        self.preview_label.pack()

        self.frame_canvas = tk.Canvas(root, bg=self.style['bg'])
        self.frame_canvas.pack(fill=tk.BOTH, expand=True)

        self.frame_grid = tk.Frame(self.frame_canvas, bg=self.style['bg'])
        self.frame_canvas.create_window((0, 0), window=self.frame_grid, anchor="nw")

        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.frame_canvas.yview, bg=self.style['bg'])
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.frame_canvas.config(yscrollcommand=self.scrollbar.set)

        self.frame_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.extract_btn = tk.Button(root, text="Extract Segments", command=self.call_extract_segments, state=tk.DISABLED, **self.style)
        self.extract_btn.pack()

    def upload_video(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")])
        if self.file_path:
            self.clip = VideoFileClip(self.file_path)
            self.display_preview_frames()
            self.extract_btn.config(state=tk.NORMAL)

    def display_preview_frames(self):
        self.selected_times_default.clear()
        self.selected_times_vertical.clear()
        for widget in self.frame_grid.winfo_children():
            widget.destroy()
        self.preview_images.clear()

        video_cap = cv2.VideoCapture(self.file_path)
        fps = video_cap.get(cv2.CAP_PROP_FPS)
        frames_to_capture = range(0, int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT)), int(fps * 60))

        columns = 4

        for i, frame_number in enumerate(frames_to_capture):
            video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            success, frame = video_cap.read()
            if not success:
                break

            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img = img.resize((350, 250))
            img_tk = ImageTk.PhotoImage(img)
            self.preview_images.append(img_tk)

            preview_frame = tk.Frame(self.frame_grid)
            preview_frame.grid(row=i // columns, column=i % columns, padx=5, pady=5)

            img_label = tk.Label(preview_frame, image=img_tk)
            img_label.pack()

            checkbox_frame = tk.Frame(preview_frame)
            checkbox_frame.pack()

            default_var = tk.BooleanVar()
            default_cb = tk.Checkbutton(checkbox_frame, text="Default", variable=default_var,
                                      command=lambda t=i: self.toggle_time_selection(t, "default"))
            default_cb.pack(side=tk.LEFT, padx=2)

            vertical_var = tk.BooleanVar()
            vertical_cb = tk.Checkbutton(checkbox_frame, text="Vertical", variable=vertical_var,
                                       command=lambda t=i: self.toggle_time_selection(t, "vertical"))
            vertical_cb.pack(side=tk.LEFT, padx=2)

        video_cap.release()

        self.frame_grid.update_idletasks()
        self.frame_canvas.config(scrollregion=self.frame_canvas.bbox("all"))

    def toggle_time_selection(self, minute, format_type):
        if format_type == "default":
            if minute in self.selected_times_default:
                self.selected_times_default.remove(minute)
            else:
                self.selected_times_default.append(minute)
        else:
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