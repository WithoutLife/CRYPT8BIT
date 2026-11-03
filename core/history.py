# core/history.py — история запусков (JSON)
import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

MAX_ENTRIES = 20


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_history() -> list:
    """Возвращает список словарей {folder_name, console, timestamp}, свежие сверху."""
    _ensure_dir()
    if not os.path.isfile(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            logger.warning("history.json — не список, игнорируем")
            return []
        # Чистим дубликаты по folder_name, оставляя первое (свежее) вхождение
        seen = set()
        cleaned = []
        for entry in data:
            folder = entry.get("folder_name")
            if not folder or folder in seen:
                continue
            seen.add(folder)
            cleaned.append(entry)
        return cleaned
    except Exception as e:
        logger.error(f"Ошибка чтения history.json: {e}")
        return []


def save_history(entries: list):
    _ensure_dir()
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(entries[:MAX_ENTRIES], f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка записи history.json: {e}")


def add_to_history(folder_name: str, console: str):
    """Добавляет игру в начало истории. Если уже была — поднимает наверх."""
    entries = load_history()
    entries = [e for e in entries if e.get("folder_name") != folder_name]
    entries.insert(0, {
        "folder_name": folder_name,
        "console": console,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    })
    save_history(entries)