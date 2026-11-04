# tools/merger.py — Слияние с переносом в USED
import os
import shutil
import re

OLD_BASE = r"F:\User\project\GitHub\CRYPT8BIT\Dendy"
NEW_BASE = r"E:\Игры\nesh\rom"
USED_DIR = os.path.join(NEW_BASE, "USED")

def normalize_name(name):
    return re.sub(r'[^a-z0-9]', '', name.lower())

def get_folders(folder):
    if not os.path.isdir(folder):
        return {}
    return {d.lower().strip(): d for d in os.listdir(folder) 
            if os.path.isdir(os.path.join(folder, d)) and d != "USED"}

def main():
    if not os.path.isdir(USED_DIR):
        os.makedirs(USED_DIR)

    old_games = get_folders(OLD_BASE)
    
    all_new = {}
    for base in [NEW_BASE, USED_DIR]:
        if os.path.isdir(base):
            for d in os.listdir(base):
                if os.path.isdir(os.path.join(base, d)) and d != "USED":
                    all_new[d.lower().strip()] = (d, base)

    print(f"Игр в старой базе: {len(old_games)}")
    print(f"Игр в новой сборке: {len(all_new)}")
    print("-" * 40)

    merged_count = 0
    skipped = []

    for old_lower, old_name in old_games.items():
        old_path = os.path.join(OLD_BASE, old_name)
        
        match_name = None
        match_base = None
        match_type = ""

        if old_lower in all_new:
            match_name, match_base = all_new[old_lower]
            match_type = "Точное"
        else:
            old_norm = normalize_name(old_name)
            for new_lower, (new_name, new_base) in all_new.items():
                if normalize_name(new_name) == old_norm:
                    match_name, match_base = new_name, new_base
                    match_type = "Нормализованное"
                    break

        if match_name:
            new_path = os.path.join(match_base, match_name)
            print(f" [{match_type}] {old_name} -> {match_name}")

            # Копируем РОМ и ВИДЕО
            for sub in ["rom", "video"]:
                src_dir = os.path.join(new_path, sub)
                dst_dir = os.path.join(old_path, sub)
                if os.path.isdir(src_dir):
                    os.makedirs(dst_dir, exist_ok=True)
                    for f in os.listdir(src_dir):
                        if os.path.isfile(os.path.join(src_dir, f)):
                            shutil.copy2(os.path.join(src_dir, f), os.path.join(dst_dir, f))

            # Копируем картинки
            src_img_dir = os.path.join(new_path, "images")
            dst_img_dir = os.path.join(old_path, "images")
            os.makedirs(dst_img_dir, exist_ok=True)
            
            if os.path.isdir(src_img_dir):
                bg_src = os.path.join(src_img_dir, "background.png")
                if os.path.isfile(bg_src):
                    shutil.copy2(bg_src, os.path.join(dst_img_dir, "background.png"))
                
                cart_src = os.path.join(src_img_dir, "cartridge.png")
                if os.path.isfile(cart_src):
                    cart_size = os.path.getsize(cart_src)
                    bg_size = os.path.getsize(bg_src) if os.path.isfile(bg_src) else 0
                    
                    if cart_size != bg_size:
                        shutil.copy2(cart_src, os.path.join(dst_img_dir, "cartridge.png"))

            # ПЕРЕНОСИМ ПАПКУ В USED (если она была в NEW_BASE)
            if match_base == NEW_BASE:
                used_path = os.path.join(USED_DIR, match_name)
                try:
                    if os.path.exists(used_path):
                        shutil.rmtree(used_path)
                    shutil.move(new_path, used_path)
                    print(f"   -> Перенесено в USED")
                except Exception as e:
                    print(f"   -> Ошибка переноса: {e}")

            # Переименовываем старую папку (если нужно)
            if old_name != match_name:
                new_old_path = os.path.join(OLD_BASE, match_name)
                if not os.path.exists(new_old_path):
                    os.rename(old_path, new_old_path)
                    old_path = new_old_path
                    print(f"   -> Переименовано в {match_name}")

            merged_count += 1
        else:
            skipped.append(old_name)

    print("\n" + "=" * 50)
    print(f"Объединено: {merged_count}")
    print(f"Не найдено: {len(skipped)}")

    if skipped:
        print("\nСПИСОК БЕЗ ПАРЫ:")
        for game in skipped:
            print(f" - {game}")
            old_path = os.path.join(OLD_BASE, game)
            new_path = os.path.join(OLD_BASE, f"_{game}")
            
            # Если уже есть с префиксом, удаляем
            if os.path.exists(new_path):
                shutil.rmtree(new_path)
            
            try:
                os.rename(old_path, new_path)
            except Exception as e:
                pass

if __name__ == "__main__":
    main()