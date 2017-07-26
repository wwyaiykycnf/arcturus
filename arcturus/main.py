# coding=utf-8
"""top level of project code"""

import logging
import traceback

from . import startup

def main():
    # prepare the logging
    startup.setup_logging()
    main_log = logging.getLogger('root')

    main_log.debug(">>> arcturus has started")

    # open and parse config
    config = startup.get_config()

    # create all necessary files and directories
    if not startup.prepare_env(config):
        return

    run_program(config)

def run_program(config):
    print("hello")

