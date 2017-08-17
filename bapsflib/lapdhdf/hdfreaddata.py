# This file is part of the bapsflib package, a Python toolkit for the
# BaPSF group at UCLA.
#
# http://plasma.physics.ucla.edu/
#
# Copyright 2017 Erik T. Everson and contributors
#
# License:
#
# TODO: decide on input args for reading out HDF5 data
#

import h5py
import numpy as np


class ReadData(np.ndarray):
    """
    I wand self to be the nparray data.
    self should have a meta attribute that contains a dict() of
     metadata for the dataset.
    Metadata that should have:
        'hdf file'       -- HDF5 file name the data was retrieved from
        'dataset name'   -- name of the dataset
        'dataset path'   -- path to said dataset in the HDF5 file
        'crate'          -- crate in which the data was recorded on
        'bit'            -- bit resolution for the crate
        'sample rate'    -- tuple containing the sample rate
                            e.g. (100.0, 'MHz')
        'board'          -- board that the corresponding probe was
                            attached to
                            ~ can I make a 'brd' alias for 'board'
        'channel'        -- channel that the corresponding probe was
                            attached to
                            ~ can I make a 'ch' alias for 'channel'
        'voltage offset' -- voltage offset for the DAQ signal
        'probe name'     -- name of deployed probe...empty dict() item
                            for user to fill out for his/her needs
        'port'           -- 2-element tuple indicating which port the
                            probe was deployed on.
                            e.g. (19, 'W') => deployed on port 19 on the
                            west side of the machine.
                            Second elements descriptors should follow:
                            'T'  = top
                            'TW' = top-west
                            'W'  = west
                            'BW' = bottom-west
                            'B'  = bottom
                            'BE' = bottome-east
                            'E'  = east
                            'TE' = top-east

        Extracting Data
            dset = h5py.get() returns a view of the dataset (dset)
            From there, instantiating from dset will create a copy of
             the data. If you want to keep views then one could use
             dset.values.view().  The dset.vlaues is np.ndarray.
            To extract data, fancy indexing [::] can be used directly on
             dset or dset.values.

    """

    def __init__(self, hdf_file, *args, return_view=False):
        # return_view=False -- return a ndarray.view() to save on memory
        #                      when working with multiple datasets...
        #                      this needs to be thought out in more
        #                      detail

        # Define meta attribute
        self.metainfo = {'hdf file': None,
                         'dataset name': None,
                         'dataset path': None,
                         'crate': None,
                         'bit': None,
                         'sample rate': None,
                         'board': None,
                         'channel': None,
                         'voltage offset': None,
                         'probe name': None,
                         'port': (None, None)}

    def convert_to_v(self):
        """
        Convert DAQ signal from bits to voltage.
        :return:
        """
        pass

    def convert_to_t(self):
        """
        Convert DAQ signal dependent axis from index to time.
        :return:
        """
        pass

    def dt(self):
        """
        Return timestep dt from the 'sample rate' dict() item.
        :return:
        """
        pass

    def dv(self):
        """
        Return voltage-step from the 'bit' dict() item.
        :return:
        """
        pass

    def full_path(self):
        """
        Return full path of the dataset in the HDF5 file.
        :return:
        """
        pass