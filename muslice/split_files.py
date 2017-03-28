
import os
import wave
import time
import pprint
from multiprocessing import Process

import muslice.logger as logger


def make_n_aural_files(groups, out_root, max_threads):
    if max_threads > 1:
        group_args = [(group, groups[group], out_root) for group in groups]
        group_args.reverse()
        processes = {}
        while len(group_args) > 0:
            n_running = sum([processes[p] is not None for p in processes])
            if n_running < max_threads:
                new_process_args = group_args.pop()
                new_process_id = new_process_args[0]
                print(new_process_args)
                processes[new_process_id] = Process(target=_make_one_group, args=new_process_args)
                processes[new_process_id].start()
                pprint.pprint(processes)
            else:
                time.sleep(1)
            for p in processes:
                if processes[p] and not processes[p].is_alive():
                    processes[p].join()
                    processes[p] = None
                    pprint.pprint(processes)
    else:
        # single threaded - mainly for code coverage and profiling
        logger.log.warn('*** SINGLE THREADED ***')
        for group in groups:
            _make_one_group(group, groups[group], out_root)


def _make_one_group(group, file_paths, out_root):
    """
    Given a dict of recordings and associated multiple, multi-channel files, create a folder per recording
    with individual (mono) files per channel.
    :param groups: dict where the recording names are the key and the files associated with that recording are in a
    list as the values
    :param out_root: root folder for the output
    """
    start = time.time()
    seconds = None

    number_of_input_channels = 2  # stereo input

    logger.log.info('converting recording : "%s"' % group)
    out_folder = os.path.join(out_root, group)
    os.makedirs(out_folder, exist_ok=True)

    # each group potentially has multiple files, each which may have multiple channels
    # typical input file scenario for a group called '0030':
    # TASCAM_0030S12.wav   - stereo channels 1 and 2
    # TASCAM_0030S34.wav   - stereo channels 3 and 4
    for file_path in file_paths:
        with wave.open(file_path) as input_wave_file:

            # one input file will be written back out as (usually) multiple output files
            # for example, one stereo input file will be written as as 2 mono output files

            # get the input file information
            frames = input_wave_file.getnframes()
            sample_width = input_wave_file.getsampwidth()
            sample_rate = input_wave_file.getframerate()
            seconds = float(frames)/float(sample_rate)

            input_samples = input_wave_file.readframes(frames)

            logger.log.info('%d frames, %d bits, %d samples/sec, %d input bytes, %f sec, %s' %
                            (frames, sample_width * 8, sample_rate, len(input_samples), seconds, file_path))

            out_files = []
            out_samples = {}
            for channel in range(0, number_of_input_channels):

                # Determine the output path.
                # Example: input file name of TASCAM_0030S12.wav (take 0030, S12 = stereo channels 1 and 2)
                # will create output file names of TASCAM_0030_0.wav and TASCAM_0030_1.wav.
                basename = os.path.basename(file_path)
                split = basename.split('S')
                prefix = basename.split('_')[0]
                base_number = int(split[2][0]) - 1
                out_file_name = '%s_%s_%d.wav' % (prefix, group, channel + base_number)
                output_path = os.path.join(out_folder, out_file_name)
                logger.log.info('writing : %s' % output_path)

                # set up the output file
                output_wave_file = wave.open(output_path, 'wb')
                output_wave_file.setnchannels(1)  # mono output
                output_wave_file.setsampwidth(sample_width)
                output_wave_file.setframerate(sample_rate)
                out_files.append(output_wave_file)
                out_samples[channel] = []

            # convert interleaved multi-channel to N mono channels
            input_byte_count = 0
            while input_byte_count < len(input_samples):
                for channel in range(0, number_of_input_channels):
                    for b in range(0, sample_width):
                        out_samples[channel].append(input_samples[input_byte_count])
                        input_byte_count += 1

            # write out the output files
            for channel in range(0, number_of_input_channels):
                out_files[channel].writeframes(bytearray(out_samples[channel]))

    execution_duration = float(time.time() - start)
    logger.log.info('completed : "%s" (%f seconds, %fx realtime)' %
                    (group, execution_duration, execution_duration/float(seconds)))