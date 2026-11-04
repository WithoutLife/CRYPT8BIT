# tools/auditor.py — Ревизор библиотеки
import os
import json

# --- НАСТРОЙКИ ---
LIBRARY_DIR = r"E:\Игры\nesh\merged"  # Где лежит собранная библиотека
# (Можешь поменять на F:\User\project\GitHub\CRYPT8BIT\Dendy, если хочешь проверить старую)

def check_game(game_path):
    audit = {
        "title": os.path.basename(game_path),
        "has_rom": False,
        "has_cover": False,
        "has_description": False,
        "screenshots_count": 0,
        "has_video": False,
        "status": "incomplete"
    }

    # Проверка РОМа
    rom_dir = os.path.join(game_path, "rom")
    if os.path.isdir(rom_dir) and any(f.lower().endswith((".nes", ".zip", ".gen", ".bin")) for f in os.listdir(rom_dir)):
        audit["has_rom"] = True

    # Проверка обложки (в images/cartridge.png или images/background.png)
    images_dir = os.path.join(game_path, "images")
    if os.path.isdir(images_dir):
        if os.path.isfile(os.path.join(images_dir, "cartridge.png")):
            audit["has_cover"] = True
        
        # Считаем скриншоты (все файлы с цифрами)
        for f in os.listdir(images_dir):
            if f[0].isdigit() and f.lower().endswith((".png", ".jpg", ".jpeg")):
                audit["screenshots_count"] += 1

    # Проверка описания (index.html)
    if os.path.isfile(os.path.join(game_path, "index.html")):
        audit["has_description"] = True

    # Проверка видео
    video_dir = os.path.join(game_path, "video")
    if os.path.isdir(video_dir) and any(f.lower().endswith((".mp4", ".avi")) for f in os.listdir(video_dir)):
        audit["has_video"] = True

    # Определяем статус
    if audit["has_rom"] and audit["has_cover"] and audit["has_description"] and audit["screenshots_count"] > 0:
        audit["status"] = "ready"
    elif audit["has_rom"]:
        audit["status"] = "need_content"

    return audit

def main():
    if not os.path.isdir(LIBRARY_DIR):
        print(f"Папка не найдена: {LIBRARY_DIR}")
        return

    games = [d for d in os.listdir(LIBRARY_DIR) if os.path.isdir(os.path.join(LIBRARY_DIR, d))]
    print(f"Сканирую {len(games)} игр...")

    ready_count = 0
    need_count = 0

    for game in games:
        game_path = os.path.join(LIBRARY_DIR, game)
        audit_data = check_game(game_path)
        
        # Сохраняем файл аудита в папку игры
        audit_path = os.path.join(game_path, "audit.json")
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(audit_data, f, ensure_ascii=False, indent=4)

        if audit_data["status"] == "ready":
            ready_count += 1
        else:
            need_count += 1

    print(f"Готовых игр: {ready_count}")
    print(f"Требуют доработки: {need_count}")
    print("Ревизия завершена!")

if __name__ == "__main__":
    main()