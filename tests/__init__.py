# coding: utf-8

import unittest
import datetime as dt
from vvs_efa import VVS_EFA

vvs_efa = VVS_EFA.VVS_EFA()

class TestConvertNameToId(unittest.TestCase):

    def test_stadtbibliothek_name(self):
        self.assertEqual(vvs_efa.convertNameToId("Stadtbibliothek"), "5006116")

    def test_hauptbahnhof_name(self):
        self.assertEqual(vvs_efa.convertNameToId("Hauptbahnhof"), "5006118")

    def test_name_with_umlaut(self):
        self.assertEqual(vvs_efa.convertNameToId("Möhringen"), "5006169")

    def test_name_with_scharfs(self):
        self.assertEqual(vvs_efa.convertNameToId("Vaihinger Straße"), "5000170")

    def test_stadtbibliothek_name_mobile(self):
        self.assertEqual(vvs_efa.convertNameToId("Stadtbibliothek", True), "5006116")

    def test_hauptbahnhof_name_mobile(self):
        self.assertEqual(vvs_efa.convertNameToId("Hauptbahnhof", True), "5006118")

    def test_empty_name(self):
        self.assertEqual(vvs_efa.convertNameToId(""), None)

class TestGetNextConnections(unittest.TestCase):

    def test_invalid_origin(self):
        with self.assertRaises(TypeError):
            vvs_efa.getNextConnections("", "Feuersee", dt.datetime(2015, 7, 13, 7, 20), True)

if __name__ == '__main__':
    unittest.main()
