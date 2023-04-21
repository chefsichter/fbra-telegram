import datetime
import logging
import sys


class StderrLogger:
    STDERR_LOGGER = 'stderr-console'

    def __init__(self, propagate=True):
        self.modul = 'ERROR - stderr'
        self.logger = self._create_logger(propagate)
        sys.stderr = self
        self.buf = []
        self.delay_time = 60
        self.last_log = datetime.datetime.now() - datetime.timedelta(seconds=self.delay_time)

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
        now = datetime.datetime.now()
        if (now - self.last_log).total_seconds() > self.delay_time:
            self.last_log = now
            str_logging_time_stamp = now.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
            self.buf.append(f"{str_logging_time_stamp} - {self.modul}:\n")
        if buf.endswith('\n'):
            self.buf.append(buf.removesuffix('\n'))
            built_buf = ''.join(self.buf)
            if built_buf == "" or built_buf.isspace():
                built_buf = "_" * 10 + "empty_line" + "_" * 10
            self.logger.error(built_buf)
            self.buf = []
        else:
            self.buf.append(buf)

    def flush(self):
        pass

    def getvalue(self):
        pass

