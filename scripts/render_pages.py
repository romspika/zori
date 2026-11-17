"""Рендер всех страниц из inventory/pages.csv через headless Chrome с локального сервера (scripts/serve_mirror.py).
Сеть наружу закрыта (--host-resolver-rules), кроме 127.0.0.1. Результат: work/rendered/<local_file> (UTF-8 DOM после JS)."""
import csv, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
OUT = ROOT / 'work' / 'rendered'
PORT = sys.argv[1] if len(sys.argv) > 1 else '8765'
rows = list(csv.DictReader(open(ROOT / 'inventory' / 'pages.csv', encoding='utf-8-sig')))
for r in rows:
    lf = r['local_file'].split('/', 1)[1]
    dst = OUT / lf
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--mute-audio',
           f'--user-data-dir={ROOT / "work" / "chrome-profile"}',
           '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1',
           '--virtual-time-budget=8000', '--window-size=1400,1000', '--dump-dom', f'http://127.0.0.1:{PORT}/{lf}']
    p = subprocess.run(cmd, capture_output=True, timeout=120)
    dst.write_bytes(p.stdout)
    print(len(p.stdout), lf)
