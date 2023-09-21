from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from atexit import register


class QueueListenerHandler(QueueHandler):
    def __init__(self, handlers, respect_handler_level=False):
        super().__init__(Queue(-1))
        self._listener = QueueListener(
            self.queue,
            *handlers,
            respect_handler_level=respect_handler_level,
        )
        self.start()
        register(self.stop)

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()
