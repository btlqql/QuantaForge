import unittest

import numpy as np

from quantaforge.experiments import _ghz_output_distribution
from quantaforge.verification import exact_maxcut, grover_theory, verify_ghz, verify_grover, verify_qaoa


class VerificationTests(unittest.TestCase):
    def test_bell_analytic_verification(self):
        report = verify_ghz([0.5, 0.0, 0.0, 0.5], 2)
        self.assertTrue(report["passed"])

    def test_grover_analytic_verification(self):
        _, probability = grover_theory(3)
        report = verify_grover("101", "101", probability, 3)
        self.assertTrue(report["passed"])

    def test_large_ghz_web_output_is_sparse_but_verified(self):
        probabilities = np.zeros(8192, dtype=np.float32)
        probabilities[0] = probabilities[-1] = 0.5
        self.assertTrue(verify_ghz(probabilities, 13)["passed"])
        values, labels, mode = _ghz_output_distribution(probabilities, 13)
        self.assertEqual(mode, "sparse_nonzero")
        self.assertEqual(values, [0.5, 0.5])
        self.assertEqual(labels, ["0" * 13, "1" * 13])

    def test_exact_maxcut_cycle(self):
        edges = [(0, 1), (1, 2), (2, 3), (0, 3)]
        optimum, solutions = exact_maxcut(4, edges)
        self.assertEqual(optimum, 4)
        self.assertIn("0101", solutions)
        self.assertTrue(verify_qaoa("0101", 4, 4, edges)["passed"])


if __name__ == "__main__":
    unittest.main()
