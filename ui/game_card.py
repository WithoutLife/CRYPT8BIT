# ui/game_card.py — виджет одной карточки игры

import os
import logging

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QPainter, QPainterPath

from core.favorites import is_favorite

logger = logging.getLogger(__name__)

# --- РАЗМЕРЫ ---
CARD_WIDTH = 220
CARD_HEIGHT = 220
COVER_WIDTH = 200
COVER_HEIGHT = 130

# --- ПАЛИТРА ---
COLOR_BORDER = "#3d2666"           # Тонкая фиолетовая рамка по умолчанию
COLOR_BORDER_HOVER = "#d966ff"     # Яркая при наведении
COLOR_BORDER_SELECTED = "#d966ff"  # Яркая при выделении
COLOR_BG = "transparent"
COLOR_BG_HOVER = "rgba(26, 16, 40, 0.6)"
COLOR_BG_SELECTED = "rgba(26, 16, 40, 0.8)"
COLOR_TEXT = "#e5e5e5"


class GameCard(QFrame):
    """Карточка игры: обложка (картридж) + название."""

    clicked = Signal(object)
    double_clicked = Signal(object)
    context_menu_requested = Signal(object, object)

    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self._hovered = False
        self._selected = False

        self.setFixedSize(CARD_WIDTH, CARD_HEIGHT)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # Контейнер под обложку
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(COVER_WIDTH, COVER_HEIGHT)
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setStyleSheet("background: transparent; border: none;")
        self._load_cover()
        layout.addWidget(self.cover_label, 0, Qt.AlignHCenter)

        # Звёздочка избранного
        self.fav_label = QLabel("★", self)
        self.fav_label.setStyleSheet(
            "color: #fca311; font-size: 18pt; background: transparent; border: none;"
        )
        self.fav_label.setFixedSize(26, 26)
        self.fav_label.move(self.width() - 32, 8)
        self.fav_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.reload_favorite()

        # Название
        self.title_label = QLabel(game.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 9.5pt; background: transparent; border: none; font-weight: bold;")
        self.title_label.setFixedHeight(36)
        layout.addWidget(self.title_label)

        layout.addStretch()
        self._update_style()

    def _load_cover(self):
        if not self.game.cartridge_path or not os.path.isfile(self.game.cartridge_path):
            self.cover_label.setText("нет обложки")
            self.cover_label.setStyleSheet("color: #555; font-size: 9pt; border: 1px dashed #3d2666; border-radius: 6px;")
            return

        pixmap = QPixmap(self.game.cartridge_path)
        if pixmap.isNull():
            self.cover_label.setText("ошибка")
            return

        # УВЕЛИЧИЛИ область отрисовки (картридж будет больше)
        target_size = QSize(COVER_WIDTH + 20, COVER_HEIGHT + 10) 
        scaled = pixmap.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Закругляем углы
        rounded = QPixmap(scaled.size())
        rounded.fill(Qt.transparent)
        
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, scaled.width(), scaled.height(), 6, 6)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, scaled)
        painter.end()

        self.cover_label.setPixmap(rounded)

    def _update_style(self):
        if self._selected:
            border = COLOR_BORDER_SELECTED
            bg = COLOR_BG_SELECTED
            border_width = "2px"
        elif self._hovered:
            border = COLOR_BORDER_HOVER
            bg = COLOR_BG_HOVER
            border_width = "2px"
        else:
            border = COLOR_BORDER
            bg = COLOR_BG
            border_width = "1px" # Тонкая рамка в обычном состоянии

        self.setStyleSheet(
            f"GameCard {{ background-color: {bg}; "
            f"border: {border_width} solid {border}; border-radius: 12px; }}"
        )

    def set_selected(self, value: bool):
        if self._selected == value:
            return
        self._selected = value
        self._update_style()

    def reload_favorite(self):
        self.fav_label.setVisible(is_favorite(self.game.folder_name))

    def enterEvent(self, event):
        self._hovered = True
        self._update_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._update_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.game)
        elif event.button() == Qt.RightButton:
            self.context_menu_requested.emit(self.game, event.globalPosition().toPoint())
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self.game)
        super().mouseDoubleClickEvent(event)