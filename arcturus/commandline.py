# coding=utf-8
"""top level of project code"""

import argparse
import ctypes
import logging
import logging.handlers
import os
import pathlib
from pathlib import Path
from shutil import copyfile
from typing import Optional

from . import ArcturusCore
from .config import get_config

CONFIG_JSON_NAME = 'config.json'
CONFIG_SCHEMA_NAME = 'resources/config_schema.json'
CONFIG_DEFAULT_NAME = 'resources/config_default.json'
DEFAULT_TAGLIST_NAME = 'taglist.txt'
DEFAULT_CACHE_NAME = '.cache'


def get_cli_args(program: str, version: str) -> argparse.Namespace:
    """
    gets any arguments from command line then validates and returns them

    :param program:     the program name (used in help/version commands)
    :param version:     the program version (used in help/version commands)
    :return:            namespace with all args
    """
    parser = argparse.ArgumentParser(prog=program)
    parser.add_argument('--version', action='version', version=f"{program} {version}")
    parser.add_argument('--config', default=CONFIG_JSON_NAME,
                        help=f"specify custom config file (default={CONFIG_JSON_NAME})")
    parser.add_argument('--debug', action="store_true", default=False,
                        help="log debug output to terminal")
    return parser.parse_args()


def setup_logging(debug_output: bool = False):
    """
    sets up logging so messages with error and higher go to console but everything is logged to file

    :param debug_output: if true, log debug output to terminal as well as file
    :return: None
    """

    # the log file will use all settings applied to the root_logger
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    root_formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d %(name)-21s %(levelname)-8s %(message)s',
                                       datefmt='%Y-%m-%d %H:%M:%S')

    # define a Handler which writes ERROR messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console_level = logging.DEBUG if debug_output else logging.ERROR
    console.setLevel(console_level)
    console.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(name)-15s: %(levelname)-8s %(message)s',
                                           datefmt='%H:%M:%S'))  # simpler format for console
    root_logger.addHandler(console)

    # create the log/ directory if needed
    pathlib.Path('log').mkdir(parents=True, exist_ok=True)

    # define a rotating file handler that logs everything to file (debug)
    rotating_file = logging.handlers.RotatingFileHandler(
        filename='log/debug_log.txt',
        maxBytes=8388608,  # ~8MB (2^23) seems reasonable
        backupCount=10
    )
    rotating_file.setFormatter(root_formatter)
    root_logger.addHandler(rotating_file)


def make_file_from_template(path: Path, file_desc: str, contents=Optional[Path]):
    """
    creates a file at path with the supplied contents
    :param path:        path to the file to be created
    :param file_desc:   description of the file (for logging)
    :param contents:    if supplied, this file's contents will be copied to the new file
    :return:            None
    """
    path.mkdir(parents=True)
    path.touch()

    if contents:
        copyfile(src=contents, dst=str(path))

    logging.getLogger().debug(f"created {file_desc} at {path}")


def file_exists(path: Path, file_desc: str) -> bool:
    """
    checks if a file exists, automatically logging the result as well as returning it

    :param path:        path to be checked
    :param file_desc:   description of the file (for logging)
    :return:            True if file exists, else false
    """
    if path.exists() and path.is_file():
        logging.getLogger().debug(f"found {file_desc} at {str(path)}")
        return True
    else:
        logging.getLogger().debug(f"{file_desc} {str(path)} either cannot be found or is not a file")
        return False


def prepare_filesystem(config: dict) -> bool:
    """
    creates all required files and folders, if needed
    :param config: validated config dictionary
    :return: true if OK to proceed, else false
    """
    success = True

    log = logging.getLogger('')
    cwd = os.getcwd()
    log.debug(f"cwd = {cwd}")

    # always create download dir
    os.makedirs(config['download_dir'], exist_ok=True)
    log.debug(f"download_dir is {config['download_dir']}")

    # create a cache file if one does not exist, and hide it if on wandows
    cache_path = Path(cwd) / Path(DEFAULT_CACHE_NAME)
    if file_exists(path=cache_path, file_desc="cache"):
        log.debug(f'cache at {str(cache_path)}')
    else:
        make_file_from_template(cache_path, "cache")
        log.debug(f"cache {str(cache_path)} was not found and has been created")
    if os.name == 'nt':  # set the hidden flag if running on wandows
        ctypes.windll.kernel32.SetFileAttributesW(str(cache_path), 0x02)  # why does it have to be this hard?

    # if the taglist is not there, create it.  set success to false now because the taglist is empty.
    taglist_path = Path(cwd) / Path(config['taglist_file'])
    if file_exists(path=taglist_path, file_desc="taglist"):
        log.debug(f"taglist at {str(taglist_path)}")
    else:
        make_file_from_template(taglist_path, "taglist", Path('arcturus/resources/taglist_default.txt'))
        log.critical(f"taglist '{str(taglist_path)}' was not found and has been created from defaults")
        log.critical(f"try editing the file then running this program again")
        success = False

    # if blacklist is ignored, then we can skip all of this
    if config['blacklist_ignored']:
        log.info('blacklist ignored')
    # blacklist will be used, so if it is there, then create it and keep running.
    else:
        blacklist_path = Path(cwd) / Path(config['blacklist_file'])
        if not file_exists(path=blacklist_path, file_desc="blacklist"):
            make_file_from_template(blacklist_path, "blacklist", Path('arcturus/resources/blacklist_default.txt'))
            log.warning(f"blacklist '{str(blacklist_path)}' was not found and has been created from defaults")
        else:
            log.debug(f"blacklist at {str(blacklist_path)}")

    return success


def startup_program() -> {bool, argparse.Namespace, dict}:
    # read in command line arguments, if present
    args = get_cli_args(program=ArcturusCore.NAME, version=ArcturusCore.VERSION)

    # get logs started
    setup_logging(debug_output=args.debug)
    log = logging.getLogger()

    log.debug(">>> arcturus has started")

    # open and parse config then add command line args to this as well
    config = get_config(CONFIG_JSON_NAME, CONFIG_JSON_NAME, CONFIG_DEFAULT_NAME)
    config.update(args.__dict__)

    # startup returning false means the program is not prepared for start
    ready_to_start = prepare_filesystem(config=config)
    log.debug(f">>> arcturus initialization done.  ready to start = {str(ready_to_start).upper()}")

    return ready_to_start, args, config


def run_program(ready, args, config):
    log = logging.getLogger()
    if ready:
        try:
            print("hello")

        except Exception as err:
            log.fatal(">>> o shit waddup, here come dat exception")
            log.fatal(err, exc_info=1)

    log.debug(">>> arcturus has ended")


def main():
    (ready, args, config) = startup_program()

    run_program(ready, args, config)
