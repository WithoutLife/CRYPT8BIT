# tools/check_paths.py — Проверка путей в index.html
import os
import re

LIBRARY_DIR = r"F:\User\project\GitHub\CRYPT8BIT\Dendy"

def main():
    print("Проверка путей в index.html...")
    issues = 0

    for game_folder in os.listdir(LIBRARY_DIR):
        game_path = os.path.join(LIBRARY_DIR, game_folder)
        if not os.path.isdir(game_path):
            continue
            
        html_path = os.path.join(game_path, "index.html")
        if not os.path.isfile(html_path):
            continue

        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Ищем абсолютные пути (F:\ или C:\)
        if re.search(r'[A-Z]:\\', content):
            print(f" [!] Абсолютный путь найден в: {game_folder}")
            issues += 1

        # Ищем ссылки на картинки (src="..." или url(...))
        img_links = re.findall(r'src=["\'](.*?)["\']', content)
        for link in img_links:
            if link.startswith("http"):
                continue
            # Проверяем, существует ли файл относительно папки игры
            full_path = os.path.join(game_path, link)
            if not os.path.exists(full_path):
                print(f" [!] Битая ссылка в {game_folder}: {link}")
                issues += 1

    if issues == 0:
        print("Все пути относительные и рабочие!")
    else:
        print(f"Найдено проблем: {issues}")

if __name__ == "__main__":
    main()