# coding=utf-8
"""
functions used in startup process of arcturus
"""
from jsonschema import Draft4Validator, validators
import json
import shutil
import logging
import logging.handlers
import pathlib
import os
import ctypes
from shutil import copyfile

def get_config() -> dict:
    """read and parse the user config.

    if config.json is not found, it is created form defaults and this function exits the program
    if config.json is found and is readable, it is vaildated against the schema then returned

    :returns: validated json object.  all non-required properties in the schema will be filled in with defaults
    """
    log = logging.getLogger("get_config")
    try:
        with open('config.json') as infile:
            log.debug("config.json (raw file before parsing):")
            for line in infile:
                log.debug(line.rstrip())
        config = json.load(open("config.json"))

    except FileNotFoundError:
        shutil.copyfile(src="arcturus/resources/config_default.json", dst="config.json")
        log.fatal("config.json was missing and has been created.  please inspect the generated file and try again")
        exit(-1)

    schema = json.load(open("arcturus/resources/config_schema.json"))
    clean_config = validate_json_supply_defaults(obj=config, schema=schema)

    log.info("config.json contents (parsed and validated, with all fields):")
    for key, val in clean_config.items():
        log.info("    {:<24} {}".format(key+':', val))

    return clean_config


def setup_logging():
    """
    sets up logging so messages with error and higher go to console but all levels log to rotating files
    :return:
    """

    # the log file will use all settings applied to the root_logger
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    root_formatter = logging.Formatter(fmt='%(asctime)s %(name)-21s %(levelname)-8s %(message)s',
                                       datefmt='%Y-%m-%d %H:%M:%S')

    # define a Handler which writes ERROR messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    console.setFormatter(logging.Formatter('%(name)-21s: %(levelname)-8s %(message)s'))  # simpler format for console
    root_logger.addHandler(console)

    # create the log/ directory if needed
    pathlib.Path('log').mkdir(parents=True, exist_ok=True)

    # define a rotating file handler that logs everything to file (debug)
    rotating_file = logging.handlers.RotatingFileHandler(
        filename='log/debug_log.txt',
        maxBytes=8388608,  # ~8MB (2^23) seems reasonable
        backupCount=10,
    )
    rotating_file.setFormatter(root_formatter)
    root_logger.addHandler(rotating_file)


def __extend_with_default(validator_class):
    """
    extends the supplied validator class to fill in defaults for missing optional properties

    usage:
    DefaultValidatingDraft4Validator(schema).validate(obj)
    
    :seealso: https://python-jsonschema.readthedocs.io/en/latest/faq
    
    :param validator_class: validator object from the jsonschema module
    :type validator_class: Draft4Validator
    :return: Draft4Validator which also validates defaults
    """
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for prop, sub_schema in properties.items():
            if "default" in sub_schema:
                instance.setdefault(prop, sub_schema["default"])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {"properties" : set_defaults},
    )


def validate_json_supply_defaults(obj, schema):
    """
    validates and returns the obj against schema, setting any missing optional fields to their default values

    this function can mutate the obj argument.  if not all of its optional fields exist it will add them
    :param obj: json object to validate
    :param schema: json schema which obj must comply to
    :return: validated json object with all missing optional fields set to their default values
    """
    default_validator = __extend_with_default(Draft4Validator)
    default_validator(schema).validate(obj)
    return obj

    # usage:
    # DefaultValidatingDraft4Validator(schema).validate(obj)


def create_file(file_name: str, file_desc: str, default=None) -> bool:

    log = logging.getLogger('create_file')
    file_path = pathlib.Path(file_name)

    if file_path.exists() and file_path.is_file():
        log.debug(f"located {file_desc} at {str(file_path)}")
        return True

    else:  # we need to make the file
        os.makedirs(os.path.dirname(file_path.absolute()), exist_ok=True)

        # now the path is created (if needed)
        if default is not None:
            copyfile(src=default, dst=file_name)
        else:
            file_path.touch()

        log.debug(f"created {file_desc} at {str(file_path)}")
        return False


def prepare_env(cfg) -> bool:
    """
    creates all required files and folders, if needed
    :param cfg: validated config dictionary
    :return: true if OK to proceed, else false
    """
    log = logging.getLogger('prepare_env')
    log.debug(f"cwd = {os.getcwd()}")

    # always create download dir
    os.makedirs(cfg['download_dir'], exist_ok=True)
    log.debug(f"created download_dir at {cfg['download_dir']}")

    success = True

    # if taglist is not there, create it and then terminate
    key = 'taglist_file'
    if not create_file(file_desc=key, file_name=cfg[key], default='arcturus/resources/taglist_default.txt'):
        log.critical(f"{key} '{cfg[key]}' was not found and has been created from defaults")
        log.critical(f"try editing the file then running this program again")
        success = False

    # if using a blacklist, create if it if needed (no need to terminate in this case)
    if not cfg['blacklist_ignored']:
        key = 'blacklist_file'
        create_file(file_desc=key, file_name=cfg[key], default='arcturus/resources/blacklist_default.txt')

    # if cache is enabled, create it if needed (not need to terminate in this case).  also hide this file
    if not cfg['advanced_duplicates']:
        key = 'advanced_cache'
        create_file(file_desc=key, file_name=cfg[key])
        if os.name == 'nt':
            file_attribute_hidden = 0x02
            ret = ctypes.windll.kernel32.SetFileAttributesW(cfg[key], file_attribute_hidden)

    return success




