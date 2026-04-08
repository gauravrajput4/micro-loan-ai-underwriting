import unittest
import numpy as np

from backend.services.model_monitoring import _psi


class TestMonitoringMetrics(unittest.TestCase):
    def test_psi_non_negative(self):
        expected = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        actual = np.array([0.15, 0.25, 0.35, 0.45, 0.55])
        score = _psi(expected, actual)
        self.assertGreaterEqual(score, 0.0)


if __name__ == "__main__":
    unittest.main()

