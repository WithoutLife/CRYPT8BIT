# core/scanner.py — сканирование папок с играми
import os
import sys
import logging
from typing import List
from core.game import Game

logger = logging.getLogger(__name__)

if getattr(sys, 'frozen', False):
    GAMES_ROOT = os.path.dirname(sys.executable)
else:
    GAMES_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONSOLES = ["Dendy", "Sega", "Sony"]
CONSOLE_KEY_MAP = {"Dendy": "DENDY", "Sega": "SEGA", "Sony": "SONY"}

# Добавили .gif и .webp
SCREENSHOT_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp")

def scan_all_games() -> List[Game]:
    all_games = []
    for folder_name in CONSOLES:
        console_key = CONSOLE_KEY_MAP.get(folder_name, folder_name.upper())
        console_path = os.path.join(GAMES_ROOT, folder_name)
        if not os.path.isdir(console_path):
            continue
        games = _scan_console(console_path, console_key)
        logger.info(f"Консоль {console_key}: найдено {len(games)} игр")
        all_games.extend(games)
    logger.info(f"Всего игр: {len(all_games)}")
    return all_games

def _scan_console(console_path: str, console_key: str) -> List[Game]:
    games = []
    try:
        entries = sorted(os.listdir(console_path))
    except OSError:
        return games

    for entry in entries:
        game_path = os.path.join(console_path, entry)
        if not os.path.isdir(game_path) or entry.startswith(".") or entry.startswith("_"):
            continue
        game = _scan_one_game(game_path, entry, console_key)
        if game is not None:
            games.append(game)
    return games

def _scan_one_game(game_path: str, folder_name: str, console_key: str) -> Game:
    game = Game(title=folder_name, folder_name=folder_name, folder_path=game_path, console=console_key)

    images_dir = os.path.join(game_path, "images")
    if os.path.isdir(images_dir):
        cartridge = os.path.join(images_dir, "cartridge.png")
        if os.path.isfile(cartridge):
            game.cartridge_path = cartridge

        # Ищем скриншоты (1.png, 1.gif, 2.jpg и т.д.)
        for i in range(1, 11):
            for ext in SCREENSHOT_EXTS:
                shot = os.path.join(images_dir, f"{i}{ext}")
                if os.path.isfile(shot):
                    game.screenshots.append(shot)
                    break

    rom_dir = os.path.join(game_path, "rom")
    if os.path.isdir(rom_dir):
        try:
            for f in os.listdir(rom_dir):
                full = os.path.join(rom_dir, f)
                if os.path.isfile(full) and f.lower() not in ("desktop.ini", "thumbs.db"):
                    game.rom_path = full
                    break
        except OSError as e:
            logger.error(f"Не удалось прочитать {rom_dir}: {e}")

    if game.rom_path is None:
        logger.warning(f"Игра '{folder_name}' пропущена: папка rom пуста.")
        return None

    html = os.path.join(game_path, "index.html")
    if os.path.isfile(html):
        game.html_path = html

    return game