from typing import Dict, Union

from tornado.escape import json_encode, utf8
from tornado.web import RequestHandler, ErrorHandler, HTTPError


class ApplicationRequestHandler(RequestHandler):
    def _request_summary(self) -> Dict:
        return {
            "uri": self.request.uri,
            "method": self.request.method,
            "addr": self.request.remote_ip,
            "rsize": self._headers.get("Content-Length", None),
            "proto": self.request.version,
            "headers": len(self._headers),
        }

    def write(self, chunk: Union[str, bytes, dict, list]) -> None:
        try:
            super(ApplicationRequestHandler, self).write(chunk)
        except TypeError:
            if isinstance(chunk, list):
                chunk = utf8(json_encode(chunk))
                self.set_header("Content-Type", "application/json; charset=UTF-8")
                self._write_buffer.append(chunk)
            else:
                raise


class ApplicationErrorHandler(ErrorHandler, ApplicationRequestHandler):
    pass


class ApplicationCustomError(HTTPError):
    pass
