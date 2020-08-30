from dataclasses import asdict
from datetime import timedelta

import cerberus


class ValidationError(Exception):
    def __init__(self, message, details=None):
        self.details = details
        super().__init__(f'{message}, details: {details}')


timedelta_type = cerberus.TypeDefinition('timedelta', (timedelta, None), ())


class CustomValidator(cerberus.Validator):
    types_mapping = cerberus.Validator.types_mapping.copy()
    types_mapping['timedelta'] = timedelta_type

    def _validate_minseconds(self, minseconds, field, value):
        """ Test the seconds to be at least.

        This is a required comment to deprecate a warning

        The rule's arguments are validated against this schema:
        {'type': 'integer'}
        """
        if minseconds and value.seconds < minseconds:
            self._error(field, f"Must be at least {minseconds}")


def validate(scheme, obj, allow_unknown=False):
    v = CustomValidator(scheme, allow_unknown=allow_unknown)
    if not v.validate(asdict(obj)):
        raise ValidationError('invalid data', details=v.errors)
