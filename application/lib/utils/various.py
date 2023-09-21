import re
from typing import Callable

from tornado.ioloop import IOLoop


def snake_to_upper_camel(*args: str) -> str:
    regex = r"[^\r\n\t\f\v\ _]+"
    segments = []
    for word in args:
        segments.append(
            "".join([segment.capitalize() for segment in re.findall(regex, word)])
        )

    return "".join(segments)


def fire_and_forget(func: Callable, loop: IOLoop = None, **kwargs):
    used_loop = loop if loop is not None else IOLoop.current()
    used_loop.add_callback(func, **kwargs)
