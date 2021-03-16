import logging
import os
import sys

try:
    debug_mode = os.environ["DEBUG"]
except KeyError:
    debug_mode = False

if debug_mode:
    file_handler = logging.FileHandler(filename='gadown.log')
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=[file_handler]
    )

stdout_handler = logging.StreamHandler(sys.stdout)
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[stdout_handler]
)


def get_logger():
    return logging.getLogger("gadown")
