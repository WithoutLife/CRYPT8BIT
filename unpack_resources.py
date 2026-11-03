import os
import resources_rc  # noqa: F401 — просто чтобы модуль загрузился
from PySide6.QtCore import QFile, QIODevice

FILES = [
    "launcher_icon.ico",
    "retro_hub_logo.png",
    "style.css",
    "icon_dendy.png",
    "icon_sega.png",
    "icon_sony.png",
]

OUT_DIR = "assets"
os.makedirs(OUT_DIR, exist_ok=True)

for name in FILES:
    qf = QFile(f":/{name}")
    if not qf.exists():
        print(f"[SKIP] {name} — нет в ресурсах")
        continue
    if not qf.open(QIODevice.ReadOnly):
        print(f"[FAIL] {name} — не открылся")
        continue
    data = qf.readAll().data()
    qf.close()
    out_path = os.path.join(OUT_DIR, name)
    with open(out_path, "wb") as f:
        f.write(data)
    print(f"[OK]   {name} -> {out_path} ({len(data)} байт)")

print("Готово.")