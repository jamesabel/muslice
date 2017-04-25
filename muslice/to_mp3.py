
import os
import subprocess

from muslice import folders
from muslice import logger


def to_mp3(output_folder, bit_rate_kbps, cloud_base_url):
    """
    convert wav files to mp3s
    :param output_folder: main output root for muslice
    :param bit_rate_kbps: bit rate in kbps as a string
    :param dropbox_user_number: i.e. for public links: https://dl.dropboxusercontent.com/u/<dropbox_user_number>
    :return: 
    """

    html = ['<body>']

    # sox -t wav --norm=-1 TASCAM_0045_1_fp32.wav -t mp3 -C 384.0 TASCAM_0045_1.mp3
    wav_folder = folders.segments_mix_wav_folder(output_folder)
    for wav_file in os.listdir(wav_folder):
        wav_path = os.path.join(wav_folder, wav_file)
        if os.path.isfile(wav_path):
            mp3_folder = folders.segments_mix_mp3_folder(output_folder)
            mp3_file_name = os.path.basename(wav_path).replace('.wav', '.mp3')
            os.makedirs(mp3_folder, exist_ok=True)
            # <bit_rate>.0 , where the .0 means highest quality
            sox_cmd = ' '.join(['/usr/local/bin/sox', '-t', 'wav', '--norm=-1', wav_path, '-t', 'mp3', '-C', str(bit_rate_kbps) + '.0', os.path.join(mp3_folder, mp3_file_name)])
            logger.log.info(sox_cmd)
            subprocess.run(sox_cmd, shell=True)

            url = '%s/mp3/%s' % (cloud_base_url, mp3_file_name)
            html.append('<a href="%s">%s</a>' % (url, mp3_file_name))
            html.append('<br>')

    html.append('</body>')

    return '\n'.join(html)