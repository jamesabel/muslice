
import os
import glob
import time
from multiprocessing import Process

import muslice.logger as logger
import muslice.level_meter as level_meter

if False:
    # todo: make this return a dict of meters and replace level_meter_folder()
    def mt_level_meter(root_folder, recordings, config):

        # todo: make a 'top level' check if all files already exist so this returns quickly (we don't have to wait
        # for processes to be created and exit)

        # make individual level meter files from the mono wav files
        args_list = []
        for recording in recordings:
            for file_path in glob.glob(os.path.join(root_folder, recording) + os.sep + '*_fp32.wav'):
                args_list.append((file_path, config.get('meter_window'), config.get('meter_sample_period'), True))

        # todo: ST version
        processes = []
        while len(args_list) > 0:
            if sum([p.is_alive() for p in processes]) < config.get('max_threads'):
                args = args_list.pop(0)
                p = Process(target=level_meter.level_meter_file, args=args)
                processes.append(p)
                p.start()
                logger.log.debug('started level_meter process : %s : %s' % (str(p), args))
            else:
                time.sleep(0.1)

        # ensure all processes are complete before we return
        for p in processes:
            p.join()
