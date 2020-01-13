import hal
import sys
import traceback
import logging
import wpilib

logger = logging.getLogger("wpilib.ds")


def report_error(
    isError: bool, code: int, error: str, printTrace: bool, exc_info=None
) -> None:
    traceString = ""
    locString = ""

    if printTrace:
        # If an exception is passed in or an exception is present
        if exc_info is None:
            exc_info = sys.exc_info()

        exc = exc_info[0]
        if exc is None:
            tb = traceback.extract_stack()[:-2]
        else:
            tb = traceback.extract_tb(exc_info[2])

        locString = "%s.%s:%s" % (tb[-1][0], tb[-1][1], tb[-1][2])

        trc = "Traceback (most recent call last):\n"
        stackstr = trc + "".join(traceback.format_list(tb))
        if exc is not None:
            stackstr += "  " + ("".join(traceback.format_exception(*exc_info))).lstrip(
                trc
            )
        traceString += "\n" + stackstr

        if exc is None:
            logger.error(error + "\n" + traceString)
        else:
            logger.error(error, exc_info=exc_info)

    elif isError:
        logger.error(error)
    else:
        logger.warning(error)

    hal.sendError(
        isError,
        code,
        False,
        error.encode("utf-8"),
        locString.encode("utf-8"),
        traceString.encode("utf-8"),
        0 if wpilib.RobotBase.isSimulation() else 1,
    )
