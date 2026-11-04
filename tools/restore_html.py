# tools/restore_html.py — Восстановление только index.html из бэкапа
import os
import shutil

# --- НАСТРОЙКИ ---
CURRENT_BASE = r"F:\User\project\GitHub\CRYPT8BIT\Dendy"  # Текущая папка (где каша)
BACKUP_BASE = r"F:\User\project\GitHub\CRYPT8BIT\Dendy_Backup" # Твоя папка с бэкапом

def main():
    if not os.path.isdir(BACKUP_BASE):
        print(f"Бэкап не найден: {BACKUP_BASE}")
        return

    restored = 0
    skipped = []

    # Проходим по всем папкам в текущей базе
    for game_folder in os.listdir(CURRENT_BASE):
        current_game_path = os.path.join(CURRENT_BASE, game_folder)
        if not os.path.isdir(current_game_path):
            continue

        # Ищем такую же папку в бэкапе
        backup_game_path = os.path.join(BACKUP_BASE, game_folder)
        
        if os.path.isdir(backup_game_path):
            backup_html = os.path.join(backup_game_path, "index.html")
            current_html = os.path.join(current_game_path, "index.html")
            
            if os.path.isfile(backup_html):
                # Копируем старый index.html (с правильным текстом) поверх нового
                shutil.copy2(backup_html, current_html)
                print(f"[RESTORED] {game_folder}")
                restored += 1
            else:
                skipped.append(game_folder)
        else:
            skipped.append(game_folder)

    print(f"\nВосстановлено: {restored}")
    print(f"Пропущено (нет в бэкапе): {len(skipped)}")

if __name__ == "__main__":
    main()