# ui/neon_icons.py — Векторные неоновые иконки на QPainter
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath
from PySide6.QtCore import Qt, QRectF, QPointF

class NeonIcon(QWidget):
    def __init__(self, icon_type: str, color: str = "#c77dff", parent=None):
        super().__init__(parent)
        self.icon_type = icon_type
        self.color = QColor(color)
        self.setFixedSize(32, 32) # Размер иконки
        self.setAttribute(Qt.WA_TransparentForMouseEvents) # Чтобы клики проходили сквозь иконку на кнопку

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Настройки пера (толщина и цвет)
        pen = QPen(self.color, 2.5)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        # Масштабируем под размер виджета
        w = self.width()
        h = self.height()
        painter.scale(w / 32.0, h / 32.0)

        # Отрисовка в зависимости от типа
        if self.icon_type == "home":
            path = QPainterPath()
            path.moveTo(16, 4)    # Крыша верх
            path.lineTo(28, 16)   # Правый скат
            path.lineTo(24, 16)   # Спуск вправо
            path.lineTo(24, 28)   # Правая стена
            path.lineTo(8, 28)    # Левая стена
            path.lineTo(8, 16)    # Спуск влево
            path.lineTo(4, 16)    # Левый скат
            path.closeSubpath()
            painter.drawPath(path)

        elif self.icon_type == "star":
            path = QPainterPath()
            # Рисуем 4-конечную звезду (как в референсе)
            path.moveTo(16, 4)
            path.quadTo(16, 16, 28, 16)
            path.quadTo(16, 16, 16, 28)
            path.quadTo(16, 16, 4, 16)
            path.quadTo(16, 16, 16, 4)
            painter.drawPath(path)

        elif self.icon_type == "recent":
            # Циферблат
            painter.drawEllipse(QRectF(4, 4, 24, 24))
            # Стрелки
            painter.drawLine(QPointF(16, 16), QPointF(16, 8))
            painter.drawLine(QPointF(16, 16), QPointF(22, 16))

        elif self.icon_type == "add":
            # Квадрат со скруглением
            painter.drawRoundedRect(QRectF(4, 4, 24, 24), 6, 6)
            # Плюс
            painter.drawLine(QPointF(16, 10), QPointF(16, 22))
            painter.drawLine(QPointF(10, 16), QPointF(22, 16))

        elif self.icon_type == "gamepad":
            # Основа геймпада
            path = QPainterPath()
            path.moveTo(10, 10)
            path.lineTo(22, 10)
            path.quadTo(28, 10, 28, 18)
            path.quadTo(28, 26, 22, 26)
            path.lineTo(10, 26)
            path.quadTo(4, 26, 4, 18)
            path.quadTo(4, 10, 10, 10)
            painter.drawPath(path)
            # D-pad (крестовина)
            painter.drawLine(QPointF(9, 15), QPointF(9, 19))
            painter.drawLine(QPointF(7, 17), QPointF(11, 17))
            # Кнопки
            painter.drawEllipse(QPointF(22, 16), 1.5, 1.5)
            painter.drawEllipse(QPointF(24, 18), 1.5, 1.5)

        elif self.icon_type == "dendy": # Заглушка под консоль
            painter.drawRect(QRectF(6, 8, 20, 16))
            painter.drawLine(QPointF(10, 14), QPointF(22, 14))
            painter.drawLine(QPointF(10, 18), QPointF(18, 18))
            
        elif self.icon_type == "sega":
            painter.drawEllipse(QRectF(8, 8, 16, 16))
            painter.drawLine(QPointF(16, 8), QPointF(16, 24))

        elif self.icon_type == "sony":
            painter.drawRoundedRect(QRectF(6, 8, 20, 16), 4, 4)
            painter.drawPoint(QPointF(12, 16))
            painter.drawPoint(QPointF(20, 16))

        painter.end()