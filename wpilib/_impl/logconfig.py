# novalidate

import logging
import pprint

# TODO: Make these configurable
log_datefmt = "%H:%M:%S"
log_format = "%(asctime)s:%(msecs)03d %(levelname)-8s: %(name)-20s: %(message)s"


def configure_logging(verbose):
    formatter = VerboseExceptionFormatter(fmt=log_format, datefmt=log_datefmt)

    # console logging
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logging.root.addHandler(handler)
    logging.root.setLevel(logging.DEBUG if verbose else logging.INFO)


MAX_VARS_LINES = 30
MAX_LINE_LENGTH = 100


class VerboseExceptionFormatter(logging.Formatter):
    """
    Taken from http://word.bitly.com/post/69080588278/logging-locals
    """

    def __init__(self, log_locals_on_exception=True, *args, **kwargs):
        self._log_locals = log_locals_on_exception
        super(VerboseExceptionFormatter, self).__init__(*args, **kwargs)

    def formatException(self, exc_info):
        # First get the original formatted exception.
        exc_text = super(VerboseExceptionFormatter, self).formatException(exc_info)
        if not self._log_locals:
            return exc_text
        # Now we're going to format and add the locals information.
        output_lines = [exc_text, "\n"]

        # Retrieve locals from the innermost exception
        exc = exc_info[1]
        while exc.__cause__:
            exc = exc.__cause__

        tb = exc.__traceback__  # This is the outermost frame of the traceback.
        if tb:  # this should always be true, but sometimes someone messes up
            while tb.tb_next:
                tb = tb.tb_next  # Zoom to the innermost frame.
            output_lines.append("Locals at innermost frame:\n")
            locals_text = pprint.pformat(tb.tb_frame.f_locals, indent=2)
            locals_lines = locals_text.split("\n")
            if len(locals_lines) > MAX_VARS_LINES:
                locals_lines = locals_lines[:MAX_VARS_LINES]
                locals_lines[-1] = "..."
            output_lines.extend(
                line[: MAX_LINE_LENGTH - 3] + "..."
                if len(line) > MAX_LINE_LENGTH
                else line
                for line in locals_lines
            )
            output_lines.append("\n")
        return "\n".join(output_lines)
