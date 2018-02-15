#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the bapsflib package, a Python toolkit for the
# BaPSF group at UCLA.
#
# http://plasma.physics.ucla.edu/
#
# Copyright 2017-2018 Erik T. Everson and contributors
#
# License: Standard 3-clause BSD; see "LICENSES/LICENSE.txt" for full
#   license terms and contributor agreement.
#
import h5py
import numpy as np
import unittest as ut

from ..map_controls.waveform import hdfMap_control_waveform
from ..files import File
from ..hdfreadcontrol import condition_shotnum_list, condition_controls

from bapsflib.lapdhdf.tests import FauxHDFBuilder


class TestConditionShotnumList(ut.TestCase):
    """Test Case for condition_shotnum_list"""

    def setUp(self):
        self.f = FauxHDFBuilder(
            add_modules={'Waveform': {'n_configs': 1, 'sn_size': 100}})
        self.mod = self.f.modules['Waveform']

    def tearDown(self):
        self.f.cleanup()

    @property
    def cgroup(self):
        return self.f['Raw data + config/Waveform']

    @property
    def map(self):
        return hdfMap_control_waveform(self.cgroup)

    def test_simple_dataset(self):
        """
        Tests for a dataset containing recorded data for a single
        configuration.
        """
        if self.mod.knobs.n_configs != 1:
            self.mod.knobs.n_configs = 1

        # test zero shot number
        self.assertZeroSN()

        # test negative shot number cases
        self.assertNegativeSN()

        # test in range shot number cases
        self.assertInRangeSN()

        # test out of range shot number cases
        self.assertOutRangeSN()

    def test_complex_dataset(self):
        """
        Tests for a dataset containing recorded data for a multiple
        configurations.
        """
        if self.mod.knobs.n_configs != 3:
            self.mod.knobs.n_configs = 3

        # test zero shot number
        self.assertZeroSN()

        # test negative shot number cases
        self.assertNegativeSN()

        # test in range shot number cases
        self.assertInRangeSN()

        # test out of range shot number cases
        self.assertOutRangeSN()

    def assertZeroSN(self):
        """Assert the zero shot number case."""
        og_shotnum = [0]
        cdset = self.cgroup['Run time list']
        shotnumkey = 'Shot number'
        for cspec in self.map.configs:
            self.assertRaises(ValueError, condition_shotnum_list,
                              og_shotnum, cdset, shotnumkey, self.map,
                              cspec)

    def assertNegativeSN(self):
        """Assert negative shot number cases."""
        shotnum_list = [
            [-1],
            [-10, -5, 0]
        ]
        cdset = self.cgroup['Run time list']
        shotnumkey = 'Shot number'
        for og_shotnum in shotnum_list:
            for cspec in self.map.configs:
                self.assertRaises(ValueError, condition_shotnum_list,
                                  og_shotnum, cdset, shotnumkey,
                                  self.map, cspec)

    def assertInRangeSN(self):
        """
        Assert shot numbers cases within range of dataset shot numbers.
        """
        shotnum_list = [
            [10],
            [50, 51],
            [50, 60],
            [1, self.mod.knobs.sn_size],
            [50, 51, 52, 53, 54, 55, 56, 57, 58, 59],
            [1, 11, 21, 31, 41, 51, 61, 71, 81, 91]
        ]
        cdset = self.cgroup['Run time list']
        shotnumkey = 'Shot number'
        configkey = 'Configuration name'
        for og_shotnum in shotnum_list:
            for cspec in self.map.configs:
                index, shotnum, sni = \
                    condition_shotnum_list(og_shotnum, cdset,
                                           shotnumkey,
                                           self.map, cspec)
                self.assertSNSuite(og_shotnum,
                                   index, shotnum, sni,
                                   cdset, shotnumkey,
                                   configkey, cspec)

    def assertOutRangeSN(self):
        """
        Assert shot number cases where some shot numbers are out of
        range of the dataset shotnumbers.
        """
        # - one above largest shot number
        # - out of range above (sn_size+1) and below (-1)
        # - out of range below (-5, -1, 0) and valid
        # - out of range above (sn_size+1, sn_size+10, sn_size+100)
        #   and valid
        # - out of range below (-5, -1, 0), above (sn_size+1,
        #   sn_size+10, sn_size+100), and valid
        #
        shotnum_list = [
            [self.mod.knobs.sn_size + 1],
            [-1, self.mod.knobs.sn_size + 1],
            [-5, -1, 0, 10, 15],
            [10, 15, self.mod.knobs.sn_size + 1,
             self.mod.knobs.sn_size + 10,
             self.mod.knobs.sn_size + 100],
            [-5, -1, 0, 10, 15, self.mod.knobs.sn_size + 1,
             self.mod.knobs.sn_size + 10,
             self.mod.knobs.sn_size + 100]
        ]
        cdset = self.cgroup['Run time list']
        shotnumkey = 'Shot number'
        configkey = 'Configuration name'
        for og_shotnum in shotnum_list:
            for cspec in self.map.configs:
                index, shotnum, sni = \
                    condition_shotnum_list(og_shotnum, cdset,
                                           shotnumkey,
                                           self.map, cspec)
                self.assertSNSuite(og_shotnum,
                                   index, shotnum, sni,
                                   cdset, shotnumkey,
                                   configkey, cspec)

    def assertSNSuite(self, og_shotnum, index, shotnum, sni,
                      cdset, shotnumkey, configkey, cspec):
        """Suite of assertions for shot number conditioning"""
        # all return variables should be np.ndarray
        self.assertTrue(isinstance(index, np.ndarray))
        self.assertTrue(isinstance(shotnum, np.ndarray))
        self.assertTrue(isinstance(sni, np.ndarray))

        # all should be 1D arrays
        self.assertEqual(index.shape[0], index.size)
        self.assertEqual(shotnum.shape[0], shotnum.size)
        self.assertEqual(sni.shape[0], sni.size)

        # equate array sizes
        self.assertEqual(shotnum.size, sni.size)
        self.assertEqual(np.count_nonzero(sni), index.size)

        # all shotnum > 0
        self.assertTrue(np.all(np.where(shotnum > 0, True, False)))

        # all og_shotnum > 0 in shotnum
        og_arr = np.array(og_shotnum)
        og_i = np.where(og_arr > 0)[0]
        if og_i.size != 0:
            self.assertTrue(np.all(np.isin(shotnum, og_arr[og_i])))
            self.assertTrue(np.all(np.isin(og_arr[og_i], shotnum)))
        else:
            # condtion_shotnum_list should have thrown a ValueError
            # since no valid shot number was originally passed in
            raise RuntimeError(
                'something went wrong, `condition_shotnum_list` should '
                'have thrown a ValueError and shotnum should be empty, '
                'shotnum.size = {}'.format(shotnum.size))

        # all 0 < og_shotnum <= sn_size in shotnum[sni]
        # - this would be incorrect if the dataset has jumps in the
        #   recorded shot numbers
        #
        og_i1 = og_i
        og_i2 = np.where(og_arr <= self.mod.knobs.sn_size)[0]
        if og_i1.size != 0 and og_i2.size != 0:
            og_i = og_i1[np.isin(og_i1, og_i2)]
            self.assertTrue(np.all(np.isin(shotnum[sni], og_arr[og_i])))
            self.assertTrue(np.all(np.isin(og_arr[og_i], shotnum[sni])))
        else:
            # shotnum[sni].size should be 0
            # - ie: all elements of sni should be false
            self.assertTrue(np.all(np.logical_not(sni)))

        # shotnum[sni] = cdset[index, shotnumkey]
        if index.size != 0:
            self.assertTrue(np.array_equal(
                shotnum[sni], cdset[index.tolist(), shotnumkey]))
        else:
            self.assertEqual(shotnum[sni].size, 0)

        # ensure correct config is grabbed
        if index.size != 0:
            cname_arr = cdset[index.tolist(), configkey]
            for name in cname_arr:
                self.assertEqual(name.decode('utf-8'), cspec)


