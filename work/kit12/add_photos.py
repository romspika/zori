"""Кладёт фото в тему san-zori и собирает архив для загрузки в WordPress.

Запуск из папки kasimov-zori:
    python add_photos.py --media media/renamed --theme san-zori --out san-zori.zip

Нужен Pillow: pip install pillow
"""
import argparse
import csv
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageOps

# Консоль Windows по умолчанию в cp1251 — переводим вывод в UTF-8.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--media", default="media/renamed", help="папка с переименованными фото")
    ap.add_argument("--theme", default="san-zori", help="папка темы")
    ap.add_argument("--map", default="img-map.csv", help="таблица: слот → файл")
    ap.add_argument("--out", default="san-zori.zip", help="итоговый архив")
    args = ap.parse_args()

    media, theme = Path(args.media), Path(args.theme)
    img_dir = theme / "assets" / "img"
    img_dir.mkdir(parents=True, exist_ok=True)

    done, missing = 0, []
    with open(args.map, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            src = media / row["source"]
            if not src.exists():
                missing.append(f'{row["slot"]}: нет файла {src}')
                continue
            im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
            max_w = int(row["max_width"])
            if im.width > max_w:
                im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
            dst = img_dir / f'{row["slot"]}.jpg'
            im.save(dst, "JPEG", quality=82, optimize=True, progressive=True)
            done += 1
            print(f'ok  {row["slot"]:<20} <- {row["source"]}  {im.width}×{im.height}  {dst.stat().st_size // 1024} КБ')

    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(theme.rglob("*")):
            if p.is_file() and not p.name.startswith("."):
                z.write(p, Path("san-zori") / p.relative_to(theme))

    size_mb = Path(args.out).stat().st_size / 1024 / 1024
    print(f"\nФото: {done}, не найдено: {len(missing)}")
    for m in missing:
        print("  " + m)
    print(f"Архив: {args.out}, {size_mb:.1f} МБ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
