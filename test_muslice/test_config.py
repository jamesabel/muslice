
import os
import sys
import json

from muslice import logger
from muslice import config
from muslice import muslice_util
import test_muslice.tst_util as tst_util

TEST_NAME = 'test_config'


def get_test_config_folder():
    return os.path.join(tst_util.get_output_data_root(), TEST_NAME)


@muslice_util.time_it
def test_config():

    logger.log.info('*** starting %s ***' % sys._getframe().f_code.co_name)

    os.makedirs(get_test_config_folder(), exist_ok=True)
    config_file_path = os.path.join(get_test_config_folder(), 'tst_muslice_config.json')
    try:
        os.remove(config_file_path)
    except FileNotFoundError:
        pass

    # create the config file
    new_config = config.Config(config_file_path)
    assert(new_config.get('meter_window') == 3.0)  # get one of the defaults

    new_value = 2.0
    # modify json file
    with open(config_file_path) as fr:
        c = json.load(fr)
        c['meter_sample_period'] = new_value
        with open(config_file_path, 'w') as fw:
            json.dump(c, fw, indent=2)

    # read in modified config
    existing = config.Config(config_file_path)
    assert(existing.get('meter_sample_period') == new_value)
