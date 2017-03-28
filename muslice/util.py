

def wav_bytes_to_float(in_bytes):
    """
    converts a string of bytes read in from a .wav file to a floating point value between -1.0 and almost 1.0
    :param in_bytes: string of bytes, typically between 1 and 3 bytes but there is no actual restriction
    :return: value between -1.0 and 1.0 minus one least significant bit
    """
    bits = len(in_bytes)*8
    int_val = 0
    for b in in_bytes:
        int_val = (int_val << 8) | b
    if in_bytes[0] >= 0x80:
        # negative
        int_val = -((0x1 << bits) - int_val)
    return float(int_val)/pow(2.0, bits-1)


def mix(output_folder):
    raise NotImplementedError
