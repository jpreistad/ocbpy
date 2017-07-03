#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2017, AGB & GC
# Full license can be found in License.md
#-----------------------------------------------------------------------------
""" Tests the ocb_scaling class and functions
"""

import ocbpy.instruments.general as ocb_igen
import unittest
import numpy as np

class TestGeneralMethods(unittest.TestCase):

    def setUp(self):
        """ Initialize the OCBoundary object using the test file, as well as
        the VectorData object
        """
        from os.path import isfile
        import ocbpy
        
        ocb_dir = ocbpy.__file__.split("/")
        self.test_file = "{:s}/{:s}".format("/".join(ocb_dir[:-1]),
                                            "tests/test_data/test_north_circle")
        self.assertTrue(isfile(self.test_file))

    def tearDown(self):
        del self.test_file

    def test_file_test(self):
        """ Test the general file testing routine
        """
        self.assertTrue(ocb_igen.test_file(self.test_file))
        self.assertFalse(ocb_igen.test_file("/"))
        print "Testing for warning above stating 'name provided is not a file'"

    def test_load_ascii_data(self):
        """ Test the general routine to load ASCII data
        """

        hh = ["YEAR SOY NB PHICENT RCENT R A RERR"]
        header, data = ocb_igen.load_ascii_data(self.test_file, 0, header=hh)

        # Test to ensure the output header equals the input header
        self.assertListEqual(header, hh)

        # Test to see that the data keys are all in the header
        ktest = sorted(hh[0].split())
        self.assertListEqual(ktest, sorted(data.keys()))

        # Test the length of the data file
        self.assertEqual(data['A'].shape[0], 75)

        # Test the values of the last data line
        test_vals = {"YEAR":2000.0, "SOY":11187202.0, "NB":9.0, "A":1.302e+07,
                     "PHICENT":315.29, "RCENT":2.67, "R":18.38, "RERR":0.47}
        for kk in test_vals.keys():
            self.assertEqual(data[kk][-1], test_vals[kk])

if __name__ == '__main__':
    unittest.main()

