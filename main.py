# main.py — CRYPT8BIT (Synthwave Edition)
# Запуск: py -3.12 main.py

import sys
import ctypes
import logging
import os
import subprocess
import webbrowser
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame, QMenu, QButtonGroup, QScrollArea, QSizePolicy,
    QGraphicsColorizeEffect, QGraphicsDropShadowEffect, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QRegion, QPainterPath, QIcon, QPixmap, QColor, QPainter, QLinearGradient

from core.scanner import scan_all_games
from core.launcher import launch_game
from core.history import load_history
from ui.game_grid import GameGrid
from ui.description_window import DescriptionWindow
from ui.neon_icons import NeonIcon
from core.favorites import toggle_favorite, load_favorites

# ----------------------------------------------------------------------
# Логирование
# ----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# WinAPI
# ----------------------------------------------------------------------
user32 = ctypes.windll.user32

WM_NCLBUTTONDOWN = 0x00A1
HTCAPTION        = 2
HTLEFT           = 10
HTRIGHT          = 11
HTTOP            = 12
HTTOPLEFT        = 13
HTTOPRIGHT       = 14
HTBOTTOM         = 15
HTBOTTOMLEFT     = 16
HTBOTTOMRIGHT    = 17

RESIZE_MARGIN = 12

# ----------------------------------------------------------------------
# Палитра
# ----------------------------------------------------------------------
COLORS = {
    "bg_deep":      "#0a0612",
    "bg_panel":     "#120b1c",
    "bg_card":      "#1a1028",
    "border":       "#3d2666",
    "text":         "#f2ebff",
    "text_dim":     "#9d85c7",
    "accent":       "#d966ff",
    "favorite":     "#fca311",
}

# ----------------------------------------------------------------------
# QSS
# ----------------------------------------------------------------------
STYLE_SHEET = f"""
QMainWindow {{
    background-color: {COLORS['bg_deep']};
}}
QWidget#centralWidget {{
    background: transparent;
}}
QFrame#leftPanel {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #150c22, stop:1 #050210);
    border-right: 1px solid {COLORS['border']};
}}
QPushButton#navButton {{
    background-color: transparent;
    border: none;
    border-radius: 8px;
}}
QPushButton#navButton:hover {{
    background-color: {COLORS['bg_card']};
}}
QPushButton#navButton:checked {{
    background-color: {COLORS['bg_card']};
    border-left: 3px solid {COLORS['accent']};
}}
QFrame#titleBar {{
    background-color: transparent;
    border-bottom: 1px solid {COLORS['border']};
}}
QPushButton#windowControlButton {{
    background-color: transparent;
    border: none;
    color: {COLORS['text_dim']};
    font-size: 14pt;
    padding: 8px 16px;
}}
QPushButton#windowControlButton:hover {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text']};
}}
QPushButton#closeButton:hover {{
    background-color: #e81123;
    color: white;
}}
QFrame#toolbar {{
    background: transparent;
    border-bottom: 1px solid {COLORS['border']};
}}
QPushButton#consoleButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
}}
QPushButton#consoleButton:hover {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
}}
QPushButton#consoleButton:checked {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['accent']};
}}
QLineEdit#searchBox {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 16px;
    color: {COLORS['text']};
    font-size: 10pt;
}}
QLineEdit#searchBox:focus {{
    border: 1px solid {COLORS['accent']};
}}
QFrame#footer {{
    background-color: transparent;
    border-top: 1px solid {COLORS['border']};
}}
QLabel#footerLabel {{
    color: {COLORS['text_dim']};
    font-size: 9pt;
    padding: 0 16px;
}}
QScrollArea#gameScrollArea {{
    background-color: transparent;
    border: none;
}}
QWidget#gridWidget {{
    background-color: transparent;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: {COLORS['border']};
    border-radius: 4px;
    min-height: 40px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLORS['accent']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QMenu {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px;
}}
QMenu::item {{
    padding: 8px 24px 8px 16px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['accent']};
}}
"""

# ----------------------------------------------------------------------
# Левая панель
# ----------------------------------------------------------------------
class LeftPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("leftPanel")
        self.setFixedWidth(70)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 20, 8, 20)
        layout.setSpacing(8)
        
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons = {}
        
        nav_items = [
            ("home",     "home",   "Все игры"),
            ("favorite", "star",   "Избранное"),
            ("recent",   "recent", "Недавние"),
            ("settings", "add",    "Создать игру"),
        ]
        
        for key, icon_type, tooltip in nav_items:
            btn = QPushButton()
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.setToolTip(tooltip)
            btn.setFixedSize(54, 54)
            btn.setFocusPolicy(Qt.NoFocus)
            
            icon_widget = NeonIcon(icon_type, COLORS['accent'])
            btn_layout = QVBoxLayout(btn)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.addWidget(icon_widget)
            
            layout.addWidget(btn, 0, Qt.AlignHCenter)
            self.nav_buttons[key] = btn
            self.nav_group.addButton(btn)
            
        self.nav_buttons["home"].setChecked(True)
        layout.addStretch(1)

