from typing import Callable
from functools import wraps
from logging import getLogger


logger = getLogger("generic")


def handle_errors(request_handler_method: Callable):
    @wraps(request_handler_method)
    async def log_error(self, *args, **kwargs):
        try:
            await request_handler_method(self, *args, **kwargs)
        except Exception:
            logger.exception("Generic Exception")

    return log_error
