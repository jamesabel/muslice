
import argparse
import logging

import muslice.logger


def main():
    muslice.logger.init()

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='folder to traverse to find the input wave files')
    parser.add_argument('-o', '--mono', required=True, help='folder for the mono wave files')
    parser.add_argument('-v', '--verbose', action='store_true', help='print verbose messages')
    parser.add_argument('-c', '--convert', action='store_true', help='convert stereo wav files to multiple mono wav files')
    parser.add_argument('-m', '--mix', action='store_true', help='mix mono wav files to a stereo output file')
    args = parser.parse_args()

    if args.verbose:
        muslice.logger.set_console_handler_level(logging.INFO)
        muslice.logger.set_file_handler_level(logging.DEBUG)

    m = muslice.MuSlice(args.input, args.mono, args.convert, args.mix)
    m.run()

if __name__ == '__main__':
    main()
