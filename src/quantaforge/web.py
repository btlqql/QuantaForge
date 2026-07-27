from __future__ import annotations

import argparse
import json
import mimetypes
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .service import QuantumExperimentAgent
from .runtime import ensure_biren_process


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_ROOT = PROJECT_ROOT / "web" / "static"


def create_handler(agent: QuantumExperimentAgent):
    class Handler(BaseHTTPRequestHandler):
        server_version = "QuantaForge/0.1"

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            if path == "/api/health":
                self._json({"status": "ok", "service": "QuantaForge", "version": "0.1.0"})
                return
            if path == "/api/examples":
                self._json(
                    {
                        "examples": [
                            "构建Bell纠缠态，在CPU和壁仞GPU运行并验证结果",
                            "用5个量子比特运行Grover搜索，目标状态为10110，CPU和GPU对比",
                            "用4个量子比特运行QAOA MaxCut，层数2，优化30轮，使用GPU",
                        ]
                    }
                )
                return
            if path.startswith("/artifacts/"):
                relative = unquote(path.removeprefix("/artifacts/"))
                self._file(agent.artifact_root, relative)
                return
            relative = "index.html" if path == "/" else path.lstrip("/")
            self._file(STATIC_ROOT, relative)

        def do_POST(self) -> None:
            path = urlparse(self.path).path
            try:
                body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
                payload = json.loads(body or b"{}")
                prompt = str(payload.get("prompt", ""))
                device = str(payload.get("device", "gpu"))
                if path == "/api/plan":
                    self._json(agent.plan(prompt, default_device=device))
                    return
                if path == "/api/run":
                    self._json(agent.run(prompt, default_device=device).to_dict())
                    return
                self.send_error(HTTPStatus.NOT_FOUND)
            except ValueError as exc:
                self._json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            except Exception as exc:
                self._json(
                    {"error": f"{type(exc).__name__}: {exc}"},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                )

        def _json(self, payload: dict, *, status: HTTPStatus = HTTPStatus.OK) -> None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _file(self, root: Path, relative: str) -> None:
            root = root.resolve()
            candidate = (root / relative).resolve()
            if root not in candidate.parents and candidate != root:
                self.send_error(HTTPStatus.FORBIDDEN)
                return
            if not candidate.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            data = candidate.read_bytes()
            content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, fmt: str, *args) -> None:
            print(f"[web] {self.address_string()} {fmt % args}")

    return Handler


def main() -> None:
    ensure_biren_process(module="quantaforge.web")
    parser = argparse.ArgumentParser(description="运行QuantaForge Web演示")
    parser.add_argument("--host", default=os.getenv("QUANTAFORGE_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("QUANTAFORGE_PORT", "7860")))
    parser.add_argument("--artifacts", default=os.getenv("QUANTAFORGE_ARTIFACTS", str(PROJECT_ROOT / "artifacts")))
    args = parser.parse_args()
    agent = QuantumExperimentAgent(args.artifacts)
    server = ThreadingHTTPServer((args.host, args.port), create_handler(agent))
    print(f"QuantaForge running at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
