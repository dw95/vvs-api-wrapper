import unittest
import datetime as dt
from .. import VVS_EFA

vvs_efa = VVS_EFA()

class TestGetNextConnections(unittest.TestCase):

    def test_empty_string_origin(self):
        self.assertEqual(vvs_efa.getNextConnections("", "Feuersee", dt.datetime(2015, 7, 7, 7, 20), True), None)



if __name__ == '__main__':
    unittest.main()
