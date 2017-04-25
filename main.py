
import argparse
import logging
import time

from muslice import MuSlice
import muslice.logger as logger


def main():
    start = time.time()

    logger.init('log')  # todo: use appdirs

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='muslice_config.json', help='configuration file path')
    parser.add_argument('-n', '--nuke', action='store_true', help='remove (nuke) all prior output files before running')
    parser.add_argument('-v', '--verbose', action='store_true', help='print verbose messages')
    args = parser.parse_args()

    if args.verbose:
        logger.set_console_handler_level(logging.INFO)
        logger.set_file_handler_level(logging.DEBUG)

    m = MuSlice(args.config, args.nuke)
    m.run()

    if args.verbose:
        s = 'overall run time : %f sec' % (time.time() - start)
        print(s)
        logger.log.info(s)

if __name__ == '__main__':
    main()
