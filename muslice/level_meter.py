
import os
import math
import json
import time

import numpy as np
from scipy.io import wavfile

from muslice import plotting
from muslice import logger
from muslice import wav_util
from muslice import muslice_util


def level_meter_folder(in_wav_fp_folder, meter_folder, window):
    meters = {}
    for wav_file in os.scandir(in_wav_fp_folder):
        if os.path.isfile(wav_file.path):
            recording, channel = muslice_util.file_name_to_info(wav_file.name)
            if recording:
                meters[channel] = level_meter_file(wav_file.path, meter_folder, window)
    return meters


def level_meter_file(wav_file_path, meter_folder, window):
    """
    Return the levels in a wav file.
    :param wav_file_path: input wav file
    :param meter_folder: meter_folder
    :param window: window of time to use to calculate a meter value (seconds)
    :return: a dict that holds the level meter samples
    """

    start = time.time()

    logger.log.info('entering level_meter_file for %s' % wav_file_path)

    os.makedirs(meter_folder, exist_ok=True)
    json_file_path = os.path.join(meter_folder, os.path.basename(wav_file_path).replace('_fp32.wav', '.json'))
    png_file_path = os.path.join(meter_folder, os.path.basename(wav_file_path).replace('_fp32.wav', '.png'))

    if os.path.exists(json_file_path) and os.path.exists(png_file_path):
        # everything already exists
        with open(json_file_path) as json_file:
            meter = json.load(json_file)
        # make sure this meter .json file is from the existing .wav file
        mtime_diff = abs(meter['mtime'] - os.path.getmtime(wav_file_path))
        if  mtime_diff < 10.0:
            logger.log.debug('all files already exist for : %s (mtime diff : %.2f)' % (wav_file_path, mtime_diff))
            return meter

    # todo: check that it's a mono wav file

    logger.log.debug('making level meter file for %s' % wav_file_path)

    sample_rate, samples = wavfile.read(wav_file_path)

    meter = level_meter(samples, sample_rate, window)

    meter['file_path'] = wav_file_path
    meter['mtime'] = os.path.getmtime(wav_file_path)
    meter['wave_sample_rate'] = sample_rate

    # write out the files
    with open(json_file_path, 'w') as json_file:
        json.dump(meter, json_file, indent=2)
    plotting.plot_rms_peak(meter['rms_db'], meter['peak_db'], png_file_path)

    logger.log.debug('completed level meter file for %s (%f seconds)' % (wav_file_path, time.time() - start))

    return meter


@muslice_util.time_it
def level_meter(samples, sample_rate, window):
    """
    create a level meter
    :param samples: a list of samples in FP format between -1.0 and almost 1.0
    :param sample_rate: audio input sample rate in Hz (e.g. 44100, 48000, etc.)
    :param window: meter window in seconds
    :return: 
    """
    rms_linear_values = []
    rms_db_values = []
    peak_linear_values = []
    peak_db_values = []

    if window < 1.0:
        print('error : window must be 1 sec or more (configuration has it as %f)' % window)

    # to avoid infinite -dB for silence, define a lower limit of silence and it's dB equivalent
    linear_silence = 1.0/pow(2.0, 20.0)
    db_silence = 20.0 * math.log(abs(linear_silence), 10.0)

    # do the RMS level meter calculations
    wav_samples_per_meter_window = int(sample_rate * window + 0.5)
    window_start = 0
    while window_start <= len(samples) - wav_samples_per_meter_window:

        window_data = samples[window_start:window_start+wav_samples_per_meter_window]
        rms_linear_value = wav_util.rms(window_data)
        peak_linear_value = np.max(np.abs(window_data))

        if rms_linear_value < linear_silence:
            rms_db_value = db_silence
        else:
            rms_db_value = 20.0 * math.log(abs(rms_linear_value), 10.0)
        if peak_linear_value < linear_silence:
            peak_db_value = db_silence
        else:
            peak_db_value = 20.0 * math.log(abs(peak_linear_value), 10.0)

        # have to convert to float so it's JSON serializable (it can come in as float32, which isn't JSON serializable)
        rms_linear_values.append(float(rms_linear_value))
        rms_db_values.append(float(rms_db_value))
        peak_linear_values.append(float(peak_linear_value))
        peak_db_values.append(float(peak_db_value))

        window_start += sample_rate
        if window_start > len(samples):
            print('warning : at sample %d went beyond the end of the number of samples of %d' %
                  (window_start, len(samples)))

    levels = {'rms_linear': rms_linear_values, 'rms_db': rms_db_values,
              'peak_linear': peak_linear_values, 'peak_db': peak_db_values,
              'meter_window': window,
              }

    return levels
