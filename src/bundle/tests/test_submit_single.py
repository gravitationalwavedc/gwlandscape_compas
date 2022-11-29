import sys
import unittest
from pathlib import Path


class TestSubmitSingle(unittest.TestCase):
    def setUp(self):
        sys.path.append(str(Path(__file__).parent / "misc"))

    def test_submit_single(self):
        self.assertTrue(1)
