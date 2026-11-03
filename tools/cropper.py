# tools/cropper.py — Утилита для быстрой обрезки наклеек картриджей
import sys
import os
import glob
import shutil
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QRubberBand, QMessageBox
)
from PySide6.QtCore import Qt, QRect, QPoint, QSize
from PySide6.QtGui import QPixmap, QPainter, QColor

class ImageCropper(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CRYPT8BIT — Обрезка картриджей")
        self.resize(800, 600)
        self.setStyleSheet("""
            QWidget { background-color: #0a0612; color: #f2ebff; font-family: 'Segoe UI'; }
            QPushButton { background-color: #d966ff; color: #0a0612; border: none; padding: 10px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #e699ff; }
        """)

        # Ищем все файлы cartridge.png
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.pattern = os.path.join(base_dir, "*", "*", "images", "cartridge.png")
        self.files = glob.glob(self.pattern)
        
        if not self.files:
            QMessageBox.critical(self, "Ошибка", "Не найдено ни одного файла cartridge.png!")
            sys.exit(1)
            
        self.total = len(self.files)
        self.current_idx = 0

        # UI
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #d966ff;")
        self.layout.addWidget(self.info_label)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setStyleSheet("background-color: #1a1028; border: 1px solid #3d2666; border-radius: 8px;")
        self.layout.addWidget(self.image_label)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Сохранить (Enter)")
        self.btn_save.clicked.connect(self.save_crop)
        self.btn_skip = QPushButton("Пропустить (Пробел)")
        self.btn_skip.setObjectName("secondary")
        self.btn_skip.setStyleSheet("background-color: #3d2666; color: #f2ebff;")
        self.btn_skip.clicked.connect(self.next_image)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_skip)
        self.layout.addLayout(btn_layout)

        # Rubber Band для выделения
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self.image_label)
        self.origin = QPoint()
        self.current_rect = None
        
        self.image_label.mousePressEvent = self.mouse_press
        self.image_label.mouseMoveEvent = self.mouse_move
        self.image_label.mouseReleaseEvent = self.mouse_release

        self.load_image()

    def load_image(self):
        if self.current_idx >= self.total:
            QMessageBox.information(self, "Готово", "Все картриджи обработаны!")
            self.close()
            return

        self.current_file = self.files[self.current_idx]
        self.info_label.setText(f"[{self.current_idx + 1} / {self.total}] {self.current_file}")
        
        self.pixmap = QPixmap(self.current_file)
        self.update_image_display()

    def update_image_display(self):
        # Масштабируем картинку под лейбл
        scaled = self.pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled)
        self.offset_x = (self.image_label.width() - scaled.width()) // 2
        self.offset_y = (self.image_label.height() - scaled.height()) // 2
        self.scale_factor = self.pixmap.width() / scaled.width()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'pixmap'):
            self.update_image_display()

    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()

    def mouse_move(self, event):
        if self.rubber_band.isVisible():
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouse_release(self, event):
        if event.button() == Qt.LeftButton:
            self.rubber_band.hide()
            rect = QRect(self.origin, event.pos()).normalized()
            
            # Если рамка слишком маленькая, игнорируем
            if rect.width() < 10 or rect.height() < 10:
                return
                
            # Пересчитываем координаты на оригинальной картинке
            x = int((rect.x() - self.offset_x) * self.scale_factor)
            y = int((rect.y() - self.offset_y) * self.scale_factor)
            w = int(rect.width() * self.scale_factor)
            h = int(rect.height() * self.scale_factor)
            
            self.current_rect = (x, y, w, h)

    def save_crop(self):
        if not self.current_rect:
            QMessageBox.warning(self, "Ошибка", "Сначала выделите область мышкой!")
            return

        x, y, w, h = self.current_rect
        try:
            # Обрезаем оригинал
            cropped = self.pixmap.copy(x, y, w, h)
            
            # Создаем бэкап оригинала (если его еще нет)
            original_backup = os.path.join(os.path.dirname(self.current_file), "cartridge_original.png")
            if not os.path.exists(original_backup):
                shutil.copy2(self.current_file, original_backup)

            # Сохраняем обрезанный
            cropped.save(self.current_file, "PNG")
            
            # Переход к следующему
            self.current_rect = None
            self.next_image()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{e}")

    def next_image(self):
        self.current_idx += 1
        self.current_rect = None
        self.load_image()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.save_crop()
        elif event.key() == Qt.Key_Space:
            self.next_image()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageCropper()
    window.show()
    sys.exit(app.exec())