from json import JSONDecodeError
from typing import Callable
from functools import wraps

from tornado import escape
from tornado.web import RequestHandler
from marshmallow.exceptions import ValidationError


class ValidationException(Exception):
    pass


class UnsupportedPayloadException(Exception):
    pass


def validate(schema_name: str, accept_partial_validation: bool = False):
    def validate_decorator(func: Callable):
        @wraps(func)
        def wrapper(self: RequestHandler, *args, **kwargs):
            try:
                request_arguments = {
                    k: v[0].decode() for k, v in self.request.arguments.items()
                }
                request_body = (
                    escape.json_decode(self.request.body) if self.request.body else {}
                )
                request_arguments.update(request_body)

                duplicated_params = set(request_arguments).intersection(set(kwargs))
                if duplicated_params:
                    raise ValidationError(
                        f"Multiple occurrences of same param/s: {duplicated_params}"
                    )

                request_arguments.update(kwargs)
                validated_data = self.schemas[schema_name].load(request_arguments)
            except ValidationError as e:
                if accept_partial_validation:
                    return func(
                        self, e.valid_data, *args, **kwargs, invalid_data=e.messages
                    )

                raise ValidationException(str(e))
            except (AttributeError, KeyError, TypeError) as e:
                raise ValidationException(repr(e))
            except (JSONDecodeError) as e:
                raise UnsupportedPayloadException(repr(e))

            return func(self, validated_data, *args, **kwargs)

        return wrapper

    return validate_decorator
