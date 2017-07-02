# coding=utf-8

from jsonschema import Draft4Validator, validators


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
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {"properties" : set_defaults},
    )


def VaidateJsonWithDefaults(obj, schema):
    DefaultValidatingDraft4Validator = __extend_with_default(Draft4Validator)
    DefaultValidatingDraft4Validator(schema).validate(obj)
    return obj

    # usage:
    # DefaultValidatingDraft4Validator(schema).validate(obj)

