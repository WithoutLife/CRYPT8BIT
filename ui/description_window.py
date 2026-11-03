# ui/description_window.py — модальное окно с описанием игры
import os
import logging

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextBrowser, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


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

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # --- Заголовок ---
        title = QLabel(game.title)
        title.setStyleSheet(
            f"color: {COLORS['text']}; font-size: 18pt; font-weight: 600;"
        )
        root.addWidget(title)

        console = QLabel(game.console)
        console.setStyleSheet(
            f"color: {COLORS['accent']}; font-size: 10pt;"
        )
        root.addWidget(console)

        # --- Скриншоты (горизонтальная полоса) ---
        if game.screenshots:
            shots_scroll = QScrollArea()
            shots_scroll.setWidgetResizable(True)
            shots_scroll.setFixedHeight(180)
            shots_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            shots_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            shots_scroll.setStyleSheet(
                f"QScrollArea {{ background-color: {COLORS['bg_panel']}; "
                f"border: 1px solid {COLORS['border']}; border-radius: 6px; }}"
            )

            shots_inner = QWidget()
            shots_inner.setStyleSheet("background-color: transparent;")
            shots_layout = QHBoxLayout(shots_inner)
            shots_layout.setContentsMargins(8, 8, 8, 8)
            shots_layout.setSpacing(8)

            for shot_path in game.screenshots:
                if not os.path.isfile(shot_path):
                    continue
                pix = QPixmap(shot_path)
                if pix.isNull():
                    continue
                pix = pix.scaledToHeight(150, Qt.SmoothTransformation)
                lbl = QLabel()
                lbl.setPixmap(pix)
                lbl.setStyleSheet("border-radius: 4px;")
                shots_layout.addWidget(lbl)

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
                browser.setHtml(html)
            except Exception as e:
                logger.error(f"Ошибка чтения HTML: {e}")
                browser.setPlainText("Не удалось прочитать описание.")
        else:
            browser.setPlainText("Описание для этой игры отсутствует.")

        root.addWidget(browser, 1)

        # --- Кнопки ---
        buttons = QHBoxLayout()
        buttons.addStretch(1)

        self.btn_play = QPushButton("▶  Запустить")
        self.btn_play.setObjectName("consoleButton")  # используем стиль из main.py
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

    def _on_play(self):
        """Кнопка «Запустить» — закрываем окно и сообщаем родителю, что надо запустить игру."""
        self.accept()
        # Родитель (MainWindow) сам подхватит результат и вызовет launch_game
        self.result_game = self.game