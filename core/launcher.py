# core/launcher.py — запуск эмуляторов
# Сворачивает окно CRYPT8BIT, запускает нужный эмулятор с ROM'ом,
# ждёт закрытия эмулятора, возвращает окно обратно.

import os
import sys
import subprocess
import logging
import time
from core.history import add_to_history

logger = logging.getLogger(__name__)

# Определяем, откуда мы запущены (из Python или из скомпилированного .exe)
if getattr(sys, 'frozen', False):
    PROJECT_ROOT = os.path.dirname(sys.executable)
else:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EMULATOR_ROOT = os.path.join(PROJECT_ROOT, "Emulator")

# Маппинг: консоль -> (путь к exe, список флагов для фуллскрина)
EMULATORS = {
    "DENDY": {
        "exe": os.path.join(EMULATOR_ROOT, "nestopia", "nestopia.exe"),
        "fullscreen_flag": [],
    },
    "SEGA": {
        "exe": os.path.join(EMULATOR_ROOT, "Gens32", "Gens32Surreal.exe"),
        "fullscreen_flag": [],
    },
    "SONY": {
        "exe": os.path.join(EMULATOR_ROOT, "DuckStation", "duckstation-qt-x64-ReleaseLTCG.exe"),
        "fullscreen_flag": ["-fullscreen"],
    },
}

def find_rom_in_folder(folder_path):
    """Ищет любой ROM-файл в папке (игнорируя мусор)"""
    if not os.path.isdir(folder_path):
        return None
        
    # Приоритет: .cue > .chd > .pbp > .iso > .gen > .smd > .md > .32x > .nes > .fds > .unf > .bin > .zip
    # Но так как нам нужно просто взять то, что есть, мы берем первый попавшийся файл с известным расширением
    # или вообще любой файл, если он не системный.
    
    rom_exts = (".cue", ".chd", ".pbp", ".iso", ".gen", ".smd", ".md", ".32x", 
                ".nes", ".fds", ".unf", ".bin", ".zip", ".rar", ".7z")
    
    try:
        for f in os.listdir(folder_path):
            full_path = os.path.join(folder_path, f)
            if os.path.isfile(full_path) and not f.lower() in ("desktop.ini", "thumbs.db"):
                # Если расширение в списке (или его нет), возвращаем
                if f.lower().endswith(rom_exts) or "." not in f:
                    return full_path
                    
        # Если ничего не нашли по расширению, берем первый попавшийся файл
        for f in os.listdir(folder_path):
            full_path = os.path.join(folder_path, f)
            if os.path.isfile(full_path) and not f.lower() in ("desktop.ini", "thumbs.db"):
                return full_path
                
    except OSError as e:
        logger.error(f"Ошибка чтения папки {folder_path}: {e}")
        
    return None

def launch_game(game, parent_window=None):
    """
    Запускает игру.
    
    game — объект Game (из core.game)
    parent_window — окно CRYPT8BIT, которое надо свернуть на время игры.
                    Если None — окно не трогаем.
    """
    
    # 1. Проверяем, есть ли уже путь к рому
    rom_path = None
    if game.rom_path and os.path.isfile(game.rom_path):
        rom_path = game.rom_path
    else:
        # 2. Если нет или файл пропал, ищем его в папке rom
        rom_dir = os.path.join(game.folder_path, "rom")
        rom_path = find_rom_in_folder(rom_dir)
        
        # 3. Если в папке rom пусто, ищем в корне игры (на случай старых сборок)
        if not rom_path:
            rom_path = find_rom_in_folder(game.folder_path)

    if not rom_path:
        logger.warning(f"У игры {game.title} нет ROM-файла, запуск отменён")
        return False

    if not os.path.isfile(rom_path):
        logger.error(f"ROM не найден: {rom_path}")
        return False

    emu = EMULATORS.get(game.console)
    if emu is None:
        logger.error(f"Нет эмулятора для консоли {game.console}")
        return False

    exe_path = emu["exe"]
    if not os.path.isfile(exe_path):
        logger.error(f"Эмулятор не найден: {exe_path}")
        return False

    # Собираем команду: exe + флаги фуллскрина + путь к ROM
    cmd = [exe_path] + emu["fullscreen_flag"] + [rom_path]
    logger.info(f"Запуск: {' '.join(cmd)}")

    # Сворачиваем своё окно, чтобы эмулятор вышел на передний план
    if parent_window is not None:
        parent_window.showMinimized()

    try:
        # Запускаем эмулятор и ждём его закрытия
        proc = subprocess.Popen(cmd, cwd=os.path.dirname(exe_path))
        # Пишем в историю сразу после старта — на случай, если эмулятор упадёт
        add_to_history(game.folder_name, game.console)
        proc.wait()
    except Exception as e:
        logger.error(f"Ошибка запуска эмулятора: {e}")
        if parent_window is not None:
            parent_window.showNormal()
        return False

    # Небольшая пауза, чтобы окно эмулятора успело закрыться
    time.sleep(0.3)

    # Возвращаем своё окно
    if parent_window is not None:
        parent_window.showNormal()
        parent_window.activateWindow()

    return True