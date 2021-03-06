# coding=utf-8
"""
convenience methods to simplify the process of loading json then validating it with a schema, with or
without filling in default values where applicable

this stuff isn't pretty, but it should be fairly stable.
"""
from jsonschema import Draft4Validator, validators
from .ArcturusCore import NAME
import json
import logging
import importlib
from datetime import datetime
import iso8601


def get_config(config_json_path, config_json_schema, default_json_path) -> dict:
    """read and parse the user config.

    if config.json is not found, it is created form defaults and this function exits the program
    if config.json is found and is readable, it is validated against the schema then returned

    :returns: validated json object.  all non-required properties in the schema will be filled in with defaults
    """
    log = logging.getLogger()
    try:
        with open(config_json_path) as infile:
            log.debug(f"{config_json_path} (raw file before parsing):")
            for line in infile:
                log.debug(line.rstrip())

    except FileNotFoundError:
        with open(default_json_path) as infile:
            with open(config_json_path, 'w') as outfile:
                contents = json.load(infile)
                contents['lastrun'] = datetime.isoformat(datetime.now())
                json.dump(contents, outfile, indent=4)
        log.warning(f"{config_json_path} was missing and has been created from defaults")

    config = json.load(open(config_json_path))
    schema = json.load(open(config_json_schema))

    clean_config = validate_json_supply_defaults(obj=config, schema=schema)

    site_key = clean_config['site']



    try:
        clean_config['lastrun'] = iso8601.parse_date(str(clean_config['lastrun']))
    except iso8601.ParseError as err:
        log.error(f"couldn't read lastrun field in config file: {str(clean_config['lastrun'])} is not iso8601 format")
        raise err

    log.debug(f"{config_json_path} contents (parsed and validated, with all fields):")
    for key, val in clean_config.items():
        log.debug("    {:<24} {}".format(key + ':', str(val)))

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
