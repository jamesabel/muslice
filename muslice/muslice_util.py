
import re
import time

from muslice import logger


def file_name_to_info(file_name):
    """
    returns the recording info from a file name
    :param file_name: file name
    :return: (recording, channel) or None if the file name does not match the file name format
    """
    recording = None
    channel = None

    # original (stereo) format:
    # TASCAM_xxxxSyy.wav where xxxx is the recording number and yy is the channel pair (e.g. 12, 34)
    orig_fields = re.search(r'(TASCAM_)([\d]*)(S)([\d]*)(.wav)', file_name)
    if orig_fields:
        recording = orig_fields.group(2)
        channel = int(orig_fields.group(4))

    # our mono format:
    # TASCAM_0044_0.wav or TASCAM_0044_0_fp32.wav
    mono_fields = re.search(r'(TASCAM_)([\d]*)(_)([\d]*)(.wav|_fp32.wav)', file_name)
    if mono_fields:
        recording = mono_fields.group(2)
        channel = int(mono_fields.group(4))

    return recording, channel


def time_it(method):
    def timed(*args, **kw):
        _time_it_start = time.time()
        _time_it_result = method(*args, **kw)
        _time_it_elapsed = time.time() - _time_it_start
        if _time_it_elapsed > 1.0:
            # don't worry about really short times
            logger.log.info('%r : %2.2f sec' % (method.__name__, _time_it_elapsed))
        return _time_it_result
    return timed
