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

from .hdfchecks import hdfCheck
from .hdfreaddata import hdfReadData
from .hdfreadcontrol import hdfReadControl


class File(h5py.File):
    """
    Open a HDF5 File.

    see :mod:`h5py` documentation for :class:`h5py.File` details:
    http://docs.h5py.org/en/latest/

    :param str name: Name of file (`str` or `unicode`)
    :param str mode: Mode in which to open the file.
        (default 'r' read-only)
    :param driver: File driver to use
    :param libver: Compatibility bounds
    :param userblock_size: Size (in bytes) of the user block. If
        nonzero, must be a power of 2 and at least 512.
    :param swmr: Single Write, Multiple Read
    :param kwargs: Driver specific keywords
    """
    def __init__(self, name, mode='r', driver=None, libver=None,
                 userblock_size=None, swmr=False, **kwargs):
        # TODO: re-work the argument pass through to h5py.File
        # TODO: add keyword save_report
        # - this will save the hdfChecks report to a text file alongside
        #   the HDF5 file
        # TODO: add keyword silent_report
        # - this will prevent the report from printing to screen, but
        #   does not affect save_report
        #
        h5py.File.__init__(self, name, mode, driver, libver,
                           userblock_size, swmr, **kwargs)

        print('Begin HDF5 Quick Report:')
        self.__file_checks = hdfCheck(self)

    @property
    def exp_descr(self):
        """Experimental description (from the HDF5 file)"""
        try:
            edescr = self['Raw data + config'].attrs['Description']
            edescr = edescr.decode('utf-8').splitlines()
        except KeyError:
            edescr = ''
        return edescr

    @property
    def file_map(self):
        """
        HDF5 file mappings
        (:class:`bapsflib.lapdhdf.hdfmapper.hdfMap`)
        """
        return self.__file_checks.get_hdf_mapping()

    @property
    def list_file_items(self):
        """
        list of absolute paths for all items (Groups and Datasets) in
        the HDF5 file
        """
        some_list = []
        self.visit(some_list.append)
        return some_list

    @property
    def list_msi(self):
        """
        list of all mapped MSI diagnostics
        """
        return list(self.file_map.msi)

    @property
    def list_digitizers(self):
        """
        list of all mapped digitizers
        """
        return list(self.file_map.digitizers)

    @property
    def list_controls(self):
        """
        list of all mapped control devices
        """
        return list(self.file_map.controls)

    def read_data(self, board, channel,
                  index=slice(None), shotnum=slice(None),
                  digitizer=None, adc=None,
                  config_name=None, keep_bits=False, add_controls=None,
                  intersection_set=True, silent=False,
                  **kwargs):
        # TODO: docstrings and code block needs updating
        """
        Provides access to
        :class:`~bapsflib.lapdhdf.hdfreaddata.hdfReadData` to extract
        data from a specified digitizer dataset in the HDF5 file and,
        if requested, mate control device data to the extracted
        digitizer data. See
        :class:`~bapsflib.lapdhdf.hdfreaddata.hdfReadData` for more
        detail.

        :param int board: digitizer board number
        :param int channel: digitizer channel number
        :param index: dataset row index
        :type index: int, list(int), slice()
        :param shotnum: HDF5 global shot number
        :type shotnum: int, list(int), slice()
        :param str digitizer: name of digitizer
        :param str adc: name of the digitizer's analog-digital converter
        :param str config_name: name of digitizer configuration
        :param bool keep_bits: :code:`True` for output in bits,
            :code:`False` (default) for output in voltage
        :param add_controls: a list of strings and/or 2-element tuples
            indicating control device data to be mated to the digitizer
            data. (see
            :class:`~bapsflib.lapdhdf.hdfreaddata.hdfReadData`
            for details)
        :type add_controls: [str, (str, val), ]
        :param bool intersection_set: :code:`True` (default) forces the
            returned array to only contain shot numbers that are in the
            intersection of :data:`shotnum`, the digitizer dataset, and
            all the control device datasets. (see
            :class:`~bapsflib.lapdhdf.hdfreaddata.hdfReadData`
            for details)
        :param bool silent: :code:`False` (default). Set :code:`True` to
            suppress command line printout of soft-warnings
        :return: extracted data from digitizer (and control devices)
        :rtype: :class:`~bapsflib.lapdhdf.hdfreaddata.hdfReadData`
        """
        #
        # :param add_controls: a list of strings and/or 2-element tuples
        #     indicating control device data to be mated to the
        #     digitizer data. If an element is a string, then that
        #     string is the name of the control device, If an element is
        #     a 2-element tuple, then the 1st element is the name of the
        #     control device and the 2nd element is a unique specifier
        #     for that control device.
        # :param intersection_set: :code:`True` (default) ensures the
        #     returned array only contains shot numbers that are found
        #     in the digitizer dataset and all added control device
        #     datasets. :code:`False` will cause the returned array to
        #     contain shot numbers specified by :data:`shotnum` or, when
        #     :data:`index` is used, the matching shot numbers in the
        #     digitizer dataset specified by :data:`index`
        #
        # TODO: write docstrings
        #
        return hdfReadData(self, board, channel,
                           index=index,
                           shotnum=shotnum,
                           digitizer=digitizer,
                           adc=adc,
                           config_name=config_name,
                           keep_bits=keep_bits,
                           add_controls=add_controls,
                           intersection_set=intersection_set,
                           silent=silent,
                           **kwargs)

    def read_controls(self, controls,
                      shotnum=slice(None), intersection_set=True,
                      silent=False, **kwargs):
        """
        Reads data out of control device datasets.  See
        :class:`~bapsflib.lapdhdf.hdfreadcontrol.hdfReadControl` for
        more detail.

        :param controls: a list of strings and/or 2-element tuples
            indicating the control device(s). (see
            :class:`~bapsflib.lapdhdf.hdfreadcontrol.hdfReadControl`
            for details)
        :type controls: [str, (str, val), ]
        :param shotnum: HDF5 file shot number(s) indicating data
            entries to be extracted
        :type shotnum: int, list(int), slice()
        :param bool intersection_set: :code:`True` (DEFAULT) will force
            the returned shot numbers to be the intersection of
            :data:`shotnum` and the shot numbers contained in each
            control device dataset. :code:`False` will return the union
            instead of the intersection  (see
            :class:`~bapsflib.lapdhdf.hdfreadcontrol.hdfReadControl`
            for details)
        :param bool silent: :code:`False` (DEFAULT).  Set :code:`True`
            to suppress command line printout of soft-warnings
        :return: extracted data from control device(s)
        :rtype: :class:`~bapsflib.lapdhdf.hdfreadcontrol.hdfReadControl`

        :Example:

            >>> # open HDF5 file
            >>> f = File('sample.hdf5')
            >>>
            >>> # list control devices
            >>> f.list_controls
            ['6K Compumotor', 'Waveform']
            >>>
            >>> # list '6K Compumotor' configurations
            >>> list(f.file_map.controls['6K Compumotor'].configs)
            [2, 3]
            >>>
            >>> # extract all '6k Compumotor', configuration 3 data
            >>> cdata = f.read_controls([('6K Compumotor', 3)])
            >>>
            >>> # list 'Waveform' configurations
            >>> list(f.file_map.controls['Waveform'].configs)
            ['config01']
            >>>
            >>> # extract 'Waveform' data
            >>> cdata = f.read_controls(['Waveform'])
            >>>
            >>> # extract both 'Waveform' and '6K Compumotor'
            >>> controls = ['Waveform', ('6K Compumotor', 2)]
            >>> cdata = f.read_controls(controls)

        """
        return hdfReadControl(self, controls,
                              shotnum=shotnum,
                              intersection_set=intersection_set,
                              silent=silent,
                              **kwargs)

    def save_report(self, sname):
        """
        Save a HDF5 file report based on the HDF5 mappings.

        :param sname: save file name

        .. Warning::

            Not implemented yet.
        """
        # TODO: implement this save report
        raise NotImplementedError
