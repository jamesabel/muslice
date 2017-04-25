
from os.path import join


def _full(output_folder):
    return join(output_folder, 'full')


def _segment(output_folder):
    return join(output_folder, 'segment')


def mono_wav_folder(output_folder, recording):
    return join(_full(output_folder), recording, 'wav')


def mono_wav_fp_folder(output_folder, recording):
    return join(_full(output_folder), recording, 'wavfp')


def mono_meters_folder(output_folder, recording):
    return join(_full(output_folder), recording, 'meters')


def segments_mono_folder(output_folder, recording, segment):
    return join(_segment(output_folder), recording, str(segment))


def segments_mix_wav_folder(output_folder):
    return join(_segment(output_folder), 'mixwav')


def segments_mix_mp3_folder(output_folder):
    return join(_segment(output_folder), 'mixmp3')