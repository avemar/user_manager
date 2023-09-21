from http import HTTPStatus
from typing import Callable
from functools import wraps
from logging import getLogger

from application.lib.validation import ValidationException, UnsupportedPayloadException
from application.lib.tornado.request_handler import ApplicationCustomError


logger = getLogger("controller")


def handle_server_errors(request_handler_method: Callable):
    @wraps(request_handler_method)
    async def log_error(self, *args, **kwargs):
        try:
            await request_handler_method(self, *args, **kwargs)
        except ValidationException as ve:
            logger.error(ve)
            self.set_status(HTTPStatus.BAD_REQUEST)
            self.write({"error": str(ve)})
        except UnsupportedPayloadException as ue:
            logger.error(ue)
            self.set_status(HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
            self.write({"error": "Unsupported Media Type"})
        except ApplicationCustomError as re:
            raise
        except Exception as e:
            logger.exception("Generic Exception")
            logger.error(f"EXC TYPE: {type(e)}")
            self.set_status(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.write({"error": "Internal Server Error"})

    return log_error
