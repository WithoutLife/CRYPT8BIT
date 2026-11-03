# tools/game_creator.py — Полноценный конструктор игр для CRYPT8BIT
# Запуск: py -3.12 tools/game_creator.py

import sys
import os
import shutil
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QFileDialog, QMessageBox,
    QGroupBox, QFormLayout, QComboBox, QListWidget, QScrollArea
)
from PySide6.QtCore import Qt

# --- Шаблон HTML ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1c1c1c;
            color: #EAEAEA;
            margin: 20px;
            font-size: 11.5pt;
        }}
        h1 {{ color: #00FFFF; font-size: 24pt; margin-top: 0; text-shadow: 0 0 5px rgba(0, 255, 255, 0.5); text-align: center; }}
        h2 {{ color: #FF8C00; font-size: 16pt; border-bottom: 2px solid #555; padding-bottom: 5px; margin-top: 30px; }}
        p {{ line-height: 1.6; text-align: justify; }}
        .details-box ul {{ list-style-type: none; padding-left: 0; margin: 0; }}
        .details-box li {{ padding: 3px 0; }}
        div.details-box {{ background-color: #2a2a2a; padding: 15px; border-left: 5px solid #00FFFF; border-radius: 8px; margin-bottom: 25px; }}
        .details-box b {{ color: #FFFF00; display: inline-block; min-width: 140px; }}
        .image-gallery {{ margin-top: 20px; }}
    </style>
    <title>{title}</title>
</head>
<body>

    <h1 style="text-align: center;">{title}</h1>

    <div class="details-box">
        <ul>
            <li><b>Разработчик:</b> {developer}</li>
            <li><b>Издатель:</b> {publisher}</li>
            <li><b>Дата выхода:</b> {release_date}</li>
            <li><b>Количество игроков:</b> {players}</li>
            <li><b>Доп. детали:</b> {genre}</li>
            <li><b>Основано на:</b> {based_on}</li>
        </ul>
    </div>

    <h2>Об игре</h2>
    <p>{about_game}</p>
    
    <h2>Геймплей и Механика</h2>
    <p>{gameplay}</p>
    
    <h2>🎧 Музыка и Графика</h2>
    <p>{music_graphics}</p>
    
    <h2>📜 Разработка и Контекст</h2>
    <p>{development}</p>

    <h2>Интересные факты</h2>
    <p>{legacy}</p>
    
    <hr style="border-top: 1px solid #FF8C00; margin: 30px 0;">

    <h2>Секреты и Коды</h2>
    <p>{secrets}</p>
    
    <div class="image-gallery"></div>

</body>
</html>
"""

class GameCreator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CRYPT8BIT — Конструктор игр")
        self.resize(900, 750) # Стартовый размер под ноутбуки
        
        # НОВЫЙ СТИЛЬ (Synthwave)
        self.setStyleSheet("""
            QWidget { 
                background-color: #0a0612; 
                color: #f2ebff; 
                font-family: 'Segoe UI'; 
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #3d2666;
                border-radius: 4px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background: #d966ff;
            }
            QLineEdit, QTextEdit, QComboBox, QListWidget { 
                background-color: #1a1028; 
                border: 1px solid #3d2666; 
                border-radius: 6px; 
                padding: 8px; 
                color: #f2ebff; 
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus { 
                border: 1px solid #d966ff; 
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1028;
                color: #f2ebff;
                selection-background-color: #d966ff;
            }
            QPushButton { 
                background-color: #d966ff; 
                color: #0a0612; 
                border: none; 
                padding: 10px; 
                border-radius: 6px; 
                font-weight: bold; 
                font-size: 11pt;
            }
            QPushButton:hover { 
                background-color: #e699ff; 
            }
            QPushButton#secondary { 
                background-color: #1a1028; 
                color: #f2ebff; 
                border: 1px solid #3d2666;
            }
            QPushButton#secondary:hover { 
                background-color: #2a1b40; 
                border: 1px solid #d966ff;
            }
            QGroupBox { 
                border: 1px solid #3d2666; 
                border-radius: 8px; 
                margin-top: 15px; 
                padding-top: 20px; 
                font-weight: bold; 
                color: #d966ff; 
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 15px; 
                padding: 0 5px; 
            }
            QLabel {
                color: #9d85c7;
                font-weight: bold;
            }
        """)

        # Главный слой окна
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)

        # Создаем прокручиваемую область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        window_layout.addWidget(scroll)

        # Внутренний контент (все поля)
        content_widget = QWidget()
        scroll.setWidget(content_widget)

        main_layout = QVBoxLayout(content_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # --- Выбор консоли ---
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Консоль:"))
        self.console_combo = QComboBox()
        self.console_combo.addItems(["Dendy", "Sega", "Sony"])
        top_layout.addWidget(self.console_combo)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        # --- Основная информация ---
        info_group = QGroupBox("Основная информация")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(8)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Название игры (папка создастся с этим именем) *")
        self.developer_input = QLineEdit()
        self.developer_input.setPlaceholderText("Разработчик (например: Ocean Software)")
        self.publisher_input = QLineEdit()
        self.publisher_input.setPlaceholderText("Издатель (например: Flying Edge)")
        self.release_input = QLineEdit()
        self.release_input.setPlaceholderText("Дата выхода (например: 1993)")
        self.players_input = QLineEdit()
        self.players_input.setPlaceholderText("Кол-во игроков (например: 1-2 игрока)")
        self.genre_input = QLineEdit()
        self.genre_input.setPlaceholderText("Жанр (например: Экшен-платформер)")
        self.based_on_input = QLineEdit()
        self.based_on_input.setPlaceholderText("Основано на (например: Фильме «Семейка Аддамс», 1991)")

        info_layout.addRow("Название игры *:", self.title_input)
        info_layout.addRow("Разработчик:", self.developer_input)
        info_layout.addRow("Издатель:", self.publisher_input)
        info_layout.addRow("Дата выхода:", self.release_input)
        info_layout.addRow("Игроков:", self.players_input)
        info_layout.addRow("Жанр:", self.genre_input)
        info_layout.addRow("Основано на:", self.based_on_input)
        main_layout.addWidget(info_group)

        # --- Файлы (РОМ, обложка, скриншоты) ---
        files_group = QGroupBox("Файлы игры (Обязательно: РОМ и Обложка)")
        files_layout = QVBoxLayout(files_group)

        # ROM
        rom_layout = QHBoxLayout()
        self.rom_path_input = QLineEdit()
        self.rom_path_input.setPlaceholderText("Путь к архиву/РОМу... *")
        self.rom_path_input.setReadOnly(True)
        btn_rom = QPushButton("Выбрать РОМ")
        btn_rom.setObjectName("secondary")
        btn_rom.clicked.connect(self.select_rom)
        rom_layout.addWidget(self.rom_path_input)
        rom_layout.addWidget(btn_rom)
        files_layout.addWidget(QLabel("РОМ-файл *:"))
        files_layout.addLayout(rom_layout)

        # Обложка
        cover_layout = QHBoxLayout()
        self.cover_path_input = QLineEdit()
        self.cover_path_input.setPlaceholderText("Выберите любой файл обложки (скрипт сам переименует)... *")
        self.cover_path_input.setReadOnly(True)
        btn_cover = QPushButton("Выбрать файл обложки")
        btn_cover.setObjectName("secondary")
        btn_cover.clicked.connect(self.select_cover)
        cover_layout.addWidget(self.cover_path_input)
        cover_layout.addWidget(btn_cover)
        files_layout.addWidget(QLabel("Файл обложки *:"))
        files_layout.addLayout(cover_layout)

        # Скриншоты
        screens_layout = QVBoxLayout()
        btn_screens = QPushButton("Добавить скриншоты (можно несколько)")
        btn_screens.setObjectName("secondary")
        btn_screens.clicked.connect(self.select_screenshots)
        self.screens_list = QListWidget()
        self.screens_list.setFixedHeight(80)
        screens_layout.addWidget(QLabel("Скриншоты (будут пронумерованы 1, 2, 3...):"))
        screens_layout.addWidget(btn_screens)
        screens_layout.addWidget(self.screens_list)
        files_layout.addLayout(screens_layout)

        main_layout.addWidget(files_group)

        # --- Описания ---
        text_group = QGroupBox("Описания (все поля опциональны)")
        text_layout = QVBoxLayout(text_group)
        
        self.about_input = QTextEdit()
        self.about_input.setPlaceholderText("Об игре: краткий сюжет, кто главный герой, что происходит...")
        self.about_input.setFixedHeight(60)
        
        self.gameplay_input = QTextEdit()
        self.gameplay_input.setPlaceholderText("Геймплей: как играется, какие механики, цели, особенности управления...")
        self.gameplay_input.setFixedHeight(60)
        
        self.music_input = QTextEdit()
        self.music_input.setPlaceholderText("Музыка и графика: визуальный стиль, композитор, атмосфера...")
        self.music_input.setFixedHeight(60)
        
        self.dev_input = QTextEdit()
        self.dev_input.setPlaceholderText("Разработка: кто делал, на чем основано, интересные моменты создания...")
        self.dev_input.setFixedHeight(60)
        
        self.legacy_input = QTextEdit()
        self.legacy_input.setPlaceholderText("Интересные факты: награды, культовый статус, отсылки, необычные детали...")
        self.legacy_input.setFixedHeight(60)
        
        self.secrets_input = QTextEdit()
        self.secrets_input.setPlaceholderText("Секреты и коды: читы, пароли, Game Genie, скрытые уровни...")
        self.secrets_input.setFixedHeight(60)

        text_layout.addWidget(QLabel("Об игре:"))
        text_layout.addWidget(self.about_input)
        text_layout.addWidget(QLabel("Геймплей и механика:"))
        text_layout.addWidget(self.gameplay_input)
        text_layout.addWidget(QLabel("Музыка и графика:"))
        text_layout.addWidget(self.music_input)
        text_layout.addWidget(QLabel("Разработка:"))
        text_layout.addWidget(self.dev_input)
        text_layout.addWidget(QLabel("Интересные факты:"))
        text_layout.addWidget(self.legacy_input)
        text_layout.addWidget(QLabel("Секреты и коды:"))
        text_layout.addWidget(self.secrets_input)

        main_layout.addWidget(text_group)

        # --- Кнопка создания ---
        self.btn_create = QPushButton("🚀 Создать игру (папка + файлы + HTML)")
        self.btn_create.clicked.connect(self.generate_game)
        main_layout.addWidget(self.btn_create)

    def select_rom(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выбери РОМ", "", "Все файлы (*.*)")
        if path:
            self.rom_path_input.setText(path)

    def select_cover(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выбери обложку", "", "Изображения (*.png *.jpg *.jpeg)")
        if path:
            self.cover_path_input.setText(path)

    def select_screenshots(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Выбери скриншоты", "", "Изображения (*.png *.jpg *.jpeg)")
        if paths:
            self.screens_list.addItems(paths)

    def generate_game(self):
        # --- ПРОВЕРКА ОБЯЗАТЕЛЬНЫХ ПОЛЕЙ ---
        title = self.title_input.text().strip()
        rom_src = self.rom_path_input.text().strip()
        cover_src = self.cover_path_input.text().strip()

        if not title:
            QMessageBox.warning(self, "Ошибка", "Введите название игры! Без него нельзя создать папку.")
            return
        if not rom_src or not os.path.isfile(rom_src):
            QMessageBox.warning(self, "Ошибка", "Выберите РОМ-файл! Без него игра не запустится.")
            return
        if not cover_src or not os.path.isfile(cover_src):
            QMessageBox.warning(self, "Ошибка", "Выберите файл обложки! Без неё карточка в лаунчере будет пустой.")
            return

        console = self.console_combo.currentText()
        
        # Где будет папка игры (рядом с main.py)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        console_dir = os.path.join(project_root, console)
        game_dir = os.path.join(console_dir, title)

        # Проверка на существование
        if os.path.exists(game_dir):
            reply = QMessageBox.question(self, "Папка существует", f"Папка '{title}' уже есть. Перезаписать?")
            if reply != QMessageBox.Yes:
                return

        try:
            # Создаём структуру папок
            images_dir = os.path.join(game_dir, "images")
            rom_dir = os.path.join(game_dir, "rom")
            os.makedirs(images_dir, exist_ok=True)
            os.makedirs(rom_dir, exist_ok=True)

            # Копируем РОМ
            rom_filename = os.path.basename(rom_src)
            shutil.copy2(rom_src, os.path.join(rom_dir, rom_filename))

            # Копируем обложку (всегда переименовываем в cartridge.png)
            shutil.copy2(cover_src, os.path.join(images_dir, "cartridge.png"))

            # Копируем скриншоты (нумеруем 1, 2, 3...)
            for i in range(self.screens_list.count()):
                screenshot_path = self.screens_list.item(i).text()
                if os.path.isfile(screenshot_path):
                    ext = os.path.splitext(screenshot_path)[1]
                    dst_path = os.path.join(images_dir, f"{i+1}{ext}")
                    shutil.copy2(screenshot_path, dst_path)

            # Генерируем HTML
            data = {
                "title": title,
                "developer": self.developer_input.text().strip() or "Неизвестно",
                "publisher": self.publisher_input.text().strip() or "Неизвестно",
                "release_date": self.release_input.text().strip() or "Неизвестно",
                "players": self.players_input.text().strip() or "Неизвестно",
                "genre": self.genre_input.text().strip() or "Неизвестно",
                "based_on": self.based_on_input.text().strip() or "Неизвестно",
                "about_game": self.about_input.toPlainText().strip() or "Описание отсутствует.",
                "gameplay": self.gameplay_input.toPlainText().strip() or "Информация отсутствует.",
                "music_graphics": self.music_input.toPlainText().strip() or "Информация отсутствует.",
                "development": self.dev_input.toPlainText().strip() or "Информация отсутствует.",
                "legacy": self.legacy_input.toPlainText().strip() or "Информация отсутствует.",
                "secrets": self.secrets_input.toPlainText().strip() or "Секреты не найдены.",
            }
            html_content = HTML_TEMPLATE.format(**data)

            with open(os.path.join(game_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(html_content)

            QMessageBox.information(self, "Готово", f"Игра создана в:\n{game_dir}\n\nПерезапусти лаунчер, чтобы увидеть её.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать игру:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameCreator()
    window.show()
    sys.exit(app.exec())