
import os
import logging

import muslice

log = None
_ch = None
_fh = None


def init():
    global log, _ch, _fh

    log = logging.getLogger(muslice.__application_name__)
    log.setLevel(logging.INFO)

    _ch = logging.StreamHandler()
    log.addHandler(_ch)

    log_folder = 'log'
    os.makedirs(log_folder, exist_ok=True)
    _fh = logging.FileHandler(os.path.join(log_folder, muslice.__application_name__ + '.log'))
    log.addHandler(_fh)


def set_console_handler_level(new_level):
    global _ch
    _ch.setLevel(new_level)


def set_file_handler_level(new_level):
    global _fh
    _fh.setLevel(new_level)
