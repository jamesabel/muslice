
import os
import collections
import shutil
import math

from scipy.io import wavfile
import numpy as np

from muslice import wav_util
from muslice import muslice_util
from muslice import plotting
from muslice import logger
from muslice import config
from muslice import mt_level_meter
from muslice import level_meter
from muslice import split_files
from muslice import folders
from muslice import to_mp3

__application_name__ = 'muslice'
__author__ = 'James Abel'
__application_version__ = '0.0.0'


class MuSlice:
    def __init__(self, config_file_path, nuke):
        self._config = config.Config(config_file_path)
        self._source_folder = self._config.get("source_folder")

        self._output_root = self._config.get("output_folder")

        if nuke:
            s = 'nuking : removing folder : "%s"' % self._output_root
            logger.log.info(s)
            print(s)
            try:
                shutil.rmtree(self._output_root)
            except FileNotFoundError:
                pass

        self._recordings = collections.defaultdict(list)
        logger.log.info('config : %s' % str(self._config.get_all()))

    @muslice_util.time_it
    def run(self):

        if not os.path.exists(self._source_folder):
            print('error : source folder "%s" does not exist' % self._source_folder)
            return

        # Use the 'ignore' list to avoid any extraneous files that may exist but you don't want to delete
        # since you may eventually want to get back to them.  For example, there may be some test or sound check
        # songs recorded to separate wav files that are not currently interesting, so put them in the ignore list.
        # Later on if you decide these are actually interesting then you can remove them from the ignore list
        # and process them.
        ignore_list = self._config.get('ignore')
        for ignore in ignore_list:
            if len(ignore) > 0:
                s = 'ignoring files containing : "%s"' % ignore
                logger.log.info(s)
                print('note : %s (from "ignore" list in %s)' % (s, self._config.config_file_path))

        for r, ds, fs in os.walk(self._source_folder):
            for f in fs:
                if not any([p in f for p in ignore_list]):
                    recording, _ = muslice_util.file_name_to_info(f)
                    if recording:
                        self._recordings[recording].append(os.path.join(r, f))

        # convert recorded wav files to N mono wav files
        split_files.make_mono_files(self._recordings, self._output_root, max_threads=self._config.get('max_threads'))

        s = 'processing recordings : %s' % ','.join(self._recordings)
        logger.log.info(s)
        print('note : %s' % s)

        # break the wav files up into songs
        for recording in self._recordings:
            self.slice(recording)

        html = to_mp3.to_mp3(self._output_root, self._config.get("bit_rate_kbps"), self._config.get("cloud_base_url"))
        with open(os.path.join(self._output_root, 'mp3.html'), 'w') as f:
            f.write(html)

    @muslice_util.time_it
    def slice(self, recording):
        meters = level_meter.level_meter_folder(folders.mono_wav_fp_folder(self._output_root, recording),
                                                folders.mono_meters_folder(self._output_root, recording),
                                                self._config.get('meter_window'))

        number_of_channels = len(meters)

        # Make the level of all channels more equal (in other words, turn up the weak signals so they
        # are all even).  Each channel's meter will have a max RMS (windowed) of 0.0 dB.
        norm_meters = {}
        for channel_number in range(0, len(meters)):
            max_db = max(meters[channel_number]['rms_db'])
            logger.log.info('%s : channel %d max dB is %f' % (recording, channel_number, max_db))
            norm_meters[channel_number] = [db - max_db for db in meters[channel_number]['rms_db']]
        # write out a graph of the normalized meters
        meters_folder = folders.mono_meters_folder(self._output_root, recording)
        os.makedirs(meters_folder, exist_ok=True)
        norm_graph_file_path = os.path.join(meters_folder, "TASCAM_%s_norm.png" % recording)
        plotting.plot_meters(norm_meters, norm_graph_file_path)

        # determine where the transitions are
        logger.log.info('%s : starting to determine transistions' % recording)
        transitions = {}
        program_threshold = self._config.get('program_threshold')
        silence_threshold = self._config.get('silence_threshold')
        trans = set()
        threshold_technique = self._config.get('threshold_technique')
        if threshold_technique == 'aggregate':
            for channel_number in range(0, number_of_channels):
                # start with a 'transition' at the beginning
                transitions[channel_number] = [0]
                meter_measurement_count = 0
                is_program = False
                for meter_value in norm_meters[channel_number]:
                    # print(meter_measurement_count, meter_value)
                    if meter_value > program_threshold and not is_program:
                        is_program = True
                        trans.add(meter_measurement_count)
                    elif meter_value < silence_threshold and is_program:
                        is_program = False
                        trans.add(meter_measurement_count)
                    meter_measurement_count += 1
            trans = sorted(trans)
        elif threshold_technique == 'max':
            trans = []
            max_norm_meter = []
            for meter_sample_number in range(0, len(norm_meters[0])):
                v = norm_meters[0][meter_sample_number]
                for channel_number in range(1, number_of_channels):
                    v = max(v, norm_meters[channel_number][meter_sample_number])
                max_norm_meter.append(v)
            max_graph_file_path = os.path.join(meters_folder, "TASCAM_%s_max.png" % recording)
            plotting.plot_meters({'max': max_norm_meter}, max_graph_file_path)
            is_program = False
            meter_measurement_count = 0
            for meter_value in max_norm_meter:
                if meter_value > program_threshold and not is_program:
                    is_program = True
                    trans.append(meter_measurement_count)
                elif meter_value < silence_threshold and is_program:
                    is_program = False
                    trans.append(meter_measurement_count)
                meter_measurement_count += 1
        else:
            raise ValueError

        # coalesce the transitions across all channels to create transitions for the overall recording
        logger.log.info('%s : starting coalesce' % recording)
        logger.log.info('%s  : initial trans : %s (sec)' % (recording, str(trans)))
        new_trans = []
        proposed_trans = []
        for tran in trans:
            if len(proposed_trans) > 0 and tran > (proposed_trans[0] + self._config.get('minimum_segment_length')):
                # averaging the beginning and end seems to be better than averaging all the transitions together
                average = (proposed_trans[0] + proposed_trans[-1]) / 2.0
                # average = math.fsum(proposed_trans)/float(len(proposed_trans))

                new_trans.append(average)
                proposed_trans = []
            proposed_trans.append(tran)
        if len(proposed_trans) > 0:
            average = math.fsum(proposed_trans) / float(len(proposed_trans))
            new_trans.append(average)

        # Insert a 'transition' at the very beginning and very end so we have a start and end when we separate the
        # wav files.
        transitions = [0] + new_trans[1:]
        end = len(meters[0]['rms_db'])
        if end - transitions[-1] >= self._config.get('minimum_segment_length'):
            transitions.append(end)
        else:
            transitions[-1] = end

        display_methods = {'sec': 1.0, 'min': 60.0}
        for display_method in display_methods:
            logger.log.info("%s : final trans %s (%s)" %
                            (recording, [t/display_methods[display_method] for t in transitions], display_method))

        # create the separate segment wav files
        logger.log.info('%s : starting to create segments' % recording)
        samples = {}
        sample_rate = None
        for channel_number in range(0, number_of_channels):
            input_file_path = os.path.join(folders.mono_wav_fp_folder(self._output_root, recording),
                                           "TASCAM_%s_%d_fp32.wav" % (recording, channel_number))
            sample_rate, samples[channel_number] = wavfile.read(input_file_path)

        # for each transition, create separate segment mono files and a mix file
        for transition_index in range(0, len(transitions)-1):

            start = int(transitions[transition_index] * sample_rate)  # first sample index for this segment
            end = int(transitions[transition_index + 1] * sample_rate)  # last sample index for this segment

            # for this segment, write out separate mono wav files for each channel
            for channel_number in range(0, number_of_channels):
                folder = folders.segments_mono_folder(self._output_root, recording, transition_index)
                os.makedirs(folder, exist_ok=True)
                out_wav = os.path.join(folder, "TASCAM_%s_%d_%d_fp32.wav" % (recording, channel_number, transition_index))
                wavfile.write(out_wav, sample_rate, samples[channel_number][start:end])

            # create one mix wav file for this segment

            mix_levels = [[1.0, 0.0], [0.0, 1.0], [0.5, 0.5], [0.5, 0.5]]  # todo: make this a config option
            pad = -20.0  # pad down so when we sum we don't end up with clipping todo: make this a config option?

            for channel_number in range(0, number_of_channels):
                max_db = max(meters[channel_number]['rms_db'])
                linear_pad = wav_util.db_to_linear(pad - max_db)
                logger.log.info('channel %d : max_db %f : linear_pad %f' % (channel_number, max_db, linear_pad))
                for lr in range(0, 2):
                    mix_levels[channel_number][lr] *= linear_pad
            logger.log.info('mix_levels : %s' % str(mix_levels))

            # todo: adjust the mix levels based on each channel's meter's max rms value over the window
            # todo: also make sure we don't clip, so we may have to do the mix twice and do a final level adjustment

            # will be transposed when we write out the wav file, but it's faster to do the calculations this way
            mix = np.zeros((2, end - start))
            for channel_number in range(0, number_of_channels):
                mix[0] += samples[channel_number][start:end] * mix_levels[channel_number][0]  # left
                mix[1] += samples[channel_number][start:end] * mix_levels[channel_number][1]  # right

            logger.log.info('recording %s : segment %d : max left : %f' % (recording, transition_index, max(abs(mix[0]))))
            logger.log.info('recording %s : segment %d : max right : %f' % (recording, transition_index, max(abs(mix[1]))))

            out_mix_wav_folder = folders.segments_mix_wav_folder(self._output_root)
            os.makedirs(out_mix_wav_folder, exist_ok=True)
            out_mix_wav_path = os.path.join(out_mix_wav_folder, "TASCAM_%s_%d_fp32.wav" % (recording, transition_index))

            wavfile.write(out_mix_wav_path, sample_rate, np.transpose(mix).astype(dtype=wav_util.WAV_FP_DTYPE))



