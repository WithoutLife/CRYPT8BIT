# ui/neon_icons.py — Векторные неоновые иконки на QPainter
import os
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QPixmap
from PySide6.QtCore import Qt, QRectF, QPointF

class NeonIcon(QWidget):
    def __init__(self, icon_type: str, color: str = "#c77dff", parent=None):
        super().__init__(parent)
        self.icon_type = icon_type
        self.color = QColor(color)
        self.setFixedSize(32, 32)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        
        # Проверяем, есть ли готовая картинка в assets
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.custom_pixmap = None
        
        # Если это кнопка "Добавить игру", ищем картинку icon_add.png
        if self.icon_type == "add":
            icon_path = os.path.join(self.base_dir, "assets", "icon_add.png")
            if os.path.exists(icon_path):
                self.custom_pixmap = QPixmap(icon_path)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Если есть кастомная картинка — рисуем её
        if self.custom_pixmap and not self.custom_pixmap.isNull():
            # Масштабируем под размер виджета
            scaled = self.custom_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            painter.end()
            return

        # --- Если картинки нет, рисуем старым способом ---
        pen = QPen(self.color, 2.5)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        w = self.width()
        h = self.height()
        painter.scale(w / 32.0, h / 32.0)

        if self.icon_type == "home":
            path = QPainterPath()
            path.moveTo(16, 4)
            path.lineTo(28, 16)
            path.lineTo(24, 16)
            path.lineTo(24, 28)
            path.lineTo(8, 28)
            path.lineTo(8, 16)
            path.lineTo(4, 16)
            path.closeSubpath()
            painter.drawPath(path)

        elif self.icon_type == "star":
            path = QPainterPath()
            path.moveTo(16, 4)
            path.quadTo(16, 16, 28, 16)
            path.quadTo(16, 16, 16, 28)
            path.quadTo(16, 16, 4, 16)
            path.quadTo(16, 16, 16, 4)
            painter.drawPath(path)

        elif self.icon_type == "recent":
            painter.drawEllipse(QRectF(4, 4, 24, 24))
            painter.drawLine(QPointF(16, 16), QPointF(16, 8))
            painter.drawLine(QPointF(16, 16), QPointF(22, 16))

        elif self.icon_type == "add":
            painter.drawRoundedRect(QRectF(4, 4, 24, 24), 6, 6)
            painter.drawLine(QPointF(16, 10), QPointF(16, 22))
            painter.drawLine(QPointF(10, 16), QPointF(22, 16))

        painter.end()