import logging
import sys

DEFAULT_FORMAT = (
    '%(asctime)s - %(levelname)s [%(process)d] %(name)s: %(message)s'
)


def setup_logging(
    file_path,
    fmt=None,
    level=logging.INFO,
    print_console=False
):
    """ Setup logging
    :param file_path: a file path
    :param fmt: a format to use in the log
    :param level: a level to use
    :param print_console: dump logs to console as well
    :return:
    """
    fmt = fmt or DEFAULT_FORMAT
    formatter = logging.Formatter(fmt)
    if isinstance(level, str):
        level = logging.getLevelName(level.upper())

    # everything to file
    filelog = logging.FileHandler(file_path, delay=True)
    filelog.setLevel(level)
    filelog.setFormatter(formatter)

    console = logging.StreamHandler(stream=sys.stdout)
    console.setLevel(level)
    console.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(filelog)
    if print_console:
        root.addHandler(console)

    # disabling log messages from the Requests library
    # https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logging.getLogger("kafka").setLevel(logging.WARNING)
