# tools/parser.py — Умный конвертер для CRYPT8BIT
import os
import shutil
import re
from PIL import Image

# --- НАСТРОЙКИ ---
NES_H_DIR = r"E:\Игры\nesh"
OUTPUT_DIR = os.path.join(NES_H_DIR, "rom")
MEDIA_DIR = os.path.join(NES_H_DIR, "media")

processed_games = set()

def clean_name(filename):
    """Убирает расширение и квадратные скобки, оставляя полное название"""
    name = os.path.splitext(filename)[0]
    # Убираем все квадратные скобки и их содержимое: [T+Rus...] -> ""
    name = re.sub(r'\[.*?\]', '', name)
    # Убираем круглые скобки (регион, год): (U), (1990) -> ""
    name = re.sub(r'\(.*?\)', '', name)
    # Убираем хвосты типа _2, _3 в конце
    name = re.sub(r'_\d+$', '', name)
    # Убираем лишние пробелы и дефисы на концах
    return name.strip(" -_")

def get_media_file(media_subfolder, base_name, ext_filter=None):
    """Ищет файл в папке media с нужным именем и расширением"""
    folder_path = os.path.join(MEDIA_DIR, media_subfolder)
    if not os.path.isdir(folder_path):
        return None
    
    for f in os.listdir(folder_path):
        if ext_filter and not f.lower().endswith(ext_filter):
            continue
        if f.startswith(base_name):
            return os.path.join(folder_path, f)
    return None

def is_valid_screenshot(filepath):
    """Проверяет картинку по размеру и пропорциям"""
    try:
        with Image.open(filepath) as img:
            width, height = img.size
            
            # 1. Минимальный размер (отсеиваем иконки и мелкие логотипы)
            if width < 300 or height < 300:
                return False
            
            # 2. Соотношение сторон (отсеиваем полоски и баннеры)
            ratio = max(width, height) / min(width, height)
            if ratio > 2.5: 
                return False
                
            return True
    except Exception:
        return False

def process_game(rom_file):
    base_name = os.path.splitext(rom_file)[0]
    clean_title = clean_name(rom_file)
    
    if not clean_title:
        return
        
    game_dir = os.path.join(OUTPUT_DIR, clean_title)
    
    # Если игра уже обработана, просто копируем ром (если это другая версия)
    if clean_title in processed_games:
        rom_dir = os.path.join(game_dir, "rom")
        rom_src = os.path.join(NES_H_DIR, rom_file)
        if os.path.isfile(rom_src):
            shutil.copy2(rom_src, os.path.join(rom_dir, rom_file))
        return

    print(f"[PROCESS] {clean_title}")
    
    rom_dir = os.path.join(game_dir, "rom")
    images_dir = os.path.join(game_dir, "images")
    video_dir = os.path.join(game_dir, "video")
    
    os.makedirs(rom_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(video_dir, exist_ok=True)

    # Копируем РОМ
    rom_src = os.path.join(NES_H_DIR, rom_file)
    if os.path.isfile(rom_src):
        shutil.copy2(rom_src, os.path.join(rom_dir, rom_file))

    # --- СКРИНШОТЫ С УМНЫМ ФИЛЬТРОМ ---
    advert_folder = os.path.join(MEDIA_DIR, "advert")
    if os.path.isdir(advert_folder):
        count = 1
        for f in os.listdir(advert_folder):
            if f.startswith(base_name) and f.lower().endswith((".png", ".jpg", ".jpeg")):
                full_path = os.path.join(advert_folder, f)
                
                # Проверяем, что это нормальный скриншот
                if is_valid_screenshot(full_path):
                    ext = os.path.splitext(f)[1]
                    dst = os.path.join(images_dir, f"{count}{ext}")
                    shutil.copy2(full_path, dst)
                    count += 1

    # Фон
    bg_src = get_media_file("background", base_name, (".png", ".jpg", ".jpeg"))
    if bg_src:
        shutil.copy2(bg_src, os.path.join(images_dir, "background.png"))

    # Баннер (обложка для карточки)
    banner_src = get_media_file("banner", base_name, (".png", ".jpg", ".jpeg"))
    if banner_src:
        shutil.copy2(banner_src, os.path.join(images_dir, "cartridge.png"))
    else:
        # Если баннера нет, берем коробку
        for sub in ["box", "cart", "box3d"]:
            fallback = get_media_file(sub, base_name, (".png", ".jpg", ".jpeg"))
            if fallback:
                shutil.copy2(fallback, os.path.join(images_dir, "cartridge.png"))
                break

    # Видео
    vid_src = get_media_file("video", base_name, (".mp4", ".avi", ".webm"))
    if vid_src:
        ext = os.path.splitext(vid_src)[1]
        shutil.copy2(vid_src, os.path.join(video_dir, f"gameplay{ext}"))

    processed_games.add(clean_title)

def main():
    if not os.path.isdir(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Ищем все ромы в корне nesh
    rom_files = [f for f in os.listdir(NES_H_DIR) if f.lower().endswith((".nes", ".zip", ".gen", ".smd", ".bin"))]
    
    print(f"Найдено ромов: {len(rom_files)}")
    
    for rom in rom_files:
        process_game(rom)

    print(f"\nГотово! Собрано уникальных папок: {len(processed_games)}")
    print(f"Результат в папке: {OUTPUT_DIR}")

if __name__ == "__main__":
    # Проверяем, установлена ли библиотека Pillow
    try:
        from PIL import Image
    except ImportError:
        print("ОШИБКА: Не установлена библиотека Pillow.")
        print("Введи в консоли: pip install Pillow")
        input("Нажми Enter для выхода...")
        exit(1)
        
    main()