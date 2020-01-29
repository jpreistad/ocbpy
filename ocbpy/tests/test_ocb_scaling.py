#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2017, AGB & GC
# Full license can be found in License.md
#-----------------------------------------------------------------------------
""" Tests the ocb_scaling class and functions
"""

import numpy as np
from os import path
import sys
import unittest

import ocbpy

class TestOCBScalingMethods(unittest.TestCase):

    def setUp(self):
        """ Initialize the OCBoundary object using the test file, as well as
        the VectorData object
        """

        test_file = path.join(path.dirname(ocbpy.__file__), "tests",
                              "test_data", "test_north_circle")
        self.assertTrue(path.isfile(test_file))
        self.ocb = ocbpy.ocboundary.OCBoundary(filename=test_file,
                                               instrument='image')
        self.ocb.rec_ind = 27
        self.vdata = ocbpy.ocb_scaling.VectorData(0, self.ocb.rec_ind, 75.0,
                                                  22.0, aacgm_n=50.0,
                                                  aacgm_e=86.5, aacgm_z=5.0,
                                                  dat_name="Test",
                                                  dat_units="$m s^{-1}$")
        self.wdata = ocbpy.ocb_scaling.VectorData(0, self.ocb.rec_ind, 75.0,
                                                  22.0, aacgm_n=50.0,
                                                  aacgm_e=86.5, aacgm_z=5.0,
                                                  aacgm_mag=100.036243432,
                                                  dat_name="Test",
                                                  dat_units="$m s^{-1}$")
        self.zdata = ocbpy.ocb_scaling.VectorData(0, self.ocb.rec_ind, 87.2,
                                                  21.22, aacgm_n=0.0,
                                                  aacgm_e=0.0,
                                                  dat_name="Test Zero",
                                                  dat_units="$m s^{-1}$")

    def tearDown(self):
        del self.ocb, self.vdata, self.wdata, self.zdata

    def test_init_nez(self):
        """ Test the initialisation of the VectorData object without magnitude
        """
        self.assertAlmostEqual(self.vdata.aacgm_mag, 100.036243432)
        self.assertAlmostEqual(self.zdata.aacgm_mag, 0.0)

    def test_init_mag(self):
        """ Test the initialisation of the VectorData object with magnitude
        """
        self.assertAlmostEqual(self.wdata.aacgm_mag, 100.036243432)

    def test_init_failure(self):
        """ Test the initialisation of the VectorData object with inconsistent
        AACGM components
        """
        with self.assertRaisesRegexp(ValueError, "inconsistent AACGM"):
            self.wdata = ocbpy.ocb_scaling.VectorData(0, self.ocb.rec_ind, 75.0,
                                                      22.0, aacgm_mag=100.0,
                                                      dat_name="Test",
                                                      dat_units="$m s^{-1}$")

    def test_vector_repr_str(self):
        """ Test the VectorData print statement using repr and str """
        self.assertTrue(self.vdata.__repr__() == self.vdata.__str__())

    def test_vector_repr_no_scaling(self):
        """ Test the VectorData print statement without a scaling function """
        out = self.vdata.__repr__()

        if sys.version_info.major == 2:
            self.assertRegexpMatches(out, "Vector data:")
            self.assertRegexpMatches(out, "No magnitude scaling function")
        else:
            self.assertRegex(out, "Vector data:")
            self.assertRegex(out, "No magnitude scaling function")
        del out

    def test_vector_repr_with_scaling(self):
        """ Test the VectorData print statement with a scaling function """
        self.vdata.set_ocb(self.ocb, scale_func=ocbpy.ocb_scaling.normal_evar)
        out = self.vdata.__repr__()

        if sys.version_info.major == 2:
            self.assertRegexpMatches(out, "Vector data:")
            self.assertRegexpMatches(out, "Scaling function")
        else:
            self.assertRegex(out, "Vector data:")
            self.assertRegex(out, "Scaling function")

    def test_vector_bad_lat(self):
        """ Test the VectorData output with data from the wrong hemisphere """
        self.vdata.aacgm_lat *= -1.0
        self.vdata.set_ocb(self.ocb, scale_func=ocbpy.ocb_scaling.normal_evar)

        self.assertTrue(np.isnan(self.vdata.ocb_lat))
        self.assertTrue(np.isnan(self.vdata.ocb_mlt))
        self.assertTrue(np.isnan(self.vdata.r_corr))
        self.assertTrue(np.isnan(self.vdata.ocb_n))
        self.assertTrue(np.isnan(self.vdata.ocb_e))
        self.assertTrue(np.isnan(self.vdata.ocb_z))

    def test_haversine(self):
        """ Test implimentation of the haversine
        """
        self.assertEqual(ocbpy.ocb_scaling.hav(0.0), 0.0)
        self.assertEqual(ocbpy.ocb_scaling.hav(np.pi), 1.0)
        self.assertEqual(ocbpy.ocb_scaling.hav(-np.pi), 1.0)
        self.assertAlmostEqual(ocbpy.ocb_scaling.hav(2.0 * np.pi), 0.0)
        self.assertAlmostEqual(ocbpy.ocb_scaling.hav(-2.0 * np.pi), 0.0)

    def test_inverse_haversine(self):
        """ Test implimentation of the inverse haversine
        """
        self.assertEqual(ocbpy.ocb_scaling.archav(0.0), 0.0)
        self.assertEqual(ocbpy.ocb_scaling.archav(1.0), np.pi)
        
    def test_calc_large_pole_angle(self):
        """ Test to see that the OCB polar angle calculation is performed
        properly when the angle is greater than 90 degrees
        """
        self.zdata.ocb_aacgm_mlt = 1.260677777
        self.zdata.ocb_aacgm_lat = 83.99
        self.zdata.ocb_lat = 84.838777192
        self.zdata.ocb_mlt = 15.1110383783

        self.zdata.calc_vec_pole_angle()
        self.assertAlmostEqual(self.zdata.pole_angle, 91.72024697182087)
        
    def test_calc_vec_pole_angle(self):
        """ Test to see that the polar angle calculation is performed properly
        """
        self.vdata.ocb_aacgm_mlt = self.ocb.phi_cent[self.vdata.ocb_ind] / 15.0
        self.vdata.ocb_aacgm_lat = 90.0 - self.ocb.r_cent[self.vdata.ocb_ind]
        (self.vdata.ocb_lat, self.vdata.ocb_mlt,
         self.vdata.r_corr) = self.ocb.normal_coord(self.vdata.aacgm_lat,
                                                    self.vdata.aacgm_mlt)

        # Test the calculation of the test pole angle
        self.vdata.calc_vec_pole_angle()
        self.assertAlmostEqual(self.vdata.pole_angle, 8.67527923044)
        
        # If the measurement has the same MLT as the OCB pole, the angle is
        # zero.  This includes the AACGM pole and the OCB pole.
        self.vdata.aacgm_mlt = self.vdata.ocb_aacgm_mlt
        self.vdata.calc_vec_pole_angle()
        self.assertEqual(self.vdata.pole_angle, 0.0)

        # If the measurement is on the opposite side of the AACGM pole as the
        # OCB pole, then the angle will be 180 degrees
        self.vdata.aacgm_mlt = self.vdata.ocb_aacgm_mlt + 12.0
        self.vdata.calc_vec_pole_angle()
        self.assertEqual(self.vdata.pole_angle, 180.0)

        # Set the distance between the data point and the OCB is equal to the
        # distance between the AACGM pole and the OCB so that the triangles
        # we're examining are isosceles triangles.  If the triangles were flat,
        # the angle would be 46.26 degrees
        self.vdata.aacgm_mlt = 0.0
        self.vdata.aacgm_lat = self.vdata.ocb_aacgm_lat
        self.vdata.calc_vec_pole_angle()
        self.assertAlmostEqual(self.vdata.pole_angle, 46.2932179019)

        # Return to the default AACGM MLT value
        self.vdata.aacgm_mlt = 22.0

    def test_define_quadrants(self):
        """ Test the assignment of quadrants
        """
        # Set the initial values
        self.vdata.ocb_aacgm_mlt = self.ocb.phi_cent[self.vdata.ocb_ind] / 15.0
        self.vdata.ocb_aacgm_lat = 90.0 - self.ocb.r_cent[self.vdata.ocb_ind]
        (self.vdata.ocb_lat, self.vdata.ocb_mlt,
         self.vdata.r_corr) = self.ocb.normal_coord(self.vdata.aacgm_lat,
                                                     self.vdata.aacgm_mlt)
        self.vdata.calc_vec_pole_angle()
        
        # Get the test quadrants
        self.vdata.define_quadrants()
        self.assertEqual(self.vdata.ocb_quad, 1)
        self.assertEqual(self.vdata.vec_quad, 1)

    def test_define_quadrants_neg_adj_mlt(self):
        """ Test the quadrant assignment with a negative AACGM MLT """
        self.vdata.aacgm_mlt = -22.0
        self.vdata.set_ocb(self.ocb, scale_func=ocbpy.ocb_scaling.normal_evar)
        self.assertGreater(self.vdata.ocb_aacgm_mlt-self.vdata.aacgm_mlt, 24)
        self.assertEqual(self.vdata.ocb_quad, 1)
        self.assertEqual(self.vdata.vec_quad, 1)

    def test_define_quadrants_neg_north(self):
        """ Test the quadrant assignment with a vector pointing south """
        self.vdata.aacgm_n *= -1.0
        self.vdata.set_ocb(self.ocb, scale_func=ocbpy.ocb_scaling.normal_evar)
        self.assertEqual(self.vdata.ocb_quad, 1)
        self.assertEqual(self.vdata.vec_quad, 4)

    def test_calc_ocb_vec_sign(self):
        """ Test the calculation of the OCB vector signs
        """

        # Set the initial values
        self.vdata.ocb_aacgm_mlt = self.ocb.phi_cent[self.vdata.ocb_ind] / 15.0
        self.vdata.ocb_aacgm_lat = 90.0 - self.ocb.r_cent[self.vdata.ocb_ind]
        (self.vdata.ocb_lat, self.vdata.ocb_mlt,
         self.vdata.r_corr) = self.ocb.normal_coord(self.vdata.aacgm_lat,
                                                    self.vdata.aacgm_mlt)
        self.vdata.calc_vec_pole_angle()
        self.vdata.define_quadrants()

        vmag = np.sqrt(self.vdata.aacgm_n**2 + self.vdata.aacgm_e**2)
        self.vdata.aacgm_naz = np.degrees(np.arccos(self.vdata.aacgm_n / vmag))

        # Calculate the vector data signs
        vsigns = self.vdata.calc_ocb_vec_sign(north=True, east=True)
        self.assertTrue(vsigns['north'])
        self.assertTrue(vsigns['east'])

        del vmag, vsigns

    def test_scale_vec(self):
        """ Test the calculation of the OCB vector signs
        """

        # Set the initial values
        self.vdata.ocb_aacgm_mlt = self.ocb.phi_cent[self.vdata.ocb_ind] / 15.0
        self.vdata.ocb_aacgm_lat = 90.0 - self.ocb.r_cent[self.vdata.ocb_ind]
        (self.vdata.ocb_lat, self.vdata.ocb_mlt,
         self.vdata.r_corr) = self.ocb.normal_coord(self.vdata.aacgm_lat,
                                                    self.vdata.aacgm_mlt)
        self.vdata.calc_vec_pole_angle()
        self.vdata.define_quadrants()

        vmag = np.sqrt(self.vdata.aacgm_n**2 + self.vdata.aacgm_e**2)
        self.vdata.aacgm_naz = np.degrees(np.arccos(self.vdata.aacgm_n / vmag))

        # Scale the data vector
        self.vdata.scale_vector()

        # Test the North and East components
        self.assertAlmostEqual(self.vdata.ocb_n, 62.4751208491)
        self.assertAlmostEqual(self.vdata.ocb_e, 77.9686428950)
        
        # Test to see that the magnitudes and z-components are the same
        self.assertEqual(self.vdata.aacgm_mag, self.vdata.ocb_mag)
        self.assertEqual(self.vdata.ocb_z, self.vdata.aacgm_z)

        del vmag

    def test_scale_vec_z_zero(self):
        """ Test the calculation of the OCB vector sign with no vertical aacgm_z
        """
        # Re-assing the necessary variable
        self.vdata.aacmg_z = 0.0

        # Run the scale_vector routine
        self.vdata.set_ocb(self.ocb, scale_func=ocbpy.ocb_scaling.normal_evar)
        self.vdata.scale_vector()

        # Assess the ocb_z component
        self.assertEqual(self.vdata.ocb_z,
                         self.vdata.scale_func(0.0. self.vdata.unscaled_r,
                                               self.vdata.scaled_r))
        
    def test_set_ocb_zero(self):
        """ Test setting of OCB values for the VectorData object without any
        magnitude
        """
        # Set the OCB values without any E-field scaling, test to see that the
        # AACGM and OCB vector magnitudes are the same
        self.zdata.set_ocb(self.ocb)
        self.assertEqual(self.zdata.ocb_mag, 0.0)

    def test_set_ocb_none(self):
        """ Test setting of OCB values for the VectorData object
        """

        # Set the OCB values without any E-field scaling, test to see that the
        # AACGM and OCB vector magnitudes are the same
        self.vdata.set_ocb(self.ocb)
        self.assertEqual(self.vdata.aacgm_mag, self.vdata.ocb_mag)

    def test_set_ocb_evar(self):
        """ Test setting of OCB values for the VectorData object
        """

        # Set the OCB values with scaling for a variable proportional to
        # the electric field
        self.vdata.set_ocb(self.ocb, scale_func=ocbpy.ocb_scaling.normal_evar)
        self.assertAlmostEqual(self.vdata.ocb_mag, 88.1262660863)
        
    def test_set_ocb_curl_evar(self):
        """ Test setting of OCB values for the VectorData object
        """

        # Set the OCB values with scaling for a variable proportional to
        # the curl of the electric field
        self.vdata.set_ocb(self.ocb,
                           scale_func=ocbpy.ocb_scaling.normal_curl_evar)
        self.assertAlmostEqual(self.vdata.ocb_mag, 77.6423447186)

    def test_scaled_r(self):
        """ Test that the scaled radius is correct
        """
        self.vdata.set_ocb(self.ocb, None)
        self.assertEqual(self.vdata.scaled_r, 16.0)

    def test_unscaled_r(self):
        """ Test that the scaled radius is correct
        """
        self.vdata.set_ocb(self.ocb, None)
        self.assertEqual(self.vdata.unscaled_r, 14.09)

    def test_no_ocb_lat(self):
        """ Test failure when OCB latitude is not available"""

        self.vdata.ocb_lat = np.nan
        
        with self.assertRaisesRegexp(ValueError, 'OCB coordinates required'):
            self.vdata.scale_vector()

    def test_no_ocb_mlt(self):
        """ Test failure when OCB latitude is not available"""

        self.vdata.ocb_mlt = np.nan
        
        with self.assertRaisesRegexp(ValueError, 'OCB coordinates required'):
            self.vdata.scale_vector()

    def test_no_ocb_pole_location(self):
        """ Test failure when OCB latitude is not available"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.ocb_aacgm_mlt = np.nan
        
        with self.assertRaisesRegexp(ValueError, "OCB pole location required"):
            self.vdata.scale_vector()

    def test_no_ocb_pole_angle(self):
        """ Test failure when pole angle is not available"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.pole_angle = np.nan
        
        with self.assertRaisesRegexp(ValueError, \
                            "vector angle in poles-vector triangle required"):
            self.vdata.scale_vector()

    def test_bad_ocb_quad(self):
        """ Test failure when OCB quadrant is wrong"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.ocb_quad = -1
        
        with self.assertRaisesRegexp(ValueError, "OCB quadrant undefined"):
            self.vdata.calc_ocb_polar_angle()

    def test_bad_vec_quad(self):
        """ Test failure when vector quadrant is wrong"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.vec_quad = -1
        
        with self.assertRaisesRegexp(ValueError, "Vector quadrant undefined"):
            self.vdata.calc_ocb_polar_angle()

    def test_bad_quad_polar_angle(self):
        """ Test failure when quadrant polar angle is bad"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.aacgm_naz = np.nan
        
        with self.assertRaisesRegexp(ValueError, "AACGM polar angle undefined"):
            self.vdata.calc_ocb_polar_angle()

    def test_bad_quad_pole_angle(self):
        """ Test failure when quandrant pole angle is bad"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.pole_angle = np.nan
        
        with self.assertRaisesRegexp(ValueError, "Vector angle undefined"):
            self.vdata.calc_ocb_polar_angle()

    def test_bad_calc_vec_sign_direction(self):
        """ Test calc_vec_sign failure when no direction is provided"""

        self.vdata.set_ocb(self.ocb, None)
        
        with self.assertRaisesRegexp(ValueError,
                                     "must set at least one direction"):
            self.vdata.calc_ocb_vec_sign()

    def test_bad_calc_sign_ocb_quad(self):
        """ Test calc_vec_sign failure with bad OCB quadrant"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.ocb_quad = -1
        
        with self.assertRaisesRegexp(ValueError, "OCB quadrant undefined"):
            self.vdata.calc_ocb_vec_sign(north=True)

    def test_bad_calc_sign_vec_quad(self):
        """ Test calc_vec_sign failure with bad vector quadrant"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.vec_quad = -1
        
        with self.assertRaisesRegexp(ValueError, "Vector quadrant undefined"):
            self.vdata.calc_ocb_vec_sign(north=True)

    def test_bad_calc_sign_polar_angle(self):
        """ Test calc_vec_sign failure with bad polar angle"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.aacgm_naz = np.nan
        
        with self.assertRaisesRegexp(ValueError, "AACGM polar angle undefined"):
            self.vdata.calc_ocb_vec_sign(north=True)

    def test_bad_calc_sign_pole_angle(self):
        """ Test calc_vec_sign failure with bad pole angle"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.pole_angle = np.nan
        
        with self.assertRaisesRegexp(ValueError, "Vector angle undefined"):
            self.vdata.calc_ocb_vec_sign(north=True)

    def test_bad_calc_vec_pole_angle_mlt(self):
        """Test calc_vec_pole_angle failure with bad AACGM MLT"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.aacgm_mlt = np.nan
        
        with self.assertRaisesRegexp(ValueError,
                                     "AACGM MLT of Vector undefinded"):
            self.vdata.calc_vec_pole_angle()

    def test_bad_calc_vec_pole_angle_ocb_mlt(self):
        """Test calc_vec_pole_angle failure with bad OCB MLT"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.ocb_aacgm_mlt = np.nan
        
        with self.assertRaisesRegexp(ValueError,
                                     "AACGM MLT of OCB pole is undefined"):
            self.vdata.calc_vec_pole_angle()

    def test_bad_calc_vec_pole_angle_ocb_mlat(self):
        """Test calc_vec_pole_angle failure with bad OCB latitude"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.ocb_aacgm_lat = np.nan
        
        with self.assertRaisesRegexp(ValueError,
                                     "AACGM latitude of OCB pole is undefined"):
            self.vdata.calc_vec_pole_angle()

    def test_bad_calc_vec_pole_angle_vec_mlat(self):
        """Test calc_vec_pole_angle failure with bad vector latitude"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.aacgm_lat = np.nan
        
        with self.assertRaisesRegexp(ValueError,
                                     "AACGM latitude of Vector undefined"):
            self.vdata.calc_vec_pole_angle()

    def test_bad_define_quandrants_pole_mlt(self):
        """Test define_quadrants failure with bad pole MLT"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.ocb_aacgm_mlt = np.nan
        
        with self.assertRaisesRegexp(ValueError, "OCB pole location required"):
            self.vdata.define_quadrants()

    def test_bad_define_quandrants_vec_mlt(self):
        """Test define_quadrants failure with bad vector MLT"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.aacgm_mlt = np.nan
        
        with self.assertRaisesRegexp(ValueError,
                                     "Vector AACGM location required"):
            self.vdata.define_quadrants()

    def test_bad_define_quandrants_pole_angle(self):
        """Test define_quadrants failure with bad pole angle"""

        self.vdata.set_ocb(self.ocb, None)
        self.vdata.pole_angle = np.nan
        
        with self.assertRaisesRegexp(ValueError, \
                            "vector angle in poles-vector triangle required"):
            self.vdata.define_quadrants()

if __name__ == '__main__':
    unittest.main()

