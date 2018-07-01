# vim: ts=2:sw=2:et:ft=python

import os
import sys
import boto3
import logging
import json

from getenv import *
import aws

###############################################################################
# Environment vars

# Loggers config
#logger = lambda_logging.setup_logging(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, LOGLEVEL))

TRANSITIONS = {
  'term':   "autoscaling:EC2_INSTANCE_TERMINATING",
  'launch': "autoscaling:EC2_INSTANCE_LAUNCHING"
}

def asg_instances(asg_name = None):
  asg = aws.AutoScalingGroup(REGION)
  asg.describe(asg_name)
  return asg.getInstanceIdsByAz()

def r53_update(instance, azs_instances = {}, host_prefix = ''):
  ec2 = aws.EC2(REGION)
  r53 = aws.Route53(R53_DOMAIN, R53_ZONE_ID)

  ips = {}
  for az in azs_instances.keys():
    ips[az] = ec2.getInstancesPrivateIp(azs_instances[az])
    logger.info("{} IPs: {}".format(az, ips[az]))
    record_name = "{}-{}.{}".format(
      host_prefix, 
      az.split('-')[2], 
      r53.domain
    )
    r53.RecordUpsert(record_name, ips[az])


def main(event, context):

  if R53_DOMAIN == "" and R53_ZONE_ID == "":
    raise Exception("You need to define either R53_DOMAIN or R53_ZONE_ID environment vars")

  if DRY_RUN:
    logger.warning("Changes will not be applyed to Route53 resource records (DRY_RUN:{})".format(DRY_RUN))

  # Get the SNS event message
  msg = json.loads(event['Records'][0]['Sns']['Message'])

  if logger.isEnabledFor("DEBUG"):
    for k,v in msg.iteritems():
      logger.debug("{}: {}".format(k, v))

  transition = msg['LifecycleTransition'].split('_')[-1].lower().capitalize()

  logger.info("Transition: {}".format(msg['LifecycleTransition']))
  logger.info("{} instance {}".format(transition, msg['EC2InstanceId']))

  az_instances = asg_instances(msg['AutoScalingGroupName'])

  event_instance_id = msg['EC2InstanceId']
 
  event_instance_az = filter(
    lambda i: event_instance_id in az_instances[i], az_instances
  )

  if msg['LifecycleTransition'] == TRANSITIONS['term']:
    pass

  if msg['LifecycleTransition'] == TRANSITIONS['launch']:
    pass

  logger.debug("Instances: {}".format(az_instances))

  host_prefix = msg['AutoScalingGroupName'].replace('-asg', '')
  r53_update(msg['EC2InstanceId'], az_instances, host_prefix)

  return True

