
import os
import wave
import time
from multiprocessing import Process

import numpy as np
from scipy.io import wavfile

from muslice import logger
from muslice import muslice_util
from muslice import wav_util
from muslice import folders

"""

Split multiple N-channel (usually 2 channel stereo) wav files into multiple mono wav files.  The output files 
are both in the original bit representation (e.g. 16 bit integer, 24 bit integer, etc.) and 32-bit floating 
point (AKA FP32).

To speed processing, it can be run multi-threaded.

e.g.:

    input of:

    MUSIC/DR40_0000/DR40_0000/TASCAM_0030S12.wav  # stereo channels 1 and 2
    MUSIC/DR40_0000/DR40_0000/TASCAM_0030S34.wav  # stereo channels 3 and 4

    is converted to:
    output/0030/TASCAM_0030_0.wav       # channel 1 from above
    output/0030/TASCAM_0030_0_fp32.wav  # channel 1 from above in FP32 format
    output/0030/TASCAM_0030_1.wav       # channel 2 from above
    output/0030/TASCAM_0030_1_fp32.wav  # channel 2 from above in FP32 format
    output/0030/TASCAM_0030_2.wav       # channel 3 from above
    output/0030/TASCAM_0030_2_fp32.wav  # channel 3 from above in FP32 format
    output/0030/TASCAM_0030_3.wav       # channel 4 from above
    output/0030/TASCAM_0030_3_fp32.wav  # channel 4 from above in FP32 format

"""


@muslice_util.time_it
def make_mono_files(recordings, out_root, max_threads):

    # todo: make a 'top level' check if all files already exist so this returns quickly (we don't have to wait
    # for processes to be created and exit)

    if max_threads > 1:
        recording_args = [(recording, recordings[recording], out_root) for recording in recordings]
        print(recording_args)
        processes = []
        while len(recording_args) > 0:
            if sum([p.is_alive() for p in processes]) < max_threads:
                p = Process(target=_make_mono_files_one_recording, args=recording_args.pop(0))
                processes.append(p)
                p.start()
            else:
                time.sleep(0.1)
        # ensure all processes are complete before we return
        for p in processes:
            p.join()
    else:
        # single threaded - mainly for code coverage and profiling
        logger.log.warn('*** SINGLE THREADED ***')
        for recording in recordings:
            _make_mono_files_one_recording(recording, recordings[recording], out_root)


@muslice_util.time_it
def _make_mono_files_one_recording(recording, file_paths, out_root):
    """
    Given a dict of recordings and associated multiple, multi-channel files, create a folder per recording
    with individual (mono) files per channel.
    :param groups: dict where the recording names are the key and the files associated with that recording are in a
    list as the values
    :param out_root: root folder for the output
    """
    start = time.time()

    logger.log.debug('converting recording : "%s"' % recording)

    # each recording potentially has multiple files, each which may have multiple channels
    # typical input file scenario for a recording called '0030':
    # TASCAM_0030S12.wav   - stereo channels 1 and 2
    # TASCAM_0030S34.wav   - stereo channels 3 and 4
    for file_path in file_paths:
        with wave.open(file_path) as input_wave_file:

            # one multi-channel input file will be written back out as multiple output files
            # for example, one stereo input file will be written as as 2 mono output files

            # get the input file information
            frames = input_wave_file.getnframes()
            sample_width = int(input_wave_file.getsampwidth())
            sample_rate = input_wave_file.getframerate()
            seconds = float(frames)/float(sample_rate)
            number_of_input_channels = int(input_wave_file.getnchannels())

            # determine the output file paths
            out_file_paths = {}
            out_file_paths_fp32 = {}
            for channel in range(0, number_of_input_channels):
                # Example: input file name of TASCAM_0030S12.wav (take 0030, S12 = stereo channels 1 and 2)
                # will create output file names of TASCAM_0030_0.wav and TASCAM_0030_1.wav.
                file_name = os.path.basename(file_path)
                split = file_name.split('S')  # assumes Snm format in file
                prefix = file_name.split('_')[0]
                base_number = int(split[2][0]) - 1  # zero based numbering

                wav_folder_path = folders.mono_wav_folder(out_root, recording)
                os.makedirs(wav_folder_path, exist_ok=True)
                out_file_name = '%s_%s_%d.wav' % (prefix, recording, channel + base_number)  # same format as original
                out_file_paths[channel] = os.path.join(wav_folder_path, out_file_name)

                wav_fp_folder_path = folders.mono_wav_fp_folder(out_root, recording)
                os.makedirs(wav_fp_folder_path, exist_ok=True)
                out_file_name_fp32 = '%s_%s_%d_fp32.wav' % (prefix, recording, channel + base_number)  # FP format
                out_file_paths_fp32[channel] = os.path.join(wav_fp_folder_path, out_file_name_fp32)

            if all([os.path.exists(out_file_paths[p]) for p in out_file_paths]) and all([os.path.exists(out_file_paths_fp32[p]) for p in out_file_paths_fp32]):
                logger.log.debug('all mono wav files for %s already exist' % file_path)
            else:
                [logger.log.info('making %s' % out_file_paths[p]) for p in out_file_paths]
                [logger.log.info('making %s' % out_file_paths_fp32[p]) for p in out_file_paths_fp32]

                input_samples = input_wave_file.readframes(frames)

                logger.log.info('%d frames, %d bits, %d channels, %d samples/sec, %d input bytes, %f sec, %s' %
                                (frames, sample_width * 8, number_of_input_channels, sample_rate, len(input_samples),
                                 seconds, file_path))

                out_samples = {}
                out_samples_fp32 = {}
                for channel in range(0, number_of_input_channels):
                    out_samples[channel] = []
                    out_samples_fp32[channel] = []

                # convert interleaved multi-channel to N mono channels
                input_byte_count = 0
                while input_byte_count < len(input_samples):
                    for channel in range(0, number_of_input_channels):
                        sample = input_samples[input_byte_count:input_byte_count+sample_width]

                        # original format
                        out_samples[channel].extend(list(sample))
                        input_byte_count += sample_width

                        # fp32
                        out_samples_fp32[channel].append(wav_util.wav_bytes_to_float(sample))

                # write out the output files
                for channel in range(0, number_of_input_channels):

                    output_wave_file = wave.open(out_file_paths[channel], 'wb')
                    output_wave_file.setnchannels(1)  # mono output
                    output_wave_file.setsampwidth(sample_width)
                    output_wave_file.setframerate(sample_rate)
                    output_wave_file.writeframes(bytearray(out_samples[channel]))

                    wavfile.write(out_file_paths_fp32[channel], sample_rate, np.array(out_samples_fp32[channel],
                                                                                      dtype=wav_util.WAV_FP_DTYPE))

                execution_duration = float(time.time() - start)
                logger.log.info('completed : "%s" (%f seconds, %fx realtime)' %
                                (file_path, execution_duration, execution_duration/float(seconds)))
