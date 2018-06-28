
import logging

from asg_event.getenv import *
from asg_event.main   import main

logger = logging.getLogger('lambda_handler')
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    main(event, context)

# vim:ts=4:sw=4:et:ft=python