# ----------------------------------------------------------------------
# Title bar
# ----------------------------------------------------------------------
class TitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(10)
        
        self.logo_label = QLabel()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        logo_path = os.path.join(base_dir, "assets", "crypt8bit_logo.png")
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaledToHeight(40, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
            
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(COLORS['accent']))
            shadow.setOffset(0, 0)
            self.logo_label.setGraphicsEffect(shadow)
        else:
            self.logo_label.setText("CRYPT8BIT")
            self.logo_label.setStyleSheet(f"color: {COLORS['accent']}; font-weight: 800; font-size: 16pt; letter-spacing: 3px;")
            
        layout.addWidget(self.logo_label)
        layout.addStretch(1)
        
        self.btn_min = QPushButton("—")
        self.btn_max = QPushButton("□")
        self.btn_close = QPushButton("✕")
        for btn in (self.btn_min, self.btn_max, self.btn_close):
            btn.setObjectName("windowControlButton")
            btn.setFixedSize(48, 48) 
            btn.setFocusPolicy(Qt.NoFocus)
            layout.addWidget(btn)
        self.btn_close.setObjectName("closeButton")

# ----------------------------------------------------------------------
# Toolbar (Консоли)
# ----------------------------------------------------------------------
class Toolbar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("toolbar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(72)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(12)
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, "assets")

        self.console_group = QButtonGroup(self)
        self.console_group.setExclusive(True)
        self.console_buttons = {}
        
        consoles = [
            ("DENDY", "icon_dendy.png", "Dendy"),
            ("SEGA", "icon_sega.png", "Sega"),
            ("SONY", "icon_sony.png", "Sony"),
        ]
        
        for key, icon_file, tooltip in consoles:
            btn = QPushButton()
            btn.setObjectName("consoleButton")
            btn.setCheckable(True)
            btn.setToolTip(tooltip)
            btn.setFixedSize(48, 48)
            btn.setFocusPolicy(Qt.NoFocus)
            
            icon_path = os.path.join(assets_dir, icon_file)
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(QSize(32, 32))
                
                shadow = QGraphicsDropShadowEffect(btn)
                shadow.setBlurRadius(10)
                shadow.setColor(QColor(COLORS['accent']))
                shadow.setOffset(0, 0)
                btn.setGraphicsEffect(shadow)

            layout.addWidget(btn)
            self.console_buttons[key] = btn
            self.console_group.addButton(btn)

        self.console_buttons["DENDY"].setChecked(True)
        
        self.search = QLineEdit()
        self.search.setObjectName("searchBox")
        self.search.setPlaceholderText("Поиск игр...")
        self.search.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.search)