class TestConditonControls(ut.TestCase):
    """Test Case for condition_controls"""
    # What to test:
    # 1. passing of non lapdhdf.File object
    #    - raises AttributeError
    # 2. passing of controls as None (or not a list)
    #    - raises TypeError
    # 3. HDF5 file with no controls
    #    - raises AttributeError
    # 4. HDF5 file with one control
    #    - pass controls with
    #      a. just control name, no config
    #      b. control name and valid config
    #      c. control name and invalid config
    #      d. two control names
    # 5. HDF5 file with multiple controls
    #
    def setUp(self):
        self.f = FauxHDFBuilder(
            add_modules={'Waveform': {'n_configs': 3,
                                      'sn_size': 100},
                         '6K Compumotor': {'n_configs': 2,
                                           'sn_size': 100}})

    def tearDown(self):
        self.f.cleanup()

    @property
    def lapdf(self):
        return File(self.f.filename)

    def test_simple_puts(self):
        # hdf_file = h5py.File (but NOT lapdhdf.File)
        # controls = None
        self.assertRaises(AttributeError,
                          condition_controls, self.f, None)

        # hdf_file = lapdhdf.File
        # controls = empty list
        self.assertRaises(ValueError,
                          condition_controls, self.lapdf, [])

        # hdf_file = lapdhdf.File
        # controls = not a list
        self.assertRaises(TypeError,
                          condition_controls, self.lapdf, None)

    def test_file_w_one_control(self):
        # set one control device
        modules = list(self.f.modules.keys())
        for mod in modules:
            self.f.remove_module(mod)
        self.f.add_module('Waveform', {'n_configs': 1, 'sn_size': 100})

        con_list = [
            ['Waveform'],
            ['Waveform', '6K Compumotor'],
            [('Waveform', 'config01')],
            [('Waveform', 'config01'), ('Waveform', 'config02')],
            [('Waveform', 'config01'), '6K Compumotor']
        ]
        # ------ Waveform w/ one Configuration ------
        # conditions that work
        con_list = [
            ['Waveform'],
            [('Waveform', 'config01')]
        ]
        for og_con in con_list:
            self.assertEqual(
                condition_controls(self.lapdf, og_con),
                [('Waveform', 'config01')])

        # conditions that raise TypeError
        con_list = [
            ['Waveform', 'config01'],
            ['Waveform', ('Waveform', 'config01')],
            ['Waveform', '6K Compumotor']
        ]
        for og_con in con_list:
            self.assertRaises(TypeError,
                              condition_controls, self.lapdf, og_con)

        # ------ Waveform w/ three Configurations ------
        self.f.modules['Waveform'].knobs.n_configs = 3

        # conditions that work
        con_list = [
            [('Waveform', 'config01')],
            [('Waveform', 'config02')]
        ]
        for og_con in con_list:
            self.assertEqual(
                condition_controls(self.lapdf, og_con),
                og_con)

        # conditions that raise TypeError
        con_list = [
            ['Waveform'],
            ['Waveform', '6K Compumotor'],
            ['6K Compumotor', ('Waveform', 'config01')],
        ]
        for og_con in con_list:
            self.assertRaises(TypeError,
                              condition_controls, self.lapdf,
                              og_con)

    def test_file_w_no_controls(self):
        # remove all control devices
        modules = list(self.f.modules.keys())
        if len(modules) != 0:
            for mod in modules:
                self.f.remove_module(mod)

        self.assertRaises(AttributeError,
                          condition_controls, self.lapdf, [])


if __name__ == '__main__':
    ut.main()
