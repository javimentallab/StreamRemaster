"""Serves the frame generation bench and collects its results. Loopback only.

Usage: python -I -X utf8 server.py <clip.mp4> <results.jsonl> [port]
It exits by itself when the page reports that it is done.
"""
import http.server
import json
import pathlib
import sys
import threading

ROOT = pathlib.Path(__file__).resolve().parents[2]
CLIP = pathlib.Path(sys.argv[1]).resolve()
RESULTS = pathlib.Path(sys.argv[2]).resolve()
PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8792


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path.split("?")[0] == "/clip60.mp4":
            data = CLIP.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        super().do_GET()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        with RESULTS.open("a", encoding="utf-8") as fh:
            fh.write(body + "\n")
        self.send_response(204)
        self.end_headers()
        if json.loads(body).get("done"):
            threading.Thread(target=self.server.shutdown, daemon=True).start()

    def log_message(self, *args):
        pass


http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
