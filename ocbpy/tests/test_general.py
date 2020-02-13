#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2017, AGB & GC
# Full license can be found in License.md
#-----------------------------------------------------------------------------
""" Tests the ocb_scaling class and functions
"""
from __future__ import absolute_import, unicode_literals

import datetime as dt
import logging
from io import StringIO
import numpy as np
import os
import unittest

import ocbpy
import ocbpy.instruments.general as ocb_igen

class TestGeneralFileTestMethods(unittest.TestCase):
    def setUp(self):
        """ Initialize the logging and output variables
        """
        self.test_file = os.path.join(os.path.dirname(ocbpy.__file__), "tests",
                                      "test_data", "test_north_circle")
        self.temp_output = os.path.join(os.path.dirname(ocbpy.__file__),
                                        "tests", "test_data", "temp_gen")
        self.rstat = None

        self.lwarn = u""
        self.lout = u""
        self.log_capture = StringIO()
        ocbpy.logger.addHandler(logging.StreamHandler(self.log_capture))
        ocbpy.logger.setLevel(logging.WARNING)

    def tearDown(self):
        if os.path.isfile(self.temp_output):
            os.remove(self.temp_output)

        del self.test_file, self.lwarn, self.lout, self.log_capture, self.rstat
        del self.temp_output

    def test_file_test_success(self):
        """ Test the success condition for one of the test_data files"""
        self.rstat = ocb_igen.test_file(self.test_file)
        self.assertTrue(self.rstat)
        
    def test_file_test_not_file(self):
        """ Test the general file testing routine with a bad filename """
        self.lwarn = u"name provided is not a file"
        
        self.rstat = ocb_igen.test_file("/")
        self.lout = self.log_capture.getvalue()

        self.assertTrue(self.lout.find(self.lwarn) >= 0)
        self.assertFalse(self.rstat)

    def test_file_test_empty_file(self):
        """ Test the general file testing routine with a bad filename """
        self.lwarn = u'empty file'
        
        # Create an empty file and read it in
        open(self.temp_output, 'a').close()
        self.rstat = ocb_igen.test_file(self.temp_output)
        self.lout = self.log_capture.getvalue()

        self.assertTrue(self.lout.find(self.lwarn) >= 0)
        self.assertFalse(self.rstat)

    def test_large_file(self):
        """ Test the file size limit for loading data """
        self.lwarn = u'File size'

        # Create a 2.12 GB file
        with open(self.temp_output, 'wb') as fout:
            fout.truncate(2024 * 1024 * 1024)

        self.rstat = ocb_igen.test_file(self.temp_output)
        self.lout = self.log_capture.getvalue()

        self.assertTrue(self.lout.find(self.lwarn) >= 0)
        self.assertFalse(self.rstat)


