# ui/top_carousel.py — карусель «Недавние»

import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap

from core.history import load_history

# Уменьшенные размеры
CAROUSEL_WIDTH = 90
CAROUSEL_HEIGHT = 120

class TopCarousel(QWidget):
    item_double_clicked = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(160) # Уменьшили высоту панели (было 240)
        self.all_games = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 10, 24, 10)
        main_layout.setSpacing(4)

        # Заголовок (сделали чуть меньше)
        self.title_label = QLabel("НЕДАВНИЕ")
        self.title_label.setStyleSheet("color: #8b8b93; font-size: 9pt; font-weight: bold; letter-spacing: 1px;")
        main_layout.addWidget(self.title_label)

        # Прокручиваемая область
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; border: none; } QWidget { background: transparent; }")
        
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scroll_content = QWidget()
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(10) # Уменьшили отступы между карточками
        self.scroll_layout.setAlignment(Qt.AlignLeft)
        self.scroll.setWidget(self.scroll_content)

        main_layout.addWidget(self.scroll)

    def update_history(self, all_games):
        self.all_games = all_games
        history = load_history()
        
        # Очищаем старые виджеты
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not history:
            self.hide()
            return

        self.show()

        # Берем последние 10 игр
        for entry in history[:10]:
            folder = entry.get("folder_name")
            game = next((g for g in self.all_games if g.folder_name == folder), None)
            if not game:
                continue

            # Контейнер карточки
            card = QFrame()
            card.setFixedSize(CAROUSEL_WIDTH, CAROUSEL_HEIGHT)
            card.setCursor(Qt.PointingHandCursor)
            card.setStyleSheet("""
                QFrame {
                    background-color: #1a1028;
                    border: 1px solid #3d2666;
                    border-radius: 6px;
                }
                QFrame:hover {
                    border: 1px solid #d966ff;
                    background-color: #201330;
                }
            """)

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(6, 6, 6, 6)
            card_layout.setSpacing(2)

            # Обложка
            cover = QLabel()
            cover.setAlignment(Qt.AlignCenter)
            cover.setFixedSize(CAROUSEL_WIDTH - 12, CAROUSEL_HEIGHT - 30) # Оставляем место под текст
            
            if game.cartridge_path and os.path.isfile(game.cartridge_path):
                pixmap = QPixmap(game.cartridge_path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    cover.setPixmap(scaled)
                else:
                    cover.setText("нет")
            else:
                cover.setText("нет")
            
            cover.setStyleSheet("color: #555; font-size: 7pt;")
            card_layout.addWidget(cover)

            # Название (уменьшили шрифт)
            title = QLabel(game.title)
            title.setAlignment(Qt.AlignCenter)
            title.setWordWrap(True)
            title.setStyleSheet("color: #e5e5e5; font-size: 7.5pt; border: none;")
            card_layout.addWidget(title)

            # Обработка кликов
            card.mousePressEvent = lambda event, g=game: self._on_click(event, g)
            card.mouseDoubleClickEvent = lambda event, g=game: self._on_double_click(event, g)

            self.scroll_layout.addWidget(card)
            
        self.scroll_layout.addStretch(1)

    def _on_click(self, event, game):
        if event.button() == Qt.LeftButton:
            pass

    def _on_double_click(self, event, game):
        if event.button() == Qt.LeftButton:
            self.item_double_clicked.emit(game)