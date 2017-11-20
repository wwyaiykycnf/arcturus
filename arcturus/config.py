# coding=utf-8
"""
convenience methods to simplify the process of loading json then validating it with a schema, with or
without filling in default values where applicable

this stuff isn't pretty, but it should be fairly stable.
"""
from jsonschema import Draft4Validator, validators
import json
import shutil
import logging
from .ArcturusSources import get_by_name


def get_config(config_json_path, config_json_schema, default_json_path) -> dict:
    """read and parse the user config.

    if config.json is not found, it is created form defaults and this function exits the program
    if config.json is found and is readable, it is validated against the schema then returned

    :returns: validated json object.  all non-required properties in the schema will be filled in with defaults
    """
    log = logging.getLogger("get_config")
    try:
        with open(config_json_path) as infile:
            log.debug(f"{config_json_path} (raw file before parsing):")
            for line in infile:
                log.debug(line.rstrip())

    except FileNotFoundError:
        shutil.copyfile(src=default_json_path, dst=config_json_path)
        log.warning(f"{config_json_path} was missing and has been created from defaults")

    config = json.load(open(config_json_path))
    schema = json.load(open(config_json_schema))
    clean_config = validate_json_supply_defaults(obj=config, schema=schema)

    log.debug(f"{config_json_path} contents (parsed and validated, with all fields):")
    for key, val in clean_config.items():
        log.debug("    {:<24} {}".format(key + ':', val))

    try:
        site_key = clean_config['site']
        clean_config['site'] = get_by_name(site_key)
    except ImportError as err:
        raise ImportError(f"Could not import module {site_key}") from err

    return clean_config


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
        validator_class, {"properties": set_defaults},
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
