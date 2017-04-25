
import os
import random

from muslice import plotting
import test_muslice.tst_util as tst_util

TEST_NAME = 'test_plot'


def get_test_plot_folder():
    return os.path.join(tst_util.get_output_data_root(), TEST_NAME)


def test_rms_peak_plotting():

    os.makedirs(get_test_plot_folder(), exist_ok=True)

    rms_data = [random.random() for _ in range(0,1000)]
    peak_data = [random.random() for _ in range(0,1000)]
    file_path = os.path.join(get_test_plot_folder(), 'rms_peak.png')
    plotting.plot_rms_peak(rms_data, peak_data, file_path)


def test_plot_meters():

    os.makedirs(get_test_plot_folder(), exist_ok=True)

    db_range = -50.0
    meters = {}
    for channel in range(0, 4):
        meters[channel] = [db_range * random.random() for _ in range(0, 100)]
        plotting.plot_meters(meters, os.path.join(get_test_plot_folder(), 'meters.png'))
