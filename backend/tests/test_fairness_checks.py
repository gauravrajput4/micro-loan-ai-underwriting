import unittest

from backend.services.fairness_checks import _confusion_counts


class TestFairnessChecks(unittest.TestCase):
    def test_confusion_counts(self):
        rows = [
            {"actual_outcome": 1, "prediction": 1},
            {"actual_outcome": 0, "prediction": 1},
            {"actual_outcome": 0, "prediction": 0},
            {"actual_outcome": 1, "prediction": 0},
        ]
        cm = _confusion_counts(rows)
        self.assertEqual(cm["tp"], 1)
        self.assertEqual(cm["fp"], 1)
        self.assertEqual(cm["tn"], 1)
        self.assertEqual(cm["fn"], 1)


if __name__ == "__main__":
    unittest.main()

