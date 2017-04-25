
import os
import shutil
import glob

from muslice import logger

from test_muslice import tst_util


def _remove_folder(folder_path):
    # not given or 0 = delete everything
    try:
        s = 'removing %s' % folder_path
        print(s)
        if logger.log:
            logger.log.info(s)
        shutil.rmtree(folder_path)
    except FileNotFoundError:
        pass

def pytest_sessionstart(session):

    # remove old logs and then init log
    _remove_folder(tst_util.get_log_folder())
    os.makedirs(tst_util.get_log_folder(), exist_ok=True)
    logger.init(tst_util.get_log_folder())

    delete_starting = tst_util.get_delete_starting()
    if delete_starting is not None:
        if delete_starting == 0:
            # 0 - delete "in"
            _remove_folder(tst_util.get_input_data_root())

        if delete_starting <= 1:
            # 1 - delete "out" "full"
            folders = glob.glob(os.path.join(tst_util.get_output_data_root(), '*', 'full', '*'))
            logger.log.info('glob found : %s' % str(folders))
            [_remove_folder(f) for f in folders]

        if delete_starting <= 2:
            # 2 - delete "out" "segments"
            folders = glob.glob(os.path.join(tst_util.get_output_data_root(), '*', 'segments', '*'))
            logger.log.info('glob found : %s' % str(folders))
            [_remove_folder(f) for f in folders]

def pytest_addoption(parser):
    #
    # These switches are used to reduce the test runtime.  There are 2 ways to reduce the test runtime:
    # 1) Run less, shorter tests (less songs, shorter songs).  We specify 'n_tests', which can have a value from
    #    1 to N where N is the number of recordings.  Specifying 1 will run the shortest test only.
    #    Specifying 2 will run test 0 (shortest) and test 1 (the next longer test), and so on.  If the value is not
    #    given we run all tests.
    # 2) Re-do less from the earlier phases.  This controls what we keep from a prior run (if anything).  This is
    #    an integer from 0 to N-1, where N is the number of phases.  We delete files from this phase and onward
    #    (note it doesn't make sense to keep later files but delete earlier files, so that's why this is a number
    #    a not a series of specfic phase selections).  A value of 0 deletes all phases (since it deletes phase 0 and all
    #    subsequent phases).  If no value is specified no files are deleted.  Assignment from a number to a phase is
    #    arbitrary - see the code for the mapping.
    #
    parser.addoption("--n_tests", action="store",  help="number of tests to run")
    parser.addoption("--delete_starting", action="store", help="delete files from this phase and after (omitted = run all tests")
