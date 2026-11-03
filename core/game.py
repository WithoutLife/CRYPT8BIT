# core/game.py — модель одной игры
# Хранит все данные, которые нужны UI для отображения карточки.

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Game:
    """Одна игра. Лёгкий объект — только пути и метаданные."""
    
    # Основное
    title: str                          # Название (из имени папки)
    folder_name: str                    # Имя папки игры
    folder_path: str                    # Полный путь к папке игры
    console: str                        # "DENDY", "SEGA", "SONY"
    
    # Ресурсы
    cartridge_path: Optional[str] = None   # Путь к images/cartridge.png
    rom_path: Optional[str] = None         # Путь к rom/<файл>
    html_path: Optional[str] = None        # Путь к index.html
    screenshots: list = field(default_factory=list)  # Список путей к скриншотам
    
    # Для будущего (избранное, недавние, счётчики)
    favorite: bool = False
    play_count: int = 0
    last_played: Optional[str] = None
    
    @property
    def has_cartridge(self) -> bool:
        """Есть ли у игры обложка."""
        return self.cartridge_path is not None
    
    @property
    def has_description(self) -> bool:
        """Есть ли у игры HTML-описание."""
        return self.html_path is not None