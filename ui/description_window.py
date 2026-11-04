# ui/description_window.py — модальное окно с описанием игры
import os
import logging

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextBrowser, QScrollArea, QWidget
)
from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QPixmap, QPalette, QBrush
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

logger = logging.getLogger(__name__)

COLORS = {
    "bg_deep":   "#0e0e14",
    "bg_panel":  "#16161f",
    "bg_card":   "#1c1c26",
    "border":    "#26262f",
    "text":      "#EAEAEA",
    "text_dim":  "#8a8a96",
    "accent":    "#00e5ff",
}

class ImageGalleryViewer(QDialog):
    """Галерея для просмотра скриншотов с навигацией"""
    def __init__(self, image_paths, current_index=0, parent=None):
        super().__init__(parent)
        self.image_paths = image_paths
        self.current_index = current_index
        self.setWindowTitle("Просмотр скриншота")
        self.setModal(True)
        self.setStyleSheet("QDialog { background-color: #0e0e14; border: none; }")
        
        # Убираем рамку окна (делаем фреймлесс, как лаунчер)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Контейнер для картинки
        self.image_container = QWidget()
        self.image_container.setStyleSheet("background-color: transparent;")
        self.image_layout = QVBoxLayout(self.image_container)
        self.image_layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.image_layout.addWidget(self.label)
        
        self.main_layout.addWidget(self.image_container)
        
        # Панель с кнопками
        self.controls = QWidget(self)
        self.controls.setStyleSheet("background-color: rgba(14, 14, 20, 0.8); border-radius: 20px;")
        self.controls_layout = QHBoxLayout(self.controls)
        self.controls_layout.setContentsMargins(10, 5, 10, 5)
        self.controls_layout.setSpacing(20)
        
        # Кнопки
        self.btn_prev = QPushButton("◀")
        self.btn_prev.setStyleSheet("color: white; background: transparent; border: none; font-size: 18pt;")
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.clicked.connect(self.prev_image)
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setStyleSheet("color: #e81123; background: transparent; border: none; font-size: 18pt;")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.accept)
        
        self.btn_next = QPushButton("▶")
        self.btn_next.setStyleSheet("color: white; background: transparent; border: none; font-size: 18pt;")
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.clicked.connect(self.next_image)
        
        self.controls_layout.addWidget(self.btn_prev)
        self.controls_layout.addWidget(self.btn_close)
        self.controls_layout.addWidget(self.btn_next)
        
        # Счетчик
        self.counter_label = QLabel()
        self.counter_label.setStyleSheet("color: #9d85c7; font-size: 12pt;")
        self.controls_layout.addWidget(self.counter_label)
        
        self.controls.hide()
        
        self.load_image()

    def load_image(self):
        if not self.image_paths:
            return
            
        image_path = self.image_paths[self.current_index]
        pixmap = QPixmap(image_path)
        
        if not pixmap.isNull():
            # Получаем размер экрана
            screen = self.screen().availableGeometry()
            max_width = int(screen.width() * 0.9)
            max_height = int(screen.height() * 0.9)
            
            # УВЕЛИЧИВАЕМ В 2 РАЗА, но не больше 90% экрана
            target_w = min(pixmap.width() * 2, max_width)
            target_h = min(pixmap.height() * 2, max_height)
            
            scaled = pixmap.scaled(
                target_w,
                target_h,
                Qt.KeepAspectRatio,
                Qt.FastTransformation
            )
            self.label.setPixmap(scaled)
            self.resize(scaled.width(), scaled.height() + 60) # +60 для панели управления
        
        # Обновляем счетчик
        self.counter_label.setText(f"{self.current_index + 1} / {len(self.image_paths)}")

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()

    def next_image(self):
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.load_image()

    def showEvent(self, event):
        super().showEvent(event)
        # Центрируем панель управления внизу
        self.controls.setFixedSize(300, 50)
        self.controls.move(
            (self.width() - self.controls.width()) // 2,
            self.height() - self.controls.height() - 10
        )

    def enterEvent(self, event):
        self.controls.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.controls.hide()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        # Закрываем по клику на картинку (если кликнули не на панель)
        if event.button() == Qt.LeftButton:
            if not self.controls.geometry().contains(event.pos()):
                self.accept()


class ClickableLabel(QLabel):
    """QLabel, который реагирует на клик"""
    clicked = Signal(int)
    
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.setCursor(Qt.PointingHandCursor)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.index)
        super().mousePressEvent(event)


class DescriptionWindow(QDialog):
    """Модальное окно с HTML-описанием игры и скриншотами."""

    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game

        self.setWindowTitle(game.title)
        self.setModal(True)
        self.setMinimumSize(700, 600)
        self.resize(800, 650)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['bg_deep']}; }}")

        # --- ФОН ИЗ background.png ---
        images_dir = os.path.join(game.folder_path, "images")
        bg_path = os.path.join(images_dir, "background.png")
        if os.path.exists(bg_path):
            palette = self.palette()
            pixmap = QPixmap(bg_path)
            brush = QBrush(pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            palette.setBrush(QPalette.Window, brush)
            self.setPalette(palette)
            self.setStyleSheet(f"QDialog {{ background-color: rgba(14, 14, 20, 0.85); }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        # --- Заголовок ---
        title = QLabel(game.title)
        title.setStyleSheet(f"color: {COLORS['text']}; font-size: 18pt; font-weight: 600;")
        root.addWidget(title)

        console = QLabel(game.console)
        console.setStyleSheet(f"color: {COLORS['accent']}; font-size: 10pt;")
        root.addWidget(console)

        # --- Скриншоты ---
        self.shot_paths = []
        if game.screenshots:
            shots_scroll = QScrollArea()
            shots_scroll.setWidgetResizable(True)
            shots_scroll.setFixedHeight(100)
            shots_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            shots_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            shots_scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

            shots_inner = QWidget()
            shots_inner.setStyleSheet("background-color: transparent;")
            shots_layout = QHBoxLayout(shots_inner)
            shots_layout.setContentsMargins(0, 0, 0, 0)
            shots_layout.setSpacing(8)

            idx = 0
            for shot_path in game.screenshots:
                if not os.path.isfile(shot_path):
                    continue
                pix = QPixmap(shot_path)
                if pix.isNull():
                    continue
                pix = pix.scaledToHeight(90, Qt.SmoothTransformation)
                
                lbl = ClickableLabel(idx)
                lbl.setPixmap(pix)
                lbl.setStyleSheet("border-radius: 4px;")
                lbl.clicked.connect(self.open_gallery)
                
                shots_layout.addWidget(lbl)
                self.shot_paths.append(shot_path)
                idx += 1

            shots_layout.addStretch(1)
            shots_scroll.setWidget(shots_inner)
            root.addWidget(shots_scroll)

        # --- HTML-описание ---
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setStyleSheet(
            f"QTextBrowser {{ background-color: {COLORS['bg_panel']}; "
            f"color: {COLORS['text']}; border: 1px solid {COLORS['border']}; "
            f"border-radius: 6px; padding: 10px; font-size: 10pt; }}"
        )

        if game.html_path and os.path.isfile(game.html_path):
            try:
                with open(game.html_path, "r", encoding="utf-8") as f:
                    html = f.read()
                html = html.replace("background-color: #1c1c1c;", "background-color: transparent;")
                browser.setHtml(html)
            except Exception as e:
                logger.error(f"Ошибка чтения HTML: {e}")
                browser.setPlainText("Не удалось прочитать описание.")
        else:
            browser.setPlainText("Описание для этой игры отсутствует.")

        root.addWidget(browser, 1)

        # --- Видео (скрыто) ---
        self.video_widget = QVideoWidget()
        self.video_widget.setFixedHeight(240)
        self.video_widget.setStyleSheet("border-radius: 6px;")
        self.video_widget.hide()

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)
        
        video_path = os.path.join(game.folder_path, "video", "gameplay.mp4")
        if os.path.exists(video_path):
            self.player.setSource(QUrl.fromLocalFile(video_path))
            self.player.setLoops(QMediaPlayer.Infinite)
            root.addWidget(self.video_widget)

        # --- Кнопки ---
        buttons = QHBoxLayout()
        buttons.addStretch(1)

        if os.path.exists(video_path):
            self.btn_video = QPushButton("🎬 Видео")
            self.btn_video.setObjectName("consoleButton")
            self.btn_video.setFixedHeight(36)
            self.btn_video.setFixedWidth(100)
            self.btn_video.setCursor(Qt.PointingHandCursor)
            self.btn_video.clicked.connect(self._toggle_video)
            buttons.addWidget(self.btn_video)

        self.btn_play = QPushButton("▶  Запустить")
        self.btn_play.setObjectName("consoleButton")
        self.btn_play.setFixedHeight(36)
        self.btn_play.setFixedWidth(140)
        self.btn_play.setCursor(Qt.PointingHandCursor)
        self.btn_play.clicked.connect(self._on_play)
        buttons.addWidget(self.btn_play)

        self.btn_close = QPushButton("Закрыть")
        self.btn_close.setObjectName("consoleButton")
        self.btn_close.setFixedHeight(36)
        self.btn_close.setFixedWidth(100)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.accept)
        buttons.addWidget(self.btn_close)

        root.addLayout(buttons)

    def open_gallery(self, index):
        """Открывает галерею с выбранного индекса"""
        if not self.shot_paths:
            return
        viewer = ImageGalleryViewer(self.shot_paths, index, self)
        viewer.exec()

    def _toggle_video(self):
        if self.video_widget.isVisible():
            self.video_widget.hide()
            self.player.pause()
            self.btn_video.setText("🎬 Видео")
        else:
            self.video_widget.show()
            self.player.play()
            self.btn_video.setText("⏸ Скрыть видео")

    def _on_play(self):
        self.accept()
        self.result_game = self.game

    def closeEvent(self, event):
        if hasattr(self, 'player'):
            self.player.stop()
        super().closeEvent(event)