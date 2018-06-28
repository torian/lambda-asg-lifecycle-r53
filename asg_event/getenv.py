# vim: ts=2:sw=2:et:ft=python

import os
import distutils.util

###############################################################################

RUN_LOCAL = distutils.util.strtobool(os.environ.get('LOCAL', 'False'))

# DRY_RUN: If set to True, simulate what would be done
DRY_RUN = distutils.util.strtobool(os.environ.get('DRY_RUN', 'True'))

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()

# AWS Region & Profile
#  AWS_REGION should always be specified
#  AWS_PROFILE might be specified when running locally (development)
AWS_REGION  = os.environ.get('AWS_REGION',  'us-east-2')
AWS_PROFILE = os.environ.get('AWS_PROFILE', '')

# R53 settings and toggles
#  R53_ZONE_ID:     Define which zone to use by Zone ID
#  R53_DOMAIN:      Define which zone to use by Domain. Takes precedence over R53_ZONE_ID
#  R53_RR_TTL:      Resource record TTL. Defaults to 30s
#
R53_ZONE_ID = os.environ.get('R53_ZONE_ID', '')
R53_DOMAIN  = os.environ.get('R53_DOMAIN',  '')
R53_RR_TTL  = os.environ.get('R53_RR_TTL',  30)

