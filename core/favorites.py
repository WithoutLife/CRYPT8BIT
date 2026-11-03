# core/favorites.py — избранное (JSON-хранилище)
import os
import json
import logging

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
FAVORITES_FILE = os.path.join(DATA_DIR, "favorites.json")


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_favorites() -> set:
    """Возвращает set folder_name избранных игр."""
    _ensure_dir()
    if not os.path.isfile(FAVORITES_FILE):
        return set()
    try:
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return set(data)
        logger.warning("favorites.json — не список, игнорируем")
        return set()
    except Exception as e:
        logger.error(f"Ошибка чтения favorites.json: {e}")
        return set()


def save_favorites(fav_set: set):
    """Сохраняет set folder_name в JSON."""
    _ensure_dir()
    try:
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(fav_set), f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка записи favorites.json: {e}")


def toggle_favorite(folder_name: str) -> bool:
    """Переключает избранное. Возвращает True, если теперь в избранном."""
    favs = load_favorites()
    if folder_name in favs:
        favs.discard(folder_name)
        result = False
    else:
        favs.add(folder_name)
        result = True
    save_favorites(favs)
    return result


def is_favorite(folder_name: str) -> bool:
    return folder_name in load_favorites()