from dateutil import parser, tz

from marshmallow import fields, ValidationError


class PositiveInt(fields.Int):
    default_error_messages = {"zero_or_lower": "Value must be greater than 0"}

    def _validate(self, value):
        if value <= 0:
            raise ValidationError(self.default_error_messages["zero_or_lower"])

        super(PositiveInt, self)._validate(value)


class ConvertedAwareDateTime(fields.DateTime):
    default_error_messages = {
        "non_parsable_format": "Non-parsable datetime format",
        "missing_timezone": "Missing timezone info",
    }

    def _deserialize(self, value, attr, obj, **kwargs):
        try:
            parsed_datetime = parser.parse(value)
        except ValueError:
            raise ValidationError(self.default_error_messages["non_parsable_format"])

        # enforcing timezone aware datetime
        if not parsed_datetime.tzinfo:
            raise ValidationError(self.default_error_messages["missing_timezone"])

        if parsed_datetime.tzinfo != tz.UTC:
            parsed_datetime = parsed_datetime.astimezone(tz.UTC)

        return parsed_datetime

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return value

        return value.replace(tzinfo=tz.UTC).isoformat()
