import unittest

from quantaforge.errors import QuantaForgeError
from quantaforge.parser import parse_experiment


class ParserTests(unittest.TestCase):
    def test_grover_chinese_prompt(self):
        spec = parse_experiment("用5个量子比特运行Grover搜索，目标状态为10110，CPU和GPU对比")
        self.assertEqual(spec.algorithm, "grover")
        self.assertEqual(spec.qubits, 5)
        self.assertEqual(spec.target, "10110")
        self.assertEqual(spec.device, "both")

    def test_qaoa_defaults_to_cycle_graph(self):
        spec = parse_experiment("用4个量子比特运行QAOA MaxCut，层数2，优化30轮，使用GPU")
        self.assertEqual(spec.algorithm, "qaoa")
        self.assertEqual(spec.edges, [(0, 1), (0, 3), (1, 2), (2, 3)])

    def test_rejects_invalid_grover_target(self):
        with self.assertRaisesRegex(QuantaForgeError, "二进制串"):
            parse_experiment("用5个量子比特运行Grover，目标状态为101")

    def test_rejects_unknown_algorithm(self):
        with self.assertRaisesRegex(QuantaForgeError, "暂未识别"):
            parse_experiment("帮我做一个量子实验")


if __name__ == "__main__":
    unittest.main()
