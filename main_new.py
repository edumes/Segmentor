import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QScrollArea,
    QCheckBox,
    QFileDialog,
    QFrame,
    QSizePolicy,
    QMessageBox,
)
from PyQt6.QtGui import QGuiApplication, QPixmap, QImage, QColor, QPalette, QFont
from PyQt6.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal
import os
import cv2
from video_utils import extract_segments


class FrameLoaderThread(QThread):
    frames_loaded = pyqtSignal(list, list)
    progress_updated = pyqtSignal(int)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.canceled = False

    def run(self):
        video_cap = cv2.VideoCapture(self.file_path)
        if not video_cap.isOpened():
            self.frames_loaded.emit([], [])
            return

        fps = video_cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames_to_capture = range(0, total_frames, int(fps * 60))
        total = len(frames_to_capture)

        frames = []
        frame_times = []

        for i, frame_number in enumerate(frames_to_capture):
            if self.canceled:
                break

            video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            success, frame = video_cap.read()
            if not success:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # frame_rgb = cv2.resize(frame_rgb, (350, 250), interpolation=cv2.INTER_CUBIC)
            frames.append(frame_rgb)
            frame_times.append(frame_number / fps)

            progress = int((i + 1) / total * 100)
            self.progress_updated.emit(progress)

        video_cap.release()
        self.frames_loaded.emit(frames, frame_times)

    def cancel(self):
        self.canceled = True


