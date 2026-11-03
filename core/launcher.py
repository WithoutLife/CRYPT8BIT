# core/launcher.py — запуск эмуляторов
# Сворачивает окно CRYPT8BIT, запускает нужный эмулятор с ROM'ом,
# ждёт закрытия эмулятора, возвращает окно обратно.

import os
import subprocess
import logging
import time
from core.history import add_to_history

logger = logging.getLogger(__name__)

# Корень проекта
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMULATOR_ROOT = os.path.join(PROJECT_ROOT, "Emulator")

# Маппинг: консоль -> (путь к exe относительно Emulator/, список флагов для фуллскрина)
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


def launch_game(game, parent_window=None):
    """
    Запускает игру.
    
    game — объект Game (из core.game)
    parent_window — окно CRYPT8BIT, которое надо свернуть на время игры.
                    Если None — окно не трогаем.
    """
    if game.rom_path is None:
        logger.warning(f"У игры {game.title} нет ROM-файла, запуск отменён")
        return False

    if not os.path.isfile(game.rom_path):
        logger.error(f"ROM не найден: {game.rom_path}")
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
    cmd = [exe_path] + emu["fullscreen_flag"] + [game.rom_path]
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