import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QScrollArea, QCheckBox, QFileDialog, QFrame, QSizePolicy
)
from PyQt6.QtGui import QGuiApplication, QPixmap, QImage, QColor, QPalette, QIcon, QFont
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
import os
import cv2
from video_utils import extract_segments

class FrameLoaderThread(QThread):
    frames_loaded = pyqtSignal(list, list)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        
    def run(self):
        video_cap = cv2.VideoCapture(self.file_path)
        if not video_cap.isOpened():
            self.frames_loaded.emit([], [])
            return
            
        fps = video_cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames_to_capture = range(0, total_frames, int(fps * 60))
        
        frames = []
        frame_times = []
        
        for frame_number in frames_to_capture:
            video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            success, frame = video_cap.read()
            if not success:
                break
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb = cv2.resize(frame_rgb, (350, 250), interpolation=cv2.INTER_CUBIC)
            frames.append(frame_rgb)
            frame_times.append(frame_number / fps)
            
        video_cap.release()
        self.frames_loaded.emit(frames, frame_times)

class ThumbnailWidget(QWidget):
    def __init__(self, image_data, minute, time_str, parent=None):
        super().__init__(parent)
        self.minute = minute
        self.parent_app = parent
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        self.setLayout(layout)

        height, width, channel = image_data.shape
        bytes_per_line = 3 * width
        qimage = QImage(image_data.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        self.pixmap = QPixmap.fromImage(qimage)
        self.pixmap.setDevicePixelRatio(self.devicePixelRatioF())

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(350, 250)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #333;
                border: 1px solid #555;
                border-radius: 5px;
            }
        """)
        self.update_image()
        layout.addWidget(self.image_label)

        time_label = QLabel(f"Time: {time_str}")
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_label.setStyleSheet("color: #aaa; font-size: 12px;")
        layout.addWidget(time_label)

        checkbox_layout = QHBoxLayout()
        checkbox_layout.setContentsMargins(0, 5, 0, 0)
        checkbox_layout.setSpacing(5)
        
        self.default_check = QCheckBox("Default")
        self.vertical_check = QCheckBox("Vertical")

        checkbox_style = """
            QCheckBox {
                color: white;
                padding: 3px;
                background-color: #3a3a3a;
                border-radius: 4px;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #0047AB;
                border: 1px solid #5d1d7d;
            }
            QCheckBox::indicator:unchecked {
                background-color: #555;
                border: 1px solid #777;
            }
        """
        self.default_check.setStyleSheet(checkbox_style)
        self.vertical_check.setStyleSheet(checkbox_style)

        self.default_check.stateChanged.connect(self.handle_checkbox_change)
        self.vertical_check.stateChanged.connect(self.handle_checkbox_change)
        
        checkbox_layout.addWidget(self.default_check)
        checkbox_layout.addWidget(self.vertical_check)
        layout.addLayout(checkbox_layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #3a3a3a;
                border-radius: 8px;
                padding: 2px;
            }
        """)
    
    def update_image(self):
        if not self.pixmap.isNull():
            scaled_pixmap = self.pixmap.scaled(
                self.image_label.width(), 
                self.image_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setScaledContents(False)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image()
    
    def handle_checkbox_change(self):
        if self.default_check.isChecked():
            if self.minute not in self.parent_app.selected_times_default:
                self.parent_app.selected_times_default.append(self.minute)
        else:
            if self.minute in self.parent_app.selected_times_default:
                self.parent_app.selected_times_default.remove(self.minute)
                
        if self.vertical_check.isChecked():
            if self.minute not in self.parent_app.selected_times_vertical:
                self.parent_app.selected_times_vertical.append(self.minute)
        else:
            if self.minute in self.parent_app.selected_times_vertical:
                self.parent_app.selected_times_vertical.remove(self.minute)

class VideoSegmenterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Segmentor")
        self.setMinimumSize(1000, 700)

        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(142, 45, 197).lighter())
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.setPalette(dark_palette)

        self.file_path = None
        self.clip = None
        self.selected_times_default = []
        self.selected_times_vertical = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        
        title_label = QLabel("Segmentor")
        title_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold;
            color: #e0e0e0;
            padding: 5px;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()

        self.upload_btn = QPushButton("Upload Video")
        self.upload_btn.setFixedSize(180, 45)
        self.upload_btn.setIcon(QIcon.fromTheme("document-open"))
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c5c5c;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #6c6c6c;
            }
            QPushButton:pressed {
                background-color: #4c4c4c;
            }
            QPushButton:disabled {
                background-color: #3c3c3c;
                color: #888;
            }
        """)
        self.upload_btn.clicked.connect(self.upload_video)
        header_layout.addWidget(self.upload_btn)

        main_layout.addLayout(header_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #555;")
        main_layout.addWidget(separator)

        preview_layout = QVBoxLayout()
        
        preview_label = QLabel("Preview Frames")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold;
            color: #d0d0d0;
            padding: 4px;
        """)
        preview_layout.addWidget(preview_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background-color: #252525; border-radius: 8px;")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: #252525;")
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        
        self.scroll_area.setWidget(self.scroll_content)
        preview_layout.addWidget(self.scroll_area, 1)
        
        main_layout.addLayout(preview_layout, 1)

        self.extract_btn = QPushButton("Extract Segments")
        self.extract_btn.setFixedHeight(50)
        self.extract_btn.setEnabled(False)
        self.extract_btn.setStyleSheet("""
            QPushButton {
                background-color: #3F00FF;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                padding: 5px;
            }
            QPushButton:disabled {
                background-color: #4a4a4a;
                color: #999;
            }
            QPushButton:hover:enabled {
                background-color: #0047AB;
            }
            QPushButton:pressed:enabled {
                background-color: #000080;
            }
        """)
        self.extract_btn.clicked.connect(self.call_extract_segments)
        main_layout.addWidget(self.extract_btn)

        self.columns = 4

        self.status_label = QLabel("Ready to upload video")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #aaa; font-size: 12px; padding: 5px;")
        main_layout.addWidget(self.status_label)

        self.progress_bar = QLabel()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet("background-color: #252525;")
        main_layout.addWidget(self.progress_bar)

        self.layout_timer = QTimer()
        self.layout_timer.timeout.connect(self.adjust_columns)
        self.layout_timer.start(500)
    
    def adjust_columns(self):
        width = self.scroll_content.width()
        new_columns = max(1, width // 400)
        
        if new_columns != self.columns:
            self.columns = new_columns
            self.update_grid_layout()
    
    def update_grid_layout(self):
        widgets = []
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widgets.append(widget)
                widget.hide()
        
        for i, widget in enumerate(reversed(widgets)):
            row = i // self.columns
            col = i % self.columns
            self.grid_layout.addWidget(widget, row, col)
            widget.show()
    
    def upload_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )
        
        if file_path:
            self.file_path = file_path
            self.upload_btn.setEnabled(False)
            self.status_label.setText("Loading video...")
            self.progress_bar.setStyleSheet("background-color: #0047AB;")

            self.loader_thread = FrameLoaderThread(file_path)
            self.loader_thread.frames_loaded.connect(self.display_preview_frames)
            self.loader_thread.start()
    
    def display_preview_frames(self, frames, frame_times):
        self.selected_times_default = []
        self.selected_times_vertical = []

        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        if not frames:
            self.status_label.setText("Failed to load video")
            self.progress_bar.setStyleSheet("background-color: #d32f2f;")
            self.upload_btn.setEnabled(True)
            return

        for idx, frame in enumerate(frames):
            minutes = int(frame_times[idx] // 60)
            seconds = int(frame_times[idx] % 60)
            time_str = f"{minutes:02d}:{seconds:02d}"

            thumbnail = ThumbnailWidget(frame, idx, time_str, self)
            row = idx // self.columns
            col = idx % self.columns
            self.grid_layout.addWidget(thumbnail, row, col)
        
        self.status_label.setText(f"Loaded {len(frames)} frames from video")
        self.progress_bar.setStyleSheet("background-color: #388e3c;")
        self.extract_btn.setEnabled(True)
        self.upload_btn.setEnabled(True)
    
    def call_extract_segments(self):
        if self.file_path and (self.selected_times_default or self.selected_times_vertical):
            self.status_label.setText("Extracting segments...")
            self.progress_bar.setStyleSheet("background-color: #0047AB;")

            QTimer.singleShot(100, lambda: self.run_extraction())
    
    def run_extraction(self):
        try:
            extract_segments(self.file_path, self.selected_times_default, self.selected_times_vertical)
            self.status_label.setText("Segments extracted successfully!")
            self.progress_bar.setStyleSheet("background-color: #388e3c;")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.progress_bar.setStyleSheet("background-color: #d32f2f;")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_columns()

if __name__ == "__main__":
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    window = VideoSegmenterApp()
    window.showMaximized()
    sys.exit(app.exec())