class TestGeneralLoadMethods(unittest.TestCase):
    def setUp(self):
        """ Initialize the parameters needed to test the general loading method
        """
        ocb_dir = os.path.dirname(ocbpy.__file__)
        self.test_file_soy = os.path.join(ocb_dir, "tests", "test_data",
                                          "test_north_circle")
        self.test_file_dt = os.path.join(ocb_dir, "tests", "test_data",
                                         "dmsp-ssj_north_out.ocb")
        self.headers = {self.test_file_soy:
                        [u"YEAR SOY NB PHICENT RCENT R A RERR"],
                        self.test_file_dt:
                        [u"#sc date time r x y fom x_1 y_1 x_2 y_2\n"]}
        self.test_out = {self.test_file_soy:
                         {"YEAR": 2000.0, "SOY": 11187202.0, "NB": 9.0,
                          "A": 1.302e+07, "PHICENT": 315.29, "RCENT": 2.67,
                          "R": 18.38, "RERR": 0.47},
                         self.test_file_dt:
                         {"sc": 16.0, "date": u"2010-12-31", "fom": 3.192,
                          "r": 1.268, "time": u"23:24:53", "x": 0.437,
                          "x_1": -7.61, "x_2": 8.485, "y": 6.999, "y_1": 5.564,
                          "y_2": 8.433,
                          "datetime": dt.datetime(2010,12,31,23,24,53)}}
        self.out = None

        self.lwarn = u""
        self.lout = u""
        self.log_capture = StringIO()
        ocbpy.logger.addHandler(logging.StreamHandler(self.log_capture))
        ocbpy.logger.setLevel(logging.WARNING)

    def tearDown(self):
        del self.test_file_soy, self.lwarn, self.lout, self.log_capture
        del self.test_file_dt, self.headers, self.out, self.test_out

    def test_load_ascii_data_badfile(self):
        """ Test the general loading routine for ASCII data with bad input
        """
        self.lwarn = u'name provided is not a file'

        self.out = ocb_igen.load_ascii_data("/", 0)
        self.lout = self.log_capture.getvalue()
        self.assertListEqual(self.out[0], [])
        self.assertDictEqual(self.out[1], {})

        self.assertTrue(self.lout.find(self.lwarn) >= 0)

    def test_load_ascii_data_bad_header(self):
        """ Test the general loading routine for ASCII data with bad header
        """
        self.lwarn = u'unable to find header'

        self.out = ocb_igen.load_ascii_data(self.test_file_soy, 0,
                                            header=list())
        self.lout = self.log_capture.getvalue()
        self.assertListEqual(self.out[0], [])
        self.assertDictEqual(self.out[1], {})

        self.assertTrue(self.lout.find(self.lwarn) >= 0)
        
    @unittest.skip("Fails when run as part of the class")
    def test_load_ascii_data_w_header(self):
        """ Test the general routine to load ASCII data that has a header
        """
        self.out = ocb_igen.load_ascii_data(self.test_file_dt, 1,
                                            datetime_cols=[1, 2],
                                            datetime_fmt="%Y-%m-%d %H:%M:%S",
                                            header=list())

        # Test to ensure the output header equals the input header
        self.assertListEqual(self.out[0], self.headers[self.test_file_dt])

        # Test to see that the data keys are all in the header
        self.assertListEqual(sorted([kk for kk in self.test_out[
            self.test_file_dt].keys()]),
                             sorted([kk for kk in self.out[1].keys()]))

        # Test the length of the data file
        self.assertTupleEqual(self.out[1]['fom'].shape, (7,))

        # Test the values of the last data line
        for kk in self.test_out[self.test_file_dt].keys():
            self.assertEqual(self.out[1][kk][-1],
                             self.test_out[self.test_file_dt][kk])

    def test_load_ascii_data_wo_header(self):
        """ Test the general routine to load ASCII data by providing a header
        """
        self.out = ocb_igen.load_ascii_data(self.test_file_soy, 0,
                                        header=self.headers[self.test_file_soy])

        # Test to ensure the output header equals the input header
        self.assertListEqual(self.out[0], self.headers[self.test_file_soy])

        # Test to see that the data keys are all in the header
        self.assertListEqual(sorted([kk for kk in self.test_out[
            self.test_file_soy].keys()]),
                             sorted([kk for kk in self.out[1].keys()]))

        # Test the length of the data file
        self.assertTupleEqual(self.out[1]['A'].shape, (75,))

        # Test the values of the last data line
        for kk in self.test_out[self.test_file_soy].keys():
            self.assertEqual(self.out[1][kk][-1],
                             self.test_out[self.test_file_soy][kk])

    def test_load_ascii_data_int_cols(self):
        """ Test the general routine to load ASCII data assigning some
        columns as integers
        """

        int_keys = ["YEAR", "SOY", "NB"]
        self.out = ocb_igen.load_ascii_data(self.test_file_soy, 0,
                    header=self.headers[self.test_file_soy], int_cols=[0, 1, 2])

        # Test to ensure the output header equals the input header
        self.assertListEqual(self.out[0], self.headers[self.test_file_soy])

        # Test to see that the data keys are all in the header
        self.assertListEqual(sorted([kk for kk in self.test_out[
            self.test_file_soy].keys()]),
                             sorted([kk for kk in self.out[1].keys()]))

        # Test the length of the data file
        self.assertTupleEqual(self.out[1]['A'].shape, (75,))

        # Test the values of the last data line
        for kk in self.test_out[self.test_file_soy].keys():
            if kk in int_keys:
                self.assertEqual(self.out[1][kk][-1],
                                 int(self.test_out[self.test_file_soy][kk]))
            else:
                self.assertEqual(self.out[1][kk][-1],
                                 self.test_out[self.test_file_soy][kk])

        del int_keys

    def test_load_ascii_data_str_cols(self):
        """ Test the general routine to load ASCII data assigning some
        columns as strings
        """

        str_keys = ["YEAR", "SOY"]
        self.out = ocb_igen.load_ascii_data(self.test_file_soy, 0,
                    header=self.headers[self.test_file_soy], str_cols=[0, 1])

        # Test to ensure the output header equals the input header
        self.assertListEqual(self.out[0], self.headers[self.test_file_soy])

        # Test to see that the data keys are all in the header
        self.assertListEqual(sorted([kk for kk in self.test_out[
            self.test_file_soy].keys()]),
                             sorted([kk for kk in self.out[1].keys()]))

        # Test the length of the data file
        self.assertEqual(self.out[1]['A'].shape, (75,))

        # Test the values of the last data line
        for kk in self.test_out[self.test_file_soy].keys():
            if kk in str_keys:
                self.assertEqual(self.out[1][kk][-1], "{:.0f}".format(
                                     self.test_out[self.test_file_soy][kk]))
            else:
                self.assertEqual(self.out[1][kk][-1],
                                 self.test_out[self.test_file_soy][kk])

        del str_keys

    def test_load_ascii_data_w_datetime(self):
        """ Test the general routine to load ASCII data
        """

        self.out = ocb_igen.load_ascii_data(self.test_file_soy, 0,
                                            datetime_cols=[0,1],
                                            datetime_fmt="YEAR SOY",
                        header=self.headers[self.test_file_soy])

        # Test to ensure the output header equals the input header
        self.assertListEqual(self.out[0], self.headers[self.test_file_soy])

        # Test to see that the data keys are all in the header
        ktest = [kk for kk in self.test_out[self.test_file_soy].keys()]
        ktest.append("datetime")
        self.assertListEqual(sorted(ktest),
                             sorted([kk for kk in self.out[1].keys()]))

        # Test the length of the data file
        self.assertTupleEqual(self.out[1]['A'].shape, (75,))

        # Test the values of the last data line
        for kk in self.test_out[self.test_file_soy].keys():
            self.assertEqual(self.out[1][kk][-1],
                             self.test_out[self.test_file_soy][kk])

        # Test the datetime
        self.assertEqual(self.out[1]['datetime'][-1],
                         dt.datetime(2000,5,9,11,33,22))

        del ktest

if __name__ == '__main__':
    unittest.main()

