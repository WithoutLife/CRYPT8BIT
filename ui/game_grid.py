# ui/game_grid.py — сетка карточек (QScrollArea + QGridLayout)

from PySide6.QtWidgets import (
    QScrollArea, QWidget, QGridLayout, QVBoxLayout, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from ui.game_card import GameCard

class GameGrid(QScrollArea):
    card_clicked = Signal(object)
    card_double_clicked = Signal(object)
    card_context_menu = Signal(object, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("gameScrollArea")
        self.setWidgetResizable(True) # Позволяет виджету менять размер под область
        self.setFrameShape(QScrollArea.NoFrame)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.grid_widget = QWidget()
        self.grid_widget.setObjectName("gridWidget")
        
        # ВАЖНО: Говорим виджету растягиваться по ширине
        self.grid_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.grid = QGridLayout(self.grid_widget)
        self.grid.setContentsMargins(24, 10, 24, 24) 
        self.grid.setSpacing(16)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.setWidget(self.grid_widget)

        self.cards = []
        self._num_cols = 0
        self._games = []

        # Отслеживаем изменение размера
        self.resizeEvent = self._on_resize

    def set_games(self, games):
        self._games = games
        self._rebuild()

    def _on_resize(self, event):
        super().resizeEvent(event)
        
        # Считаем доступную ширину (вычитаем отступы 24 слева и 24 справа)
        available_width = self.viewport().width() - 48
        card_width = 180
        spacing = 16
        
        # Вычисляем количество колонок
        new_cols = max(1, (available_width + spacing) // (card_width + spacing))

        if new_cols != self._num_cols:
            self._num_cols = new_cols
            self._rebuild()

    def _rebuild(self):
        # Очищаем старые виджеты
        for i in reversed(range(self.grid.count())):
            item = self.grid.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        self.cards.clear()

        if not self._games:
            return

        # Создаем новые карточки
        for game in self._games:
            card = GameCard(game)
            card.clicked.connect(self._on_card_clicked)
            card.double_clicked.connect(self._on_card_double_clicked)
            card.context_menu_requested.connect(self._on_card_context_menu)
            self.cards.append(card)

        # Раскладываем
        for i, card in enumerate(self.cards):
            row = i // self._num_cols
            col = i % self._num_cols
            self.grid.addWidget(card, row, col)

        # Добавляем "распорку" справа, чтобы сетка прижималась влево
        self.grid.setColumnStretch(self._num_cols, 1)

    def _on_card_clicked(self, game):
        for card in self.cards:
            card.set_selected(card.game == game)
        self.card_clicked.emit(game)

    def _on_card_double_clicked(self, game):
        self.card_double_clicked.emit(game)

    def _on_card_context_menu(self, game, pos):
        self.card_context_menu.emit(game, pos)

    def refresh_favorites(self):
        for card in self.cards:
            card.reload_favorite()