"""Local web UI server for Zero-Agent."""
from __future__ import annotations

import json
import logging
import mimetypes
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from main import build_agent

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parent
WEB = (ROOT / "web").resolve()
MAX_BODY_BYTES = 32 * 1024
AGENT = build_agent()
AGENT_LOCK = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json_error(self, status: int, message: str) -> None:
        body = json.dumps({"error": message}, ensure_ascii=False).encode("utf-8")
        self._send(status, "application/json; charset=utf-8", body)

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/" or path == "/index.html":
            relative = "index.html"
        elif path.startswith("/web/"):
            relative = path.removeprefix("/web/")
        else:
            self._send(404, "text/plain; charset=utf-8", b"Not found")
            return

        target = (WEB / relative).resolve()
        if WEB not in target.parents or not target.is_file():
            self._send(404, "text/plain; charset=utf-8", b"Not found")
            return

        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self._send(200, f"{content_type}; charset=utf-8", target.read_bytes())

    def do_POST(self) -> None:  # noqa: N802
        if self.path.split("?", 1)[0] != "/api/chat":
            self._json_error(404, "Not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json_error(400, "Invalid Content-Length")
            return

        if content_length <= 0:
            self._json_error(400, "Request body is required")
            return
        if content_length > MAX_BODY_BYTES:
            self._json_error(413, "Request body is too large")
            return

        try:
            payload = json.loads(self.rfile.read(content_length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json_error(400, "Invalid JSON")
            return

        if not isinstance(payload, dict):
            self._json_error(400, "JSON body must be an object")
            return

        message = payload.get("message")
        if not isinstance(message, str) or not message.strip():
            self._json_error(400, "message is required")
            return

        try:
            # Agent currently owns a single SQLite connection; serialize requests
            # until the memory layer provides a connection-per-thread abstraction.
            with AGENT_LOCK:
                result = AGENT.run(message.strip())
            body = json.dumps(
                {"response": result.response, "tool_used": result.tool_used},
                ensure_ascii=False,
            ).encode("utf-8")
            self._send(200, "application/json; charset=utf-8", body)
        except Exception:
            logger.exception("Web request failed")
            self._json_error(500, "Internal server error")

    def log_message(self, format: str, *args: object) -> None:
        logger.info("web %s", format % args)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    logger.info("Zero-Agent Web UI: http://localhost:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Web server stopped")
    finally:
        server.server_close()
