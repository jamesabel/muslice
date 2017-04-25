
import os
import sys
import multiprocessing

import muslice.config as config
from test_muslice import tst_util
from muslice import MuSlice
from muslice import muslice_util
from muslice import logger

TEST_NAME = 'test_slicing'


def get_input_folder():
    return os.path.join(tst_util.get_input_data_root(), TEST_NAME)


def get_output_folder():
    return os.path.join(tst_util.get_output_data_root(), TEST_NAME)


@muslice_util.time_it
def test_slicing():

    logger.log.info('*** starting %s ***' % sys._getframe().f_code.co_name)

    wav_files_folder = os.path.join(get_input_folder(), 'recordings')
    os.makedirs(wav_files_folder, exist_ok=True)
    os.makedirs(get_output_folder(), exist_ok=True)

    tst_config = config.Config(os.path.join(get_output_folder(), TEST_NAME + '.json'))
    tst_config.set('source_folder', wav_files_folder)
    tst_config.set('output_folder', get_output_folder())

    variance = -10.0

    # order:
    # recording name, duration (song length in sec), segements (number of songs)
    test_configs = [('0001', 2.5 * 60.0, 3),
                    ('0002', 3.0 * 60.0, 5),
                    ('0003', 3.5 * 60.0, 10)
                    ]
    seconds_per_pause = 20.0

    # if number of tests not given, run them all
    n_tests = tst_util.get_n_tests()
    if n_tests is None:
        n_tests = len(test_configs)

    for test in range(0, n_tests):
        logger.log.info('doing test %d : %s' % (test, test_configs[test]))
        recording, duration, segments = test_configs[test]

        wav_infos = [{'name': 'TASCAM_%sS12.wav' % recording, 'segment_level': -10.0, 'pause_level': -40.0},
                     {'name': 'TASCAM_%sS34.wav' % recording, 'segment_level': -25.0, 'pause_level': -55.0}]

        processes = []
        for wav_info in wav_infos:
            args = (
                wav_files_folder,
                48000,  # sample_rate in Hz
                2,  # number_of_channels - stereo
                segments,  # number_of_segments - i.e. songs
                duration,  # seconds_per_segment - song duration
                wav_info['segment_level'],  # segment_level - typical program material level, in dB
                seconds_per_pause,  # seconds_per_pause - breaks between songs
                wav_info['pause_level'],  # pause_level - break between song level, in dB
                0.15,  # seconds_per_note
                'test',  # file_prefix
                variance,  # dB variance for program material
                wav_info['name'],  # file_name
                False,  # don't make the FP version
                4000.0  # base freq
            )
            p = multiprocessing.Process(target=tst_util.create_test_wav_files, args=args)
            p.start()

            # todo: this is here temporarily to limit to 1 active thread since we were running out of memory for the big files
            #       so, eventually we need to not have this join() once I figure out how to reduce the memory footprint of create_test_wav_files()
            p.join()

            processes.append(p)
        for p in processes:
            p.join()

    tst_muslice = MuSlice(tst_config.config_file_path, False)
    tst_muslice.run()

    # todo: check the output (perhaps have MuSlice write transition points to a .json file?)