
import os
import logging

import muslice

log = None
_ch = None
_fh = None


def init(log_folder):
    global log, _ch, _fh, _formatter

    if log is None:
        _formatter = logging.Formatter('%(asctime)s - %(name)s - %(filename)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s')

        log = logging.getLogger(muslice.__application_name__)
        log.setLevel(logging.DEBUG)

        _ch = logging.StreamHandler()
        _ch.setLevel(logging.INFO)
        _ch.setFormatter(_formatter)
        log.addHandler(_ch)

        os.makedirs(log_folder, exist_ok=True)
        log_file_path = os.path.join(log_folder, muslice.__application_name__ + '.log')
        _fh = logging.FileHandler(log_file_path)
        _fh.setLevel(logging.DEBUG)
        _fh.setFormatter(_formatter)
        log.addHandler(_fh)

        log.info('log file path : %s (%s)' % (log_file_path, os.path.abspath(log_file_path)))
    else:
        log.info('log already set up (%s)' % log_folder)


def set_console_handler_level(new_level):
    global _ch
    _ch.setLevel(new_level)


def set_file_handler_level(new_level):
    global _fh
    _fh.setLevel(new_level)