class ThumbnailWidget(QWidget):
    def __init__(self, image_data, minute, time_str, parent=None):
        super().__init__(parent)
        self.minute = minute
        self.parent_app = parent

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        height, width, channel = image_data.shape
        bytes_per_line = 3 * width
        qimage = QImage(
            image_data.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
        )
        self.pixmap = QPixmap.fromImage(qimage)
        self.pixmap.setDevicePixelRatio(self.devicePixelRatioF())

        self.image_label = QLabel()
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(500, 375)
        self.image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.image_label.setStyleSheet(
            """
            QLabel {
                background-color: #333;
                border: 1px solid #555;
                border-radius: 5px;
            }
        """
        )
        self.update_image()
        layout.addWidget(self.image_label)

        time_label = QLabel(f"⏱ {time_str}")
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_label.setStyleSheet(
            """
            color: #aaa; 
            font-size: 14px; 
            background-color: #2a2a2a;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 500;
        """
        )
        layout.addWidget(time_label)

        checkbox_layout = QHBoxLayout()
        checkbox_layout.setContentsMargins(0, 10, 0, 0)
        checkbox_layout.setSpacing(15)

        self.default_check = QCheckBox("Default")
        self.vertical_check = QCheckBox("Vertical")

        checkbox_style = """
            QCheckBox {
                color: white;
                padding: 8px 12px;
                background-color: #3a3a3a;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
            }
            QCheckBox:hover {
                background-color: #4a4a4a;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
            }
            QCheckBox::indicator:checked {
                background-color: #3F00FF;
                border: 1px solid #0047AB;
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

        self.setStyleSheet(
            """
            QWidget {
                background-color: #323232;
                border-radius: 10px;
                border: 1px solid #444;
            }
        """
        )

    def update_image(self):
        if not self.pixmap.isNull():
            scaled_pixmap = self.pixmap.scaled(
                self.image_label.width(),
                self.image_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled_pixmap)

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
        self.setMinimumSize(1200, 850)

        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(40, 40, 40))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(63, 0, 255))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        self.setPalette(dark_palette)

        self.file_path = None
        self.clip = None
        self.selected_times_default = []
        self.selected_times_vertical = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)

        header_layout = QHBoxLayout()

        title_label = QLabel("Segmentor")
        title_label.setStyleSheet(
            """
            font-size: 28px; 
            font-weight: bold;
            color: #e0e0e0;
            padding: 5px;
        """
        )
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.upload_btn = QPushButton("📁 Upload Video")
        self.upload_btn.setFixedSize(220, 55)
        self.upload_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #5c5c5c;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                padding: 10px;
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
        """
        )
        self.upload_btn.clicked.connect(self.upload_video)
        header_layout.addWidget(self.upload_btn)

        main_layout.addLayout(header_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("border: 1px solid #444;")
        main_layout.addWidget(separator)

        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(15)

        preview_header = QHBoxLayout()

        preview_label = QLabel("🎬 Preview Frames")
        preview_label.setStyleSheet(
            """
            font-size: 20px; 
            font-weight: bold;
            color: #d0d0d0;
            padding: 8px;
        """
        )
        preview_header.addWidget(preview_label)

        preview_header.addStretch()

        self.resolution_label = QLabel("")
        self.resolution_label.setStyleSheet("color: #aaa; font-size: 14px;")
        preview_header.addWidget(self.resolution_label)

        preview_layout.addLayout(preview_header)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet(
            "background-color: #252525; border-radius: 10px;"
        )

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: #252525;")
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )
        self.grid_layout.setSpacing(25)
        self.grid_layout.setContentsMargins(30, 30, 30, 30)

        self.scroll_area.setWidget(self.scroll_content)
        preview_layout.addWidget(self.scroll_area, 1)

        main_layout.addLayout(preview_layout, 1)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(10, 0, 10, 0)

        self.extract_btn = QPushButton("🔧 Extract Segments")
        self.extract_btn.setFixedHeight(60)
        self.extract_btn.setEnabled(False)
        self.extract_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3F00FF;
                color: white;
                font-weight: bold;
                font-size: 18px;
                border-radius: 10px;
                padding: 12px 24px;
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
        """
        )
        self.extract_btn.clicked.connect(self.call_extract_segments)
        control_layout.addWidget(self.extract_btn)

        main_layout.addLayout(control_layout)

        status_layout = QVBoxLayout()
        status_layout.setSpacing(8)

        self.progress_bar = QLabel()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet(
            """
            background-color: #252525;
            border-radius: 4px;
        """
        )
        status_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready to upload video")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            """
            color: #aaa; 
            font-size: 14px; 
            padding: 8px;
            font-weight: 500;
        """
        )
        status_layout.addWidget(self.status_label)

        main_layout.addLayout(status_layout)

        self.columns = 4

        self.layout_timer = QTimer()
        self.layout_timer.timeout.connect(self.adjust_columns)
        self.layout_timer.start(500)

        self.loader_thread = None

    def adjust_columns(self):
        width = self.scroll_content.width()
        new_columns = max(1, min(4, width // 550))

        if new_columns != self.columns:
            self.columns = new_columns
            self.update_grid_layout()

    def update_grid_layout(self):
        widgets = []
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item.widget():
                widgets.append(item.widget())
                self.grid_layout.removeItem(item)

        for i, widget in enumerate(widgets):
            row = i // self.columns
            col = i % self.columns
            self.grid_layout.addWidget(widget, row, col)

    def upload_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)",
        )

        if file_path:
            self.file_path = file_path
            self.upload_btn.setEnabled(False)
            self.status_label.setText("Loading video...")
            self.progress_bar.setStyleSheet(
                """
                background-color: #3F00FF;
                border-radius: 4px;
            """
            )

            if self.loader_thread and self.loader_thread.isRunning():
                self.loader_thread.cancel()
                self.loader_thread.wait()

            self.loader_thread = FrameLoaderThread(file_path)
            self.loader_thread.frames_loaded.connect(self.display_preview_frames)
            self.loader_thread.start()

    def display_preview_frames(self, frames, frame_times):
        self.selected_times_default = []
        self.selected_times_vertical = []

        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not frames:
            self.status_label.setText("Failed to load video")
            self.progress_bar.setStyleSheet(
                """
                background-color: #d32f2f;
                border-radius: 4px;
            """
            )
            self.upload_btn.setEnabled(True)
            QMessageBox.critical(self, "Error", "Failed to load video file")
            return

        if frames:
            height, width, _ = frames[0].shape
            self.resolution_label.setText(f"Resolution: {width}×{height}")

        for idx, frame in enumerate(frames):
            minutes = int(frame_times[idx] // 60)
            seconds = int(frame_times[idx] % 60)
            time_str = f"{minutes:02d}:{seconds:02d}"

            thumbnail = ThumbnailWidget(frame, idx, time_str, self)
            row = idx // self.columns
            col = idx % self.columns
            self.grid_layout.addWidget(thumbnail, row, col)

        QApplication.processEvents()

        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if widget and hasattr(widget, "update_image"):
                widget.update_image()

        self.status_label.setText(f"Loaded {len(frames)} frames from video")
        self.progress_bar.setStyleSheet(
            """
            background-color: #388e3c;
            border-radius: 4px;
        """
        )
        self.extract_btn.setEnabled(True)
        self.upload_btn.setEnabled(True)
        QMessageBox.information(self, "Success", "Video loaded successfully!")

    def call_extract_segments(self):
        if self.file_path and (
            self.selected_times_default or self.selected_times_vertical
        ):
            self.status_label.setText("Extracting segments...")
            self.progress_bar.setStyleSheet(
                """
                background-color: #3F00FF;
                border-radius: 4px;
            """
            )

            QTimer.singleShot(100, self.run_extraction)

    def run_extraction(self):
        try:
            extract_segments(
                self.file_path,
                self.selected_times_default,
                self.selected_times_vertical,
            )
            self.status_label.setText("✅ Segments extracted successfully!")
            self.progress_bar.setStyleSheet(
                """
                background-color: #388e3c;
                border-radius: 4px;
            """
            )
            QMessageBox.information(self, "Success", "Segments extracted successfully!")
        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
            self.progress_bar.setStyleSheet(
                """
                background-color: #d32f2f;
                border-radius: 4px;
            """
            )
            QMessageBox.critical(
                self, "Error", f"Failed to extract segments:\n{str(e)}"
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_columns()
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if widget and hasattr(widget, "update_image"):
                widget.update_image()

    def closeEvent(self, event):
        if self.loader_thread and self.loader_thread.isRunning():
            self.loader_thread.cancel()
            self.loader_thread.wait()
        event.accept()


if __name__ == "__main__":
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(11)
    app.setFont(font)

    window = VideoSegmenterApp()
    window.showMaximized()
    sys.exit(app.exec())
