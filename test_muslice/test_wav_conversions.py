
import sys
import binascii

from muslice import wav_util
from muslice import muslice_util
from muslice import logger

TEST_NAME = 'test_wav_conversions'


@muslice_util.time_it
def test_wav_bytes_to_float():

    logger.log.info('*** starting %s ***' % sys._getframe().f_code.co_name)

    lsb_24_bit = 1.0/(32768.0*256.0)
    expected_values = {b'\x00': 0.0,
                       b'\x01': 1.0/128.0,
                       b'\x40': 0.5,
                       b'\x80': -1.0,
                       b'\xc0': -0.5,
                       b'\xff': -1.0/128.0,
                       b'\x7f': 127.0/128.0,

                       b'\x00\x00': 0.0,
                       b'\x00\x40': 0.5,
                       b'\x00\xc0': -0.5,
                       b'\xff\x7f': 32767.0/32768.0,
                       b'\x01\x80': -32767.0/32768.0,
                       b'\x00\x80': -1.0,

                       b'\x00\x00\x00': 0.0,
                       b'\x01\x00\x00': lsb_24_bit,
                       b'\x00\x00\x20': 0.25,
                       b'\x00\x00\x40': 0.5,
                       b'\x00\x00\xc0': -0.5,
                       b'\xff\xff\x7f': 1-lsb_24_bit,
                       }

    for value_as_byte_string in sorted(expected_values):
        expected_float_value = expected_values[value_as_byte_string]
        logger.log.info('testing %33.30f (%s)' % (expected_float_value, binascii.b2a_hex(value_as_byte_string)))
        assert(wav_util.wav_bytes_to_float(value_as_byte_string) == expected_float_value)


def _tst_conversion(value):
    #print()
    wav_bytes = wav_util.float_to_wav_bytes(value, 3)
    #print(binascii.hexlify(wav_bytes))
    check_value = wav_util.wav_bytes_to_float(wav_bytes)
    #print(check_value)
    assert(abs(value - check_value) < 0.00001)


@muslice_util.time_it
def test_conversions():

    logger.log.info('*** starting %s ***' % sys._getframe().f_code.co_name)

    _tst_conversion(0.9999999)  # 1.0 is out of range
    _tst_conversion(0.5)
    _tst_conversion(0.0)
    _tst_conversion(-0.5)
    _tst_conversion(-1.0)


def main():
    test_wav_bytes_to_float()
    test_conversions()

if __name__ == '__main__':
    main()
