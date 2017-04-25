
import math
import os
import wave
import random

import pytest
import numpy as np
from scipy.io import wavfile

from muslice import wav_util
from muslice import muslice_util
from muslice import logger

ROOT = os.path.join('test_muslice', 'data')


def get_input_data_root():
    return os.path.join(ROOT, 'in')


def get_output_data_root():
    return os.path.join(ROOT, 'out')


def get_log_folder():
    return os.path.join(ROOT, 'log')


def wav_to_fp32wav(file_path):
    return file_path.replace('.wav', '_fp32.wav')


def _get_config_int(option_string):
    # see conftest.py to set up these options
    n = pytest.config.getoption(option_string)
    if n:
        n = int(n)
    if logger.log:
        logger.log.info('%s : %s' % (option_string, str(n)))
    return n


def get_n_tests():
    return _get_config_int("--n_tests")


def get_delete_starting():
    return _get_config_int("--delete_starting")


@muslice_util.time_it
def create_mono_sine_wav_file(file_path, duration, sample_rate, bytes_per_sample, frequency, amplitude):

    float_to_int_scale = pow(2.0, bytes_per_sample * 8 - 1)  # fp to integer at this bit width
    mask = int(pow(2.0, bytes_per_sample * 8)) - 1  # all 1s for this bit width
    pi = 4.0 * math.atan(1.0)
    number_of_samples = int(sample_rate * duration + 0.5)

    # calculate the wave
    wav_data = []
    wav_data_fp32 = []
    for sample in range(0, number_of_samples):
        fp_value = amplitude * math.sin(2.0 * pi * frequency * float(sample)/float(sample_rate))
        wav_data_fp32.append(fp_value)
        value = int(fp_value * float_to_int_scale + 0.5) & mask
        wav_data.append(value.to_bytes(bytes_per_sample, 'little'))

    # write integer version to the wav file
    with wave.open(file_path, 'wb') as f:
        f.setnframes(number_of_samples)
        f.setnchannels(1)
        f.setframerate(sample_rate)
        f.setsampwidth(bytes_per_sample)
        f.writeframes(b''.join(wav_data))

    # write the floating point version
    wavfile.write(file_path.replace('.wav', '_fp32.wav'), sample_rate, np.array(wav_data_fp32, dtype=wav_util.WAV_FP_DTYPE))


@muslice_util.time_it
def create_test_wav_files(file_folder,
                          sample_rate,
                          number_of_channels,
                          number_of_segments,
                          seconds_per_segment,
                          segment_level,
                          seconds_per_pause,
                          pause_level,
                          seconds_per_note,
                          file_prefix,
                          variance,
                          file_name,
                          write_fp_file,
                          base_freq
                          ):
    """
    Create a synthetic wav file that emulates program material.

    :param file_folder: path to output folder
    :param sample_rate: sample rate in Hz
    :param number_of_channels: number of channels (1=mono, 2=stereo)
    :param number_of_segments: number of segments (a segment 'emulates' a song)
    :param seconds_per_segment: seconds per segment
    :param segment_level: level in dB of the segment (must be 0 or below)
    :param seconds_per_pause: seconds per pause
    :param pause_level: level in dB of the pause (break between segments)
    :param seconds_per_note: seconds per note
    :param file_prefix: file name prefix
    :param variance: variance in dB between notes (must be 0 or below)
    :param file_name: file name for the file - if not given, a default format will be used
    :param write_fp_file: True to write the FP wav file.  If false, only write the integer wav file.
    :param base_freq: base (highest) frequency to use
    :return: file name created for the file
    """

    # todo: can I avoid the reshape by building the samples properly to begin with?

    if variance > 0.0:
        raise ValueError

    os.makedirs(file_folder, exist_ok=True)

    if file_name is None:
        # create a unique file name based on paramters (of course, the user can rename it later)
        # avoid special chars like '.' and '-' by using abs and scaling up small values
        file_name = '%s_%d_%d_%d_%d_%d_%d_%d_%d_%d.wav' % (file_prefix, sample_rate, number_of_channels,
                                                           number_of_segments, seconds_per_segment, abs(segment_level),
                                                           seconds_per_pause, abs(pause_level), 1000 * seconds_per_note,
                                                           abs(variance))

    file_path = os.path.join(file_folder, file_name)

    if os.path.exists(file_path):
        logger.log.info('%s already exists' % file_path)
        return

    logger.log.info('making %s' % file_path)

    samples = []

    def _make_notes(amplitude_db, duration, note_base_freq):
        # make a series of notes for time duration
        for _ in range(0, int(duration/seconds_per_note + 0.5)):

            # make notes (in an array of samples), one per channel
            channels = []
            amplitude = wav_util.db_to_linear(amplitude_db + (random.random() * variance))
            for channel in range(0, number_of_channels):
                # one note
                freq = random.random() * note_base_freq
                channels.append(amplitude * np.sin(2 * np.pi * np.arange(sample_rate * seconds_per_note) * freq / sample_rate))

            # insert the samples into the sample array interleaved, so it can be used to write out the wav file
            for sample_index in range(0, len(channels[0])):
                for channel in range(0, number_of_channels):
                    samples.append(channels[channel][sample_index])

    # make an n-channel wave file that has segments with random tones and silence in between the segments
    _make_notes(pause_level, seconds_per_pause, base_freq)  # start with something close to silence
    for _ in range(0, number_of_segments):
        base_freq *= 0.5 #  lower freq as we go
        _make_notes(segment_level, seconds_per_segment, base_freq)
        _make_notes(pause_level, seconds_per_pause, base_freq)  # silence between songs

    # make the floating point wav file version
    # http://stackoverflow.com/questions/12575421/convert-a-1d-array-to-a-2d-array-in-numpy
    if write_fp_file:
        wavfile.write(wav_to_fp32wav(file_path), sample_rate,
                      np.reshape(samples, (-1, 2)).astype(dtype=wav_util.WAV_FP_DTYPE))

    # make the integer wav file version
    with wave.open(file_path, 'wb') as wav_file:
        width = 3  # bytes
        wav_file.setnframes(int(len(samples)/2))
        wav_file.setnchannels(2)
        wav_file.setframerate(int(sample_rate))
        wav_file.setsampwidth(width)
        samples_integer = []
        for sample in samples:
            samples_integer.append(wav_util.float_to_wav_bytes(sample, width))
        wav_file.writeframes(b''.join(samples_integer))

    return file_name

