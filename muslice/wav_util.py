
import functools
import math

import numpy as np
import scipy as sp

WAV_FP_DTYPE = np.float32  # all floating point wav files use this type


def wav_bytes_to_float(in_bytes):
    """
    converts a byte string read in from a .wav file to a floating point value between -1.0 and almost 1.0
    :param in_bytes: string of bytes, typically between 1 and 3 bytes but there is no actual restriction
    :return: value between -1.0 and 1.0 minus one least significant bit
    """
    bits = len(in_bytes)*8
    int_val = 0
    shift = 0
    for b in in_bytes:
        int_val |= b << shift
        shift += 8
    if in_bytes[-1] >= 0x80:
        # negative
        int_val = -((0x1 << bits) - int_val)
    return float(int_val)/pow(2.0, bits-1)


def float_to_wav_bytes(in_float, n_bytes):
    """
    convert a floating point value between -1.0 and almost 1.0 to a byte string
    :param in_float: input floating point value
    :param n_bytes: number of bytes in output byte string
    :return: a byte string that represents an integer converted from the input floating point value
    """

    # make these for speed since we use the same byte size over and over

    @functools.lru_cache()
    def _scale(n):
        return pow(2.0, n * 8 - 1)

    @functools.lru_cache()
    def _mask(n):
        return (1 << n * 8) - 1

    in_integer = int(in_float * _scale(n_bytes)) & _mask(n_bytes)
    return in_integer.to_bytes(n_bytes, byteorder='little')


def db_to_linear(db_value):
    return math.pow(10.0, db_value / 20.0)


def rms(arr):
    return sp.sqrt(np.sum(np.square(arr)) / float(len(arr)))
