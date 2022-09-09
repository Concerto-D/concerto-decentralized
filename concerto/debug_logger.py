import logging
import sys

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
log.addHandler(handler)

log_component = logging.getLogger("components_semantics")
log_component.setLevel(logging.DEBUG)
log_component.addHandler(handler)


class LogMessageOnce(logging.Filter):
    """
    For component debug messages (activation, deactivation of ports, entering, leaving places etc)
    prevent msg flooding due to the loop
    """
    msg_logged = set()
    def filter(self, record):
        if record.msg in self.msg_logged:
            return False
        self.msg_logged.add(record.msg)
        return True


log_component.addFilter(LogMessageOnce())


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    log.debug("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception
