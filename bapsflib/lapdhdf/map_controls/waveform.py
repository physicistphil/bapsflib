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
# TODO: add 'dset name' to configs dict
#
import h5py
import numpy as np
import re

from .control_template import hdfMap_control_template


class hdfMap_control_waveform(hdfMap_control_template):
    """
    .. Warning::

        In development
    """
    def __init__(self, control_group):
        hdfMap_control_template.__init__(self, control_group)

        # define control type
        self.info['contype'] = 'waveform'

        # populate self.configs
        self._build_configs()

        # verify self.info and self.configs
        # self._verify_map()

    def _build_configs(self):
        # build configuration dictionaries
        # - assume all subgroups are control device configuration groups
        #   and their names correspond to the configuration name
        #
        for name in self.sgroup_names:
            # get configuration group
            cgroup = self.group[name]

            # get IP address
            # - ip gets returned as a np.bytes_ string
            #
            ip = cgroup.attrs['IP address']
            ip = ip.decode('utf-8')

            # get device (generator) name
            # - gdevice get returned as a np.bytes_ string
            #
            gdevice = cgroup.attrs['Generator type']
            gdevice = gdevice.decode('utf-8')

            # get command list
            # - cl gets returned as a np.bytes_ string
            # - remove trailing/leading whitespace
            #
            cl = cgroup.attrs['Waveform command list']
            cl = cl.decode('utf-8').splitlines()
            cl = [cls.strip() for cls in cl]
            # pattern = re.compile('(FREQ\s)(\d+\.\d+)')
            # cl_float = []
            # for val in cl:
            #     cl_re = re.search(pattern, val)
            #     cl_float.append(float(cl_re.group(2)))

            # assign values
            # 'command list': tuple(cl_float)
            self.configs[name] = {
                'IP address': ip,
                'device name': gdevice,
                'command list': cl,
                'cl pattern': None
            }

            # define 'dataset fields'
            self.configs[name]['dataset fields'] = [
                ('Shot number', '<u4'),
                ('Configuration name', 'U'),
                ('Command index', '<u4')
            ]

            # define 'dset field to numpy field'
            self.configs[name]['dset field to numpy field'] = [
                ('Shot number', ('shotnum', '<u4'), 0),
                ('Command index',
                 ('command', np.array(cl).dtype.str), 0)
            ]

            # Define 'dset name'
            self.configs[name]['dset name'] = \
                self.construct_dataset_name(name)

    def construct_dataset_name(self, *args):
        return 'Run time list'

    # @property
    # def name(self):
    #     """
    #     :return: name of control device
    #     :rtype: str
    #     """
    #     return 'Waveform'
