
import os
import json
import datetime
import getpass

import muslice.logger as logger


class Config:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self._options = {}
        self._set_defaults()

        if os.path.exists(config_file_path):
            self._read()
        else:
            logger.log.info('creating : %s' % config_file_path)
            self.write()

    def _read(self):
        logger.log.info('reading : %s' % self.config_file_path)
        with open(self.config_file_path) as config_file:
            options_from_file = json.load(config_file)
        for option_from_file in options_from_file:
            self._options[option_from_file] = options_from_file[option_from_file]

    def write(self):
        with open(self.config_file_path, 'w') as config_file:
            json.dump(self._options, config_file, indent=2)

    def get(self, key):
        return self._options[key]

    def get_all(self):
        return self._options

    def set(self, key, value):
        self._read()
        self._options[key] = value
        self.write()

    def _set_defaults(self):
        self._options['meter_window'] = 3.0  # seconds
        self._options['program_threshold'] = -15.0  # at or above is regarded as program material (non-silence) - in dB
        self._options['silence_threshold'] = -30.0  # at or below is regarded as silence - in dB
        self._options['minimum_segment_length'] = 2.0 * 60.0  # assumed minimum song length in seconds

        # 'max' = use max meter value across all the channels
        # 'aggregate' = use all the transitions from all the channels, and rely on the coalescing to deduce one transition
        self._options['threshold_technique'] = 'max'

        self._options['ignore'] = []  # list of recording strings to ignore - provide places for the user to fill in
        self._options['source_folder'] = ''  # path to the original source wave files (e.g. what was copied from the TASCAM recorder)
        self._options['output_folder'] = 'output'  # path to the output folder
        self._options['max_threads'] = 2  # max number of threads to use during conversion

        # a few convenience things ...
        self._options['creation_file_path'] = self.config_file_path  # for convenience
        self._options['creation_utc_timestamp'] = str(datetime.datetime.utcnow())  # for convenience
        self._options['creation_user'] = getpass.getuser()  # for convenience

        # for putting up in the public cloud
        # get this when you create a public URL, e.g. for dropbox it's of the form:
        # https://dl.dropboxusercontent.com/u/<dropbox_id>
        self._options['cloud_base_url'] = 'https://your_public_cloud_base_URL'
        self._options['cloud_base_url_comment'] = 'e.g. https://dl.dropboxusercontent.com/u/<dropbox_id>'

        # MP3 bit rate
        self._options['bit_rate_kbps'] = 384
