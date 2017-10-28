# coding=utf-8
"""top level of project code"""

import logging
import traceback
import requests

from . import startup

PROG = "arcturus"

MAJOR = 0
MINOR = 1
PATCH = 1

VERSION = f"{MAJOR}.{MINOR}.{PATCH}"

def main():
    # read in command line arguments, if present
    args = startup.get_cli_args(PROG, VERSION)

    # set up logging to file and to console
    startup.setup_logging(args.debug)
    log = logging.getLogger()
    log.debug(">>> arcturus has started")

    # open and parse config
    config = startup.get_config()
    config.update(args.__dict__)

    # create all necessary files and directories
    if not startup.prepare_env(config):
        return

    log.debug(">>> arcturus initialization done")
    try:
        run_program(config)
    except Exception as err:
        log.fatal(">>> o shit waddup, here come dat exception")
        log.fatal(err, exc_info=1)

    log.debug(">>> arcturus has ended")



def run_program(config):
    print("hello")

