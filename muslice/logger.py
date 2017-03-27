
import logging

import muslice

log = None
_ch = None


def init():
    global log, _ch

    log = logging.getLogger(muslice.__application_name__)
    log.setLevel(logging.DEBUG)

    _ch = logging.StreamHandler()
    log.addHandler(_ch)


def set_console_handler_level(new_level):
    global _ch
    _ch.setLevel(new_level)
