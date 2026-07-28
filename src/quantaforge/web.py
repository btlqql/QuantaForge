from __future__ import annotations

import argparse
import json
import mimetypes
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .errors import QuantaForgeError, error_response, normalize_error
from .service import QuantumExperimentAgent
from .runtime import BIREN_ENV_SCRIPT, ensure_biren_process, warmup_biren_backend


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
            except QuantaForgeError as exc:
                self._json(error_response(exc), status=HTTPStatus(exc.http_status))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                malformed = QuantaForgeError(
                    code="MALFORMED_JSON",
                    error_type="input_error",
                    message="请求正文不是有效的JSON。",
                    field="body",
                    recoverable=True,
                    suggestions=["使用Content-Type: application/json并检查JSON语法"],
                    details={"exception_type": type(exc).__name__},
                    http_status=HTTPStatus.BAD_REQUEST,
                )
                self._json(error_response(malformed), status=HTTPStatus.BAD_REQUEST)
            except Exception as exc:
                structured = normalize_error(exc)
                self._json(error_response(structured), status=HTTPStatus(structured.http_status))

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
    parser.add_argument(
        "--skip-gpu-warmup",
        action="store_true",
        help="跳过Web服务启动阶段的壁仞GPU预热",
    )
    args = parser.parse_args()
    if BIREN_ENV_SCRIPT.is_file() and not args.skip_gpu_warmup:
        try:
            warmup = warmup_biren_backend()
            print(
                "QuantaForge GPU warm-up complete: "
                f"{warmup['elapsed_s']:.6f}s, max_abs_error={warmup['max_abs_error']:.3e}"
            )
        except Exception as exc:
            # The health endpoint and CPU experiments remain useful if a shared
            # GPU is temporarily unavailable; the first GPU request will expose
            # the original backend error with full context.
            print(f"QuantaForge GPU warm-up warning: {type(exc).__name__}: {exc}")
    agent = QuantumExperimentAgent(args.artifacts)
    server = ThreadingHTTPServer((args.host, args.port), create_handler(agent))
    print(f"QuantaForge running at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
