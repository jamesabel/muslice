
import os
import collections

import muslice.util

__application_name__ = 'muslice'
__author__ = 'James Abel'
__application_version__ = '0.0.0'


class MuSlice:
    def __init__(self, input_folder, mono_files_folder, convert, mix):
        self._input_folder = input_folder
        self._mono_files_folder = mono_files_folder
        self._convert = convert
        self._mix = mix
        self._groups = collections.defaultdict(list)

    def run(self):
        for r, ds, fs in os.walk(self._input_folder):
            for f in fs:
                self._groups[self.file_to_group(f)].append(os.path.join(r, f))
        if not self._convert and not self._mix:
            print('Error - nothing to do!  Execute -h for help')
        if self._convert:
            muslice.util.make_n_aural_files(self._groups, self._mono_files_folder)
        if self._mix:
            muslice.util.mix(self._mono_files_folder)

    def file_to_group(self, file_name):
        # isolate the group name creation in case we want to change it in the future (it's really simple now)
        return file_name[7:11]