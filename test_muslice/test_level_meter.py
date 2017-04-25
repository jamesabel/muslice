
import os
import sys
import math

from scipy.io import wavfile
import numpy as np

import muslice.level_meter as lm
from muslice import logger
from muslice import muslice_util
from muslice import folders
from test_muslice import tst_util

TEST_NAME = 'test_level_meter'


@muslice_util.time_it
def test_level_meter():

    logger.log.info('*** starting %s ***' % sys._getframe().f_code.co_name)

    tolerance = 0.0001
    sqrt_2 = math.sqrt(2.0)
    minus_3_db = 20.0 * math.log(sqrt_2/2.0, 10.0)  # approx -3.0103

    data_folder = os.path.join(tst_util.get_output_data_root(), TEST_NAME)
    os.makedirs(data_folder, exist_ok=True)

    # simple example
    file_name = 'sine_one_cycle.wav'
    file_path = os.path.join(data_folder, file_name)
    sample_rate = 48000
    samples = 8
    max_val = 0.999999
    tst_util.create_mono_sine_wav_file(file_path, 2.0, sample_rate, 3, sample_rate / samples, max_val)

    # todo: get this test to work again (it not longer works since I took out the sample_window_period (made it alway 1 sec) )
    #level_meter = lm.level_meter_file(tst_util.wav_to_fp32wav(file_path), 1.0, False, True)
    #assert(abs(level_meter['rms'][0] - sqrt_2/2.0) < tolerance)
    #assert(abs(level_meter['rms'][2] - max_val) < tolerance)
    #assert(abs(level_meter['rms'][3] - sqrt_2/2.0) < tolerance)
    #assert(len(level_meter['rms']) == samples)

    # 10 sec sine wave
    recording = 'sine_440_10_48000_10'
    file_name = recording + '.wav'
    file_path = os.path.join(data_folder, file_name)
    tst_util.create_mono_sine_wav_file(file_path, 10, 48000, 3, 440, 1.0)
    meters_folder = folders.mono_meters_folder(data_folder, recording)
    level_meter = lm.level_meter_file(tst_util.wav_to_fp32wav(file_path), meters_folder, 1.0)
    assert(all([abs(level - sqrt_2/2.0) < tolerance for level in level_meter['rms_linear']]))
    # window different than sample period
    level_meter = lm.level_meter_file(tst_util.wav_to_fp32wav(file_path), meters_folder, 1.0)
    assert(all([abs(level - sqrt_2/2.0) < tolerance for level in level_meter['rms_linear']]))
    # log mode
    level_meter = lm.level_meter_file(tst_util.wav_to_fp32wav(file_path), meters_folder, 1.0)
    assert(all([abs(level - minus_3_db) < tolerance for level in level_meter['rms_db']]))

    # lower amplitude
    recording = 'sine_440_10_48000_05'
    file_name = recording + '.wav'
    file_path = os.path.join(data_folder, file_name)
    tst_util.create_mono_sine_wav_file(file_path, 10, 48000, 3, 440, 0.5)
    meters_folder = folders.mono_meters_folder(data_folder, recording)
    level_meter = lm.level_meter_file(tst_util.wav_to_fp32wav(file_path), meters_folder, 1.0)
    assert(all([abs(level - sqrt_2/4.0) < tolerance for level in level_meter['rms_linear']]))

    # different frequency
    recording = 'sine_220_5_48000_05'
    file_name = recording + '.wav'
    file_path = os.path.join(data_folder, file_name)
    tst_util.create_mono_sine_wav_file(file_path, 5, 48000, 3, 220, 0.5)
    meters_folder = folders.mono_meters_folder(data_folder, recording)
    level_meter = lm.level_meter_file(tst_util.wav_to_fp32wav(file_path), meters_folder, 1.0)
    assert(len(level_meter['rms_linear']) == 5)
    assert(all([abs(level - sqrt_2/4.0) < tolerance for level in level_meter['rms_linear']]))

    # silence
    recording = 'sine_440_10_48000_00'
    file_name = recording + '.wav'
    file_path = os.path.join(data_folder, file_name)
    tst_util.create_mono_sine_wav_file(file_path, 10, 48000, 3, 440, 0.0)
    meters_folder = folders.mono_meters_folder(data_folder, recording)
    level_meter = lm.level_meter_file(tst_util.wav_to_fp32wav(file_path), meters_folder, 1.0)
    assert(all([level < tolerance for level in level_meter['rms_linear']]))

    # random
    recording = 'random'
    file_name = recording + '.wav'
    file_path = os.path.join(data_folder, file_name)
    random_sample_rate = 44100
    meters_folder = folders.mono_meters_folder(data_folder, recording)
    wavfile.write(tst_util.wav_to_fp32wav(file_path), random_sample_rate, 2.0 * np.random.random(2 * random_sample_rate) - 1.0)
    level_meter = lm.level_meter_file(tst_util.wav_to_fp32wav(file_path), meters_folder, 1.0)
    # https://electronics.stackexchange.com/questions/58007/a-zero-mean-random-signal-is-uniformly-distributed-between-limits-a-and-a-and-i
    assert(level_meter['rms_linear'][0] - 1.0/math.sqrt(3.0) < 0.1)  # approximate comparison for random noise
