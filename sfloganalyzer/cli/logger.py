""" CLI logger """
import contextlib
import logging
import os
import re
import sys
import tempfile

from sfloganalyzer.utils.logging import get_gist_logger


try:
    import colorama
except ImportError:
    # coloredlogs only installs colorama on Windows
    pass


def init_logger(debug=False):
    """Initialize the logger"""

    logger = logging.getLogger(__name__.split(".")[0])
    # for handler in logger.handlers:  # pragma: no cover
    #     logger.removeHandler(handler)

    if os.name == "nt" and "colorama" in sys.modules:  # pragma: no cover
        colorama.init()

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if debug:  # pragma: no cover
        # Referenced from:
        # https://github.com/urllib3/urllib3/blob/cd55f2fe98df4d499ab5c826433ee4995d3f6a60/src/urllib3/__init__.py#L48
        def add_rich_logger(
            module: str, level: int = logging.DEBUG
        ) -> logging.StreamHandler:
            """Retrieve the logger for the given module.
            Remove all handlers from it, and add a single RichHandler."""
            logger = logging.getLogger(module)
            for handler in logger.handlers:
                logger.removeHandler(handler)

            logger.setLevel(level)
            logger.debug(f"Added rich.logging.RichHandler to logger: {module}")
            return handler


def get_tempfile_logger():
    """Creates a logger that writes to a temporary
    logfile. Returns the logger and path to tempfile"""
    logger = logging.getLogger("tempfile_logger")
    file_handle, filepath = tempfile.mkstemp()
    # close the file as it will be opened again by FileHandler
    os.close(file_handle)
    handler = logging.FileHandler(filepath, encoding="utf-8")
    handler.terminator = ""
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger, filepath


@contextlib.contextmanager
def tee_stdout_stderr(args, logger, tempfile):
    """Tee stdout and stderr so that they're also routed to
    a log file. Add the current command arguments
    as the first item in the log."""
    real_stdout_write = sys.stdout.write
    real_stderr_write = sys.stderr.write

    # Add current command args as first line in logfile
    logger.debug(" ".join(args) + "\n")

    def stdout_write(s):
        output = strip_ansi_sequences(s)
        logger.debug(output)
        real_stdout_write(s)

    def stderr_write(s):
        output = strip_ansi_sequences(s)
        logger.debug(output)
        real_stderr_write(s)

    sys.stdout.write = stdout_write
    sys.stderr.write = stderr_write
    try:
        yield
    finally:
        # reset write functions
        sys.stdout.write = real_stdout_write
        sys.stderr.write = real_stderr_write

        # close temporary logfile
        logger.handlers[0].close()

        # log contents of tempfile to rotating log files
        with open(tempfile, "r", encoding="utf-8", errors="backslashreplace") as f:
            contents = f.read()

        logger = get_gist_logger()
        logger.debug(contents)
        # delete temporary log file
        os.remove(tempfile)


def strip_ansi_sequences(input):
    """Strip ANSI sequences from what's in buffer"""
    ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
    return ansi_escape.sub("", input)
