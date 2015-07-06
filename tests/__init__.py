import unittest
import datetime as dt
from vvs_efa import VVS_EFA

vvs_efa = VVS_EFA.VVS_EFA()

class TestConvertNameToId(unittest.TestCase):

    def test_stadtbibliothek_name(self):
        self.assertEqual(vvs_efa.convertNameToId("Stadtbibliothek"), "5006116")

    def test_hauptbahnhof_name(self):
        self.assertEqual(vvs_efa.convertNameToId("Hauptbahnhof"), "5006118")

    def test_stadtbibliothek_name_mobile(self):
        self.assertEqual(vvs_efa.convertNameToId("Stadtbibliothek", True), "5006116")

    def test_hauptbahnhof_name_mobile(self):
        self.assertEqual(vvs_efa.convertNameToId("Hauptbahnhof", True), "5006118")


if __name__ == '__main__':
    unittest.main()
