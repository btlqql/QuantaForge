import unittest

from quantaforge.verification import exact_maxcut, grover_theory, verify_ghz, verify_grover, verify_qaoa


class VerificationTests(unittest.TestCase):
    def test_bell_analytic_verification(self):
        report = verify_ghz([0.5, 0.0, 0.0, 0.5], 2)
        self.assertTrue(report["passed"])

    def test_grover_analytic_verification(self):
        _, probability = grover_theory(3)
        report = verify_grover("101", "101", probability, 3)
        self.assertTrue(report["passed"])

    def test_exact_maxcut_cycle(self):
        edges = [(0, 1), (1, 2), (2, 3), (0, 3)]
        optimum, solutions = exact_maxcut(4, edges)
        self.assertEqual(optimum, 4)
        self.assertIn("0101", solutions)
        self.assertTrue(verify_qaoa("0101", 4, 4, edges)["passed"])


if __name__ == "__main__":
    unittest.main()

