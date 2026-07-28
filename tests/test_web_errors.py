import json
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from quantaforge.service import QuantumExperimentAgent
from quantaforge.web import create_handler


class WebStructuredErrorTests(unittest.TestCase):
    def test_oversize_request_returns_http_422_and_structured_error(self) -> None:
        agent = QuantumExperimentAgent(PROJECT_ROOT / "qa" / "test-artifacts")
        server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(agent))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            request = Request(
                f"http://127.0.0.1:{server.server_port}/api/run",
                data=json.dumps(
                    {"prompt": "用27个量子比特构建GHZ态并使用GPU执行", "device": "gpu"}
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with self.assertRaises(HTTPError) as context:
                urlopen(request, timeout=5)
            self.assertEqual(context.exception.code, 422)
            payload = json.loads(context.exception.read().decode("utf-8"))
            self.assertEqual(payload["status"], "failed")
            self.assertEqual(payload["error"]["code"], "CAPABILITY_LIMIT_EXCEEDED")
            self.assertEqual(payload["error"]["requested"], 27)
            self.assertEqual(payload["error"]["allowed"], {"min": 3, "max": 26})
            self.assertFalse(payload["verification"]["executed"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
