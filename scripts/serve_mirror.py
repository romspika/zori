"""Локальный read-only сервер зеркала raw/site/kasimovskie-zori.ru (для рендера в headless Chrome).
HTML/JS/CSS отдаются с charset=windows-1251, как на боевом хостинге (файлы с BOM браузер всё равно читает как UTF-8)."""
import http.server, functools, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent / 'raw' / 'site' / 'kasimovskie-zori.ru'
class H(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      '.html': 'text/html; charset=windows-1251', '.js': 'application/javascript; charset=windows-1251',
                      '.css': 'text/css; charset=windows-1251'}
    def log_message(self, *a): pass
    def do_POST(self): self.send_error(405)
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(H, directory=str(ROOT))).serve_forever()