# ----------------------------------------------------------------------
# Footer (с ссылками)
# ----------------------------------------------------------------------
class Footer(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("footer")
        self.setFixedHeight(30)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 16, 0)
        layout.setSpacing(15)
        
        self.left = QLabel("v3.8.0 · No_fate") 
        self.left.setObjectName("footerLabel")
        layout.addWidget(self.left)
        
        layout.addStretch(1)
        
        self.right = QLabel("Игр: 0 · ★: 0")
        self.right.setObjectName("footerLabel")
        layout.addWidget(self.right)
        
        self.link_roms = QPushButton("Скачать РОМы")
        self.link_emus = QPushButton("Скачать эмуляторы")
        
        for btn in (self.link_roms, self.link_emus):
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #9d85c7;
                    font-size: 9pt;
                    text-decoration: underline;
                }
                QPushButton:hover {
                    color: #d966ff;
                }
            """)
            btn.hide()
            layout.addWidget(btn)

# ----------------------------------------------------------------------
# Главное окно
# ----------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CRYPT8BIT")
        self.setMinimumSize(900, 600)
        self.resize(1060, 800) 

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self._corner_radius = 12

        self.all_games = []
        self.current_console = "DENDY"
        self.search_text = ""
        self.only_favorites = False
        self.is_recent_mode = False
        self.links_data = self.load_links()
        self.current_roms_url = ""
        self.current_emu_url = ""

        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = TitleBar()
        main_layout.addWidget(self.title_bar)

        self.toolbar = Toolbar()
        main_layout.addWidget(self.toolbar)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.left_panel = LeftPanel()
        content_layout.addWidget(self.left_panel)

        right_content = QWidget()
        right_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        right_layout = QVBoxLayout(right_content)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # УБРАЛИ КАРУСЕЛЬ - СРАЗУ СЕТКА
        self.game_grid = GameGrid()
        self.game_grid.card_clicked.connect(self.on_card_clicked)
        self.game_grid.card_double_clicked.connect(self.on_card_double_clicked)
        self.game_grid.card_context_menu.connect(self.on_card_context_menu)
        right_layout.addWidget(self.game_grid, 1)

        content_layout.addWidget(right_content, 1)
        main_layout.addLayout(content_layout, 1)

        self.footer = Footer()
        main_layout.addWidget(self.footer)

        for key, btn in self.left_panel.nav_buttons.items():
            btn.clicked.connect(lambda checked=False, k=key: self.on_nav_clicked(k))
            
        for key, btn in self.toolbar.console_buttons.items():
            btn.clicked.connect(lambda checked=False, k=key: self.switch_console(k))

        self.title_bar.btn_min.clicked.connect(self.showMinimized)
        self.title_bar.btn_max.clicked.connect(self._toggle_max)
        self.title_bar.btn_close.clicked.connect(self.close)
        self.title_bar.installEventFilter(self)

        self.toolbar.search.textChanged.connect(self.on_search)

        self.footer.link_roms.clicked.connect(self.open_roms_link)
        self.footer.link_emus.clicked.connect(self.open_emus_link)

        frame = self.frameGeometry()
        center_point = QApplication.primaryScreen().availableGeometry().center()
        frame.moveCenter(center_point)
        self.move(frame.topLeft())

        QTimer.singleShot(50, self._apply_rounded_mask)
        QTimer.singleShot(100, self.load_games)

    def load_links(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        links_path = os.path.join(base_dir, "links.json")
        if os.path.exists(links_path):
            try:
                with open(links_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Ошибка чтения links.json: {e}")
        return {}

    def open_roms_link(self):
        if self.current_roms_url:
            webbrowser.open(self.current_roms_url)

    def open_emus_link(self):
        if self.current_emu_url:
            webbrowser.open(self.current_emu_url)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#050210"))
        gradient.setColorAt(0.3, QColor("#160b29"))
        gradient.setColorAt(0.7, QColor("#0d071a"))
        gradient.setColorAt(1.0, QColor("#050210"))
        
        painter.fillRect(self.rect(), gradient)
        painter.end()

    def load_games(self):
        logger.info("Сканирование папок с играми...")
        self.all_games = scan_all_games()
        self.refresh_grid()

    def refresh_grid(self):
        self.is_recent_mode = False
        filtered = [g for g in self.all_games if g.console == self.current_console]

        if self.only_favorites:
            favs = load_favorites()
            filtered = [g for g in filtered if g.folder_name in favs]

        if self.search_text:
            text = self.search_text.lower()
            filtered = [g for g in filtered if text in g.title.lower()]

        self.game_grid.set_games(filtered)
        self._update_fav_counter()

    def _update_fav_counter(self):
        favs = load_favorites()
        self.footer.right.setText(
            f"Игр: {len(self.all_games)} · ★: {len(favs)}"
        )

    def switch_console(self, console_key):
        if console_key == self.current_console and not self.is_recent_mode:
            return
        self.current_console = console_key
        
        for key, btn in self.toolbar.console_buttons.items():
            btn.setChecked(key == console_key)
            
        self.update_footer_links()
        self.refresh_grid()

    def update_footer_links(self):
        console_data = self.links_data.get(self.current_console, {})
        self.current_roms_url = console_data.get("roms", "")
        self.current_emu_url = console_data.get("emulator", "")
        
        self.footer.link_roms.setVisible(bool(self.current_roms_url))
        self.footer.link_emus.setVisible(bool(self.current_emu_url))

    def on_search(self, text):
        self.search_text = text.strip()
        if self.is_recent_mode and self.search_text:
            self.left_panel.nav_buttons["home"].setChecked(True)
            self.on_nav_clicked("home")
        self.refresh_grid()

    def _set_favorites_mode(self, enabled: bool):
        if self.only_favorites == enabled:
            return
        self.only_favorites = enabled
        self.left_panel.nav_buttons["favorite"].setChecked(enabled)
        if not enabled:
            self.left_panel.nav_buttons["home"].setChecked(True)
        self.refresh_grid()

    def on_nav_clicked(self, key):
        if key == "settings":
            self.on_nav_clicked("home")
            self.open_game_creator()
            return

        if key == "home":
            self._set_favorites_mode(False)
            self.toolbar.search.blockSignals(True)
            self.toolbar.search.clear()
            self.toolbar.search.blockSignals(False)
            self.search_text = ""
            self.current_console = "DENDY"
            for btn_key, btn in self.toolbar.console_buttons.items():
                btn.setChecked(btn_key == "DENDY")
            self.update_footer_links()
            self.refresh_grid()

        elif key == "favorite":
            self._set_favorites_mode(True)

        elif key == "recent":
            self.only_favorites = False
            self.toolbar.search.blockSignals(True)
            self.toolbar.search.clear()
            self.toolbar.search.blockSignals(False)
            self.search_text = ""
            for btn in self.toolbar.console_buttons.values():
                btn.setChecked(False)
            self.footer.link_roms.hide()
            self.footer.link_emus.hide()
            self._show_recent_games()

    def _show_recent_games(self):
        self.is_recent_mode = True
        history_entries = load_history()
        recent_games = []

        for entry in history_entries:
            folder = entry.get("folder_name")
            for game in self.all_games:
                if game.folder_name == folder:
                    recent_games.append(game)
                    break

        self.game_grid.setUpdatesEnabled(False)
        self.game_grid.set_games(recent_games)
        self.game_grid.setUpdatesEnabled(True)
        self._update_fav_counter()

    def open_game_creator(self):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        creator_exe = os.path.join(base_dir, "GameCreator.exe")
        
        if not os.path.exists(creator_exe):
            creator_exe = os.path.join(base_dir, "tools", "GameCreator.exe")

        if os.path.exists(creator_exe):
            try:
                subprocess.Popen([creator_exe], cwd=os.path.dirname(creator_exe))
                return
            except Exception as e:
                logger.error(f"Не удалось запустить конструктор: {e}")

        if not getattr(sys, 'frozen', False):
            creator_py = os.path.join(base_dir, "tools", "game_creator.py")
            if os.path.exists(creator_py):
                subprocess.Popen([sys.executable, creator_py])
                return

        QMessageBox.warning(self, "Ошибка", "Файл GameCreator.exe не найден!")

    def on_card_clicked(self, game):
        pass

    def on_card_double_clicked(self, game):
        launch_game(game, parent_window=self)

    def on_card_context_menu(self, game, global_pos):
        menu = QMenu(self)
        act_desc = menu.addAction("Описание")
        act_play = menu.addAction("Запустить")

        in_favs = game.folder_name in load_favorites()
        act_fav = menu.addAction(
            "Убрать из избранного" if in_favs else "В избранное"
        )

        chosen = menu.exec(global_pos)

        if chosen == act_desc:
            dlg = DescriptionWindow(game, parent=self)
            dlg.exec()
            if hasattr(dlg, "result_game") and dlg.result_game is not None:
                launch_game(dlg.result_game, parent_window=self)
        elif chosen == act_play:
            launch_game(game, parent_window=self)
        elif chosen == act_fav:
            toggle_favorite(game.folder_name)
            self._update_fav_counter()
            self.game_grid.refresh_favorites()
            if self.only_favorites:
                self.refresh_grid()

    def _apply_rounded_mask(self):
        path = QPainterPath()
        path.addRoundedRect(
            0, 0, self.width(), self.height(),
            self._corner_radius, self._corner_radius
        )
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.isMaximized():
            self._apply_rounded_mask()
        else:
            self.setMask(QRegion())

    def eventFilter(self, obj, event):
        if obj is self.title_bar and event.type() == event.Type.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                child = self.childAt(event.position().toPoint())
                if not isinstance(child, QPushButton):
                    self._start_drag()
                    return True
        return super().eventFilter(obj, event)

    def _start_drag(self):
        hwnd = int(self.winId())
        user32.ReleaseCapture()
        user32.SendMessageW(hwnd, WM_NCLBUTTONDOWN, HTCAPTION, 0)

    def _edge_at(self, pos):
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        m = RESIZE_MARGIN
        on_left   = x < m
        on_right  = x > w - m
        on_top    = y < m
        on_bottom = y > h - m
        if on_top and on_left:     return HTTOPLEFT
        if on_top and on_right:    return HTTOPRIGHT
        if on_bottom and on_left:  return HTBOTTOMLEFT
        if on_bottom and on_right: return HTBOTTOMRIGHT
        if on_left:                return HTLEFT
        if on_right:               return HTRIGHT
        if on_top:                 return HTTOP
        if on_bottom:              return HTBOTTOM
        return None

    def mouseMoveEvent(self, event):
        if self.isMaximized():
            self.setCursor(Qt.ArrowCursor)
            return
        in_zone = self._edge_at(event.position().toPoint()) is not None
        self.setCursor(Qt.SizeAllCursor if in_zone else Qt.ArrowCursor)
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if self.isMaximized():
            return
        if event.button() == Qt.LeftButton:
            edge = self._edge_at(event.position().toPoint())
            if edge is not None:
                hwnd = int(self.winId())
                user32.ReleaseCapture()
                user32.SendMessageW(hwnd, WM_NCLBUTTONDOWN, edge, 0)
                return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)

    def _toggle_max(self):
        if self.isMaximized():
            self.showNormal()
            QTimer.singleShot(10, self._apply_rounded_mask)
        else:
            self.setMask(QRegion())
            self.showMaximized()

# ----------------------------------------------------------------------
# Точка входа
# ----------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)

    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "launcher_icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()