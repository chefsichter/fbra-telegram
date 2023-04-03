import logging
import sys
import time


class StderrLogger:
    STDERR_LOGGER = 'stderr-console'

    def __init__(self, propagate=True):
        self.logger = self._create_logger(propagate)
        self.buf = []
        sys.stderr = self
        self.delay_time = 60
        self.last_log = time.monotonic() - self.delay_time

    def _create_logger(self, propagate):
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        stream_handler.setFormatter(formatter)
        logger = logging.getLogger(self.STDERR_LOGGER)
        logger.addHandler(stream_handler)
        logger.setLevel(level=logging.ERROR)
        logger.propagate = propagate
        return logger

    def write(self, buf):
        now = time.monotonic()
        if (now - self.last_log) > self.delay_time:
            self.last_log = now
            self.logger.error(f"Error from stderr:")
        if buf.endswith('\n'):
            self.buf.append(buf.removesuffix('\n'))
            self.logger.error(''.join(self.buf))
            self.buf = []
        else:
            self.buf.append(buf)

    def flush(self):
        pass

    def getvalue(self):
        pass

