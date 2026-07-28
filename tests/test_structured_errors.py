import unittest

from quantaforge.errors import QuantaForgeError, error_response
from quantaforge.parser import parse_experiment


class StructuredErrorTests(unittest.TestCase):
    def assert_structured_error(self, prompt, code, field, requested):
        with self.assertRaises(QuantaForgeError) as context:
            parse_experiment(prompt, default_device="cpu")
        payload = error_response(context.exception)
        self.assertEqual(payload["status"], "failed")
        self.assertFalse(payload["verification"]["executed"])
        self.assertEqual(payload["error"]["code"], code)
        self.assertEqual(payload["error"]["field"], field)
        self.assertEqual(payload["error"]["requested"], requested)
        self.assertTrue(payload["error"]["recoverable"])
        self.assertGreaterEqual(len(payload["error"]["suggestions"]), 1)

    def test_ghz_oversize(self):
        self.assert_structured_error(
            "用27个量子比特构建GHZ态，使用CPU执行",
            "CAPABILITY_LIMIT_EXCEEDED",
            "qubits",
            27,
        )

    def test_ghz_maximum_is_accepted(self):
        spec = parse_experiment("用26个量子比特构建GHZ态，使用GPU执行", default_device="gpu")
        self.assertEqual(spec.algorithm, "ghz")
        self.assertEqual(spec.qubits, 26)
        self.assertEqual(spec.device, "gpu")

    def test_grover_oversize(self):
        self.assert_structured_error(
            "用13个量子比特运行Grover搜索，目标状态为1111111111111",
            "CAPABILITY_LIMIT_EXCEEDED",
            "qubits",
            13,
        )

    def test_qaoa_oversize(self):
        self.assert_structured_error(
            "用12个量子比特运行QAOA MaxCut，使用CPU",
            "CAPABILITY_LIMIT_EXCEEDED",
            "qubits",
            12,
        )

    def test_qaoa_layers_oversize(self):
        self.assert_structured_error(
            "用4个量子比特运行QAOA MaxCut，层数8，使用CPU",
            "CAPABILITY_LIMIT_EXCEEDED",
            "layers",
            8,
        )

    def test_bell_fixed_size(self):
        self.assert_structured_error(
            "用5个量子比特构建Bell态，使用CPU",
            "FIXED_SIZE_REQUIRED",
            "qubits",
            5,
        )

    def test_empty_prompt(self):
        self.assert_structured_error("", "EMPTY_PROMPT", "prompt", "")

    def test_unknown_algorithm(self):
        with self.assertRaises(QuantaForgeError) as context:
            parse_experiment("帮我做一个量子实验", default_device="cpu")
        payload = error_response(context.exception)
        self.assertEqual(payload["error"]["code"], "UNSUPPORTED_ALGORITHM")
        self.assertEqual(payload["error"]["allowed"], ["bell", "ghz", "grover", "qaoa"])


if __name__ == "__main__":
    unittest.main()
