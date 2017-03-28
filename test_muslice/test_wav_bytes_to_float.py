
import binascii

import muslice.util


def test_wav_bytes_to_float():
    lsb_24_bit = 1.0/(32768.0*256.0)
    expected_values = {b'\x00': 0.0,
                       b'\x01': 1.0/128.0,
                       b'\x40': 0.5,
                       b'\x80': -1.0,
                       b'\xc0': -0.5,
                       b'\xff': -1.0/128.0,
                       b'\x7f': 127.0/128.0,

                       b'\x00\x00': 0.0,
                       b'\x40\x00': 0.5,
                       b'\xc0\x00': -0.5,
                       b'\x7f\xff': 32767.0/32768.0,
                       b'\x80\x01': -32767.0/32768.0,
                       b'\x80\x00': -1.0,

                       b'\x00\x00\x00': 0.0,
                       b'\x00\x00\x01': lsb_24_bit,
                       b'\x20\x00\x00': 0.25,
                       b'\x40\x00\x00': 0.5,
                       b'\xc0\x00\x00': -0.5,
                       b'\x7f\xff\xff': 1-lsb_24_bit,
                       }

    print()
    for value_as_byte_string in sorted(expected_values):
        expected_float_value = expected_values[value_as_byte_string]
        print('testing %33.30f (%s)' % (expected_float_value, binascii.b2a_hex(value_as_byte_string)))
        assert(muslice.util.wav_bytes_to_float(value_as_byte_string) == expected_float_value)


def main():
    test_wav_bytes_to_float()

if __name__ == '__main__':
    main()
