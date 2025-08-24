import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QScrollArea, QCheckBox, QFileDialog, QFrame, QSizePolicy,
    QSystemTrayIcon, QMenu, QMenuBar
)
from PyQt6.QtGui import (
    QGuiApplication, QPixmap, QImage, QColor, QPalette, QIcon, QFont,
    QDragEnterEvent, QDropEvent, QAction
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QUrl, QMimeData, QStandardPaths
import cv2
from video_utils import extract_segments
from platform_utils import get_platform_config, is_macos, is_windows, is_apple_silicon

class FrameLoaderThread(QThread):
    frames_loaded = pyqtSignal(list, list)
    progress_updated = pyqtSignal(int)
    
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
        
        for i, frame_number in enumerate(frames_to_capture):
            video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            success, frame = video_cap.read()
            if not success:
                break
            
            # Otimização para Apple Silicon: usar interpolação mais eficiente
            config = get_platform_config()
            if config.is_apple_silicon:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_rgb = cv2.resize(frame_rgb, (500, 375), interpolation=cv2.INTER_LINEAR)
            else:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_rgb = cv2.resize(frame_rgb, (500, 375), interpolation=cv2.INTER_CUBIC)
            
            frames.append(frame_rgb)
            frame_times.append(frame_number / fps)
            
            # Emitir progresso
            progress = int((i + 1) / len(frames_to_capture) * 100)
            self.progress_updated.emit(progress)
            
        video_cap.release()
        self.frames_loaded.emit(frames, frame_times)

class ThumbnailWidget(QWidget):
    def __init__(self, image_data, minute, time_str, parent=None):
        super().__init__(parent)
        self.minute = minute
        self.parent_app = parent
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)  # Reduzido para economizar espaço
        layout.setSpacing(5)
        self.setLayout(layout)
        
        # Definir tamanho fixo para o widget para evitar barras de rolagem
        self.setFixedSize(350, 300)  # Tamanho aumentado proporcionalmente mantendo qualidade

        height, width, channel = image_data.shape
        bytes_per_line = 3 * width
        qimage = QImage(image_data.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        self.pixmap = QPixmap.fromImage(qimage)
        
        # Otimização para displays de alta densidade (Retina)
        config = get_platform_config()
        self.pixmap.setDevicePixelRatio(config.ui_scaling)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Removido setMinimumSize para evitar barras de rolagem desnecessárias
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.image_label.setScaledContents(True)  # Permite que a imagem se ajuste ao tamanho do label
        
        # Estilo adaptado para tema escuro nativo do macOS
        if is_macos() and config.native_features.get('dark_mode_detection'):
            self.image_label.setStyleSheet("""
                QLabel {
                    background-color: #1e1e1e;
                    border: 1px solid #3a3a3a;
                    border-radius: 8px;
                }
            """)
        else:
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

        # Estilo de checkbox adaptado para macOS
        if is_macos():
            checkbox_style = """
                QCheckBox {
                    color: white;
                    padding: 4px;
                    background-color: #2a2a2a;
                    border-radius: 6px;
                    font-size: 13px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 4px;
                }
                QCheckBox::indicator:checked {
                    background-color: #007AFF;
                    border: 1px solid #0051D5;
                }
                QCheckBox::indicator:unchecked {
                    background-color: #48484a;
                    border: 1px solid #6d6d70;
                }
            """
        else:
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

        # Estilo do widget principal adaptado para macOS
        if is_macos():
            self.setStyleSheet("""
                QWidget {
                    background-color: #2a2a2a;
                    border-radius: 10px;
                    padding: 2px;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #3a3a3a;
                    border-radius: 8px;
                    padding: 2px;
                }
            """)
    
    def update_image(self):
        if not self.pixmap.isNull():
            # Definir um tamanho padrão para o cálculo se o widget ainda não foi renderizado
            label_width = max(self.image_label.width(), 375)
            label_height = max(self.image_label.height(), 281)
            
            scaled_pixmap = self.pixmap.scaled(
                label_width, 
                label_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
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
        self.config = get_platform_config()
        self.setup_ui()
        self.setup_native_features()
        
        self.file_path = None
        self.clip = None
        self.selected_times_default = []
        self.selected_times_vertical = []
    
    def setup_ui(self):
        """Configura a interface do usuário com otimizações específicas da plataforma"""
        self.setWindowTitle("Segmentor")
        self.setMinimumSize(1200, 800)  # Aumentado de 1000x700 para 1200x800 para acomodar quadros maiores
        
        # Configurar paleta de cores adaptada para cada plataforma
        self.setup_theme()
        
        # Configurar widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Configurar menu bar (apenas no macOS)
        if is_macos() and self.config.native_features.get('menu_bar_integration'):
            self.setup_menu_bar()

        # Header layout
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
        
        # Estilo de botão adaptado para macOS
        if is_macos():
            button_style = """
                QPushButton {
                    background-color: #007AFF;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    border-radius: 8px;
                    padding: 5px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #0051D5;
                }
                QPushButton:pressed {
                    background-color: #003D99;
                }
                QPushButton:disabled {
                    background-color: #48484a;
                    color: #8e8e93;
                }
            """
        else:
            button_style = """
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
            """
        
        self.upload_btn.setStyleSheet(button_style)
        self.upload_btn.clicked.connect(self.upload_video)
        header_layout.addWidget(self.upload_btn)

        main_layout.addLayout(header_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #555;")
        main_layout.addWidget(separator)

        # Preview layout
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
        
        # Estilo de scroll area adaptado para macOS
        if is_macos():
            scroll_style = "background-color: #1e1e1e; border-radius: 10px;"
        else:
            scroll_style = "background-color: #252525; border-radius: 8px;"
        
        self.scroll_area.setStyleSheet(scroll_style)
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet(scroll_style)
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.grid_layout.setSpacing(15)  # Aumentado de 10 para 15 para melhor espaçamento
        self.grid_layout.setContentsMargins(25, 25, 25, 25)  # Aumentado de 20 para 25
        
        self.scroll_area.setWidget(self.scroll_content)
        preview_layout.addWidget(self.scroll_area, 1)
        
        main_layout.addLayout(preview_layout, 1)

        # Extract button
        self.extract_btn = QPushButton("Extract Segments")
        self.extract_btn.setFixedHeight(50)
        self.extract_btn.setEnabled(False)
        
        if is_macos():
            extract_style = """
                QPushButton {
                    background-color: #34C759;
                    color: white;
                    font-weight: bold;
                    font-size: 16px;
                    border-radius: 10px;
                    padding: 5px;
                    border: none;
                }
                QPushButton:disabled {
                    background-color: #48484a;
                    color: #8e8e93;
                }
                QPushButton:hover:enabled {
                    background-color: #30B454;
                }
                QPushButton:pressed:enabled {
                    background-color: #28A745;
                }
            """
        else:
            extract_style = """
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
            """
        
        self.extract_btn.setStyleSheet(extract_style)
        self.extract_btn.clicked.connect(self.call_extract_segments)
        main_layout.addWidget(self.extract_btn)

        self.columns = 4

        # Status label
        self.status_label = QLabel("Ready to upload video")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #aaa; font-size: 12px; padding: 5px;")
        main_layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QLabel()
        self.progress_bar.setFixedHeight(4)
        if is_macos():
            self.progress_bar.setStyleSheet("background-color: #1e1e1e; border-radius: 2px;")
        else:
            self.progress_bar.setStyleSheet("background-color: #252525;")
        main_layout.addWidget(self.progress_bar)

        # Layout timer
        self.layout_timer = QTimer()
        self.layout_timer.timeout.connect(self.adjust_columns)
        self.layout_timer.start(500)
    
    def setup_theme(self):
        """Configura tema específico da plataforma"""
        dark_palette = QPalette()
        
        if is_macos():
            # Cores do tema escuro nativo do macOS
            dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
            dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.ColorRole.Base, QColor(22, 22, 22))
            dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(42, 42, 42))
            dark_palette.setColor(QPalette.ColorRole.Button, QColor(48, 48, 52))
            dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 255))
            dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        else:
            # Tema padrão para Windows/Linux
            dark_palette.setColor(QPalette.ColorRole.Window, QColor(35, 35, 35))
            dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
            dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(142, 45, 197).lighter())
            dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        
        self.setPalette(dark_palette)
    
    def setup_menu_bar(self):
        """Configura menu bar nativo do macOS"""
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu('File')
        
        open_action = QAction('Open Video...', self)
        open_action.setShortcut('Cmd+O')
        open_action.triggered.connect(self.upload_video)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction('Quit', self)
        quit_action.setShortcut('Cmd+Q')
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Menu Edit
        edit_menu = menubar.addMenu('Edit')
        
        select_all_default = QAction('Select All Default', self)
        select_all_default.triggered.connect(self.select_all_default)
        edit_menu.addAction(select_all_default)
        
        select_all_vertical = QAction('Select All Vertical', self)
        select_all_vertical.triggered.connect(self.select_all_vertical)
        edit_menu.addAction(select_all_vertical)
        
        edit_menu.addSeparator()
        
        clear_selection = QAction('Clear Selection', self)
        clear_selection.triggered.connect(self.clear_selection)
        edit_menu.addAction(clear_selection)
    
    def setup_native_features(self):
        """Configura recursos nativos específicos da plataforma"""
        # Habilitar drag and drop
        if self.config.native_features.get('drag_and_drop'):
            self.setAcceptDrops(True)
        
        # Configurar system tray (se suportado)
        if self.config.native_features.get('notification_center') and QSystemTrayIcon.isSystemTrayAvailable():
            self.setup_system_tray()
    
    def setup_system_tray(self):
        """Configura system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Criar menu do tray
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        
        # Definir ícone (usar ícone padrão por enquanto)
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        self.tray_icon.show()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Manipula evento de drag enter"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1:
                file_path = urls[0].toLocalFile()
                if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """Manipula evento de drop"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.load_video(file_path)
            event.acceptProposedAction()
    
    def select_all_default(self):
        """Seleciona todos os checkboxes default"""
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, ThumbnailWidget):
                widget.default_check.setChecked(True)
    
    def select_all_vertical(self):
        """Seleciona todos os checkboxes vertical"""
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, ThumbnailWidget):
                widget.vertical_check.setChecked(True)
    
    def clear_selection(self):
        """Limpa todas as seleções"""
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, ThumbnailWidget):
                widget.default_check.setChecked(False)
                widget.vertical_check.setChecked(False)
    
    def adjust_columns(self):
        width = self.scroll_content.width()
        # Calcular colunas baseado no tamanho fixo dos widgets (350px + espaçamento)
        widget_width = 350 + 15  # largura do widget + espaçamento
        available_width = width - 50  # descontar margens
        
        # Calcular número ideal de colunas
        ideal_columns = max(1, available_width // widget_width)
        
        # Limitar a 4 colunas máximo conforme solicitado
        new_columns = min(4, ideal_columns)
        
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
        """Abre diálogo para selecionar vídeo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.MoviesLocation),
            "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )
        
        if file_path:
            self.load_video(file_path)
    
    def load_video(self, file_path):
        """Carrega vídeo especificado"""
        self.file_path = file_path
        self.upload_btn.setEnabled(False)
        self.status_label.setText("Loading video...")
        
        if is_macos():
            self.progress_bar.setStyleSheet("background-color: #007AFF; border-radius: 2px;")
        else:
            self.progress_bar.setStyleSheet("background-color: #0047AB;")

        self.loader_thread = FrameLoaderThread(file_path)
        self.loader_thread.frames_loaded.connect(self.display_preview_frames)
        self.loader_thread.progress_updated.connect(self.update_progress)
        self.loader_thread.start()
    
    def update_progress(self, progress):
        """Atualiza progresso do carregamento"""
        self.status_label.setText(f"Loading video... {progress}%")
    
    def display_preview_frames(self, frames, frame_times):
        self.selected_times_default = []
        self.selected_times_vertical = []

        # Limpar widgets existentes
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        if not frames:
            self.status_label.setText("Failed to load video")
            if is_macos():
                self.progress_bar.setStyleSheet("background-color: #FF3B30; border-radius: 2px;")
            else:
                self.progress_bar.setStyleSheet("background-color: #d32f2f;")
            self.upload_btn.setEnabled(True)
            return

        # Criar thumbnails
        for idx, frame in enumerate(frames):
            minutes = int(frame_times[idx] // 60)
            seconds = int(frame_times[idx] % 60)
            time_str = f"{minutes:02d}:{seconds:02d}"

            thumbnail = ThumbnailWidget(frame, idx, time_str, self)
            row = idx // self.columns
            col = idx % self.columns
            self.grid_layout.addWidget(thumbnail, row, col)
        
        self.status_label.setText(f"Loaded {len(frames)} frames from video")
        if is_macos():
            self.progress_bar.setStyleSheet("background-color: #34C759; border-radius: 2px;")
        else:
            self.progress_bar.setStyleSheet("background-color: #388e3c;")
        self.extract_btn.setEnabled(True)
        self.upload_btn.setEnabled(True)
        
        # Mostrar notificação nativa (se suportado)
        if self.config.native_features.get('notification_center') and hasattr(self, 'tray_icon'):
            self.tray_icon.showMessage(
                "Segmentor",
                f"Video loaded successfully! {len(frames)} frames ready for processing.",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
    
    def call_extract_segments(self):
        if self.file_path and (self.selected_times_default or self.selected_times_vertical):
            self.status_label.setText("Extracting segments...")
            if is_macos():
                self.progress_bar.setStyleSheet("background-color: #FF9500; border-radius: 2px;")
            else:
                self.progress_bar.setStyleSheet("background-color: #0047AB;")

            QTimer.singleShot(100, lambda: self.run_extraction())
    
    def run_extraction(self):
        try:
            extract_segments(self.file_path, self.selected_times_default, self.selected_times_vertical)
            self.status_label.setText("Segments extracted successfully!")
            if is_macos():
                self.progress_bar.setStyleSheet("background-color: #34C759; border-radius: 2px;")
            else:
                self.progress_bar.setStyleSheet("background-color: #388e3c;")
            
            # Mostrar notificação de sucesso
            if self.config.native_features.get('notification_center') and hasattr(self, 'tray_icon'):
                self.tray_icon.showMessage(
                    "Segmentor",
                    "Video segments extracted successfully!",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            if is_macos():
                self.progress_bar.setStyleSheet("background-color: #FF3B30; border-radius: 2px;")
            else:
                self.progress_bar.setStyleSheet("background-color: #d32f2f;")
            
            # Mostrar notificação de erro
            if self.config.native_features.get('notification_center') and hasattr(self, 'tray_icon'):
                self.tray_icon.showMessage(
                    "Segmentor",
                    f"Error extracting segments: {str(e)}",
                    QSystemTrayIcon.MessageIcon.Critical,
                    5000
                )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_columns()

def main():
    """Função principal com configurações específicas da plataforma"""
    config = get_platform_config()
    
    # Configurações de ambiente específicas da plataforma
    if config.is_macos:
        os.environ["QT_MAC_WANTS_LAYER"] = "1"
        if config.is_apple_silicon:
            os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"
    
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    
    # Configurar fonte específica da plataforma
    font = QFont()
    if config.is_macos:
        font.setFamily("SF Pro Display")
        font.setPointSize(11)
    elif config.is_windows:
        font.setFamily("Segoe UI")
        font.setPointSize(10)
    else:
        font.setFamily("Ubuntu")
        font.setPointSize(10)
    
    app.setFont(font)
    
    # Configurar ícone da aplicação
    app.setApplicationName("Segmentor")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Segmentor")
    
    window = VideoSegmenterApp()
    
    # Configurar exibição maximizada para todas as plataformas
    window.showMaximized()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()