from http import HTTPStatus
from typing import Any, cast

from tornado import httputil
from tornado.log import access_log
from tornado.web import Application

from application.lib.tornado.request_handler import (
    ApplicationRequestHandler,
    ApplicationErrorHandler,
)


class WebApplication(Application):
    def log_request(self, handler: ApplicationRequestHandler) -> None:
        if "log_function" in self.settings:
            self.settings["log_function"](handler)
            return
        if handler.get_status() < 400:
            log_method = access_log.info
        elif handler.get_status() < 500:
            log_method = access_log.warning
        else:
            log_method = access_log.error
        request_time = 1000.0 * handler.request.request_time()
        log_method(
            {
                "msecs": f"{request_time:.2f}",
                "status": handler.get_status(),
                **handler._request_summary(),
                "message": "-",
            }
        )

    def find_handler(self, request: httputil.HTTPServerRequest, **kwargs: Any):
        route = self.default_router.find_handler(request)
        if route is not None:
            return route

        if self.settings.get("default_handler_class"):
            return self.get_handler_delegate(
                request,
                self.settings["default_handler_class"],
                self.settings.get("default_handler_args", {}),
            )

        return self.get_handler_delegate(
            request,
            ApplicationErrorHandler,
            {"status_code": HTTPStatus.NOT_FOUND},
        )
