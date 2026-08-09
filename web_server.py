"""Local web UI server for Zero-Agent."""
from __future__ import annotations

import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from main import build_agent

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
AGENT = build_agent()


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/" or path == "/index.html":
            target = WEB / "index.html"
        elif path.startswith("/web/"):
            target = WEB / path.removeprefix("/web/")
        else:
            self._send(404, "text/plain; charset=utf-8", b"Not found")
            return
        if not target.is_file() or WEB not in target.parents:
            self._send(404, "text/plain; charset=utf-8", b"Not found")
            return
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self._send(200, f"{content_type}; charset=utf-8", target.read_bytes())

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/chat":
            self._send(404, "application/json", b'{"error":"Not found"}')
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            message = str(payload.get("message", "")).strip()
            if not message:
                raise ValueError("message is required")
            result = AGENT.run(message)
            body = json.dumps(
                {"response": result.response, "tool_used": result.tool_used},
                ensure_ascii=False,
            ).encode("utf-8")
            self._send(200, "application/json; charset=utf-8", body)
        except Exception as exc:
            body = json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8")
            self._send(500, "application/json; charset=utf-8", body)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[web] {format % args}")


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("Zero-Agent Web UI: http://localhost:8000")
    print("Pressione Ctrl+C para encerrar.")
    server.serve_forever()
