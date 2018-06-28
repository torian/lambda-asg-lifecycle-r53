
import logging
import sys

from getenv import *

def setup_logging(name):
    logger = logging.getLogger()
    for h in logger.handlers:
      logger.removeHandler(h)
    
    h = logging.StreamHandler(sys.stdout)
    
    FORMAT = '[%(asctime)s] %(levelname)s - {}: %(message)s'.format(name)
    h.setFormatter(logging.Formatter(FORMAT))
    logger = logging.getLogger(name)
    logger.addHandler(h)
    logger.setLevel(getattr(logging, LOGLEVEL))
    
    return logger

