# vim: ts=2:sw=2:et:ft=python

import os
import boto3
import json
import logging

from getenv import *

###############################################################################

# Loggers config
#logger = lambda_logging.setup_logging(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, LOGLEVEL))

logger_botocore = logging.getLogger('botocore')
logger_botocore.setLevel('WARNING')

logger_boto3 = logging.getLogger('boto3')
logger_boto3.setLevel('WARNING')

###############################################################################

class AutoScalingGroup():

  def __init__(self, region = REGION):
    self.conn = boto3.client('autoscaling', region_name = region)

    self.asg        = None
    self.asg_az_ids = {}

  def describe(self, name):
    self.asg = self.conn.describe_auto_scaling_groups(
      AutoScalingGroupNames = [ name ]
    )['AutoScalingGroups'][0]

    if LOGLEVEL == 'DEBUG':
      logger.debug("ASG Instances:")
      for i in self.asg['Instances']:
        logger.debug("  Instance:")
        for k,v in i.iteritems():
          logger.debug("    {}: {}".format(k, v))

    return self.asg

  def getInstanceIds(self):
    if self.asg is None:
      return None
    return map(
      lambda i: i['InstanceId'], self.asg['Instances']
    )

  def getInstanceIdsByAz(self):
    for az in self.asg['AvailabilityZones']:
      logger.debug("Getting instances from AZ {}".format(az))
      self.asg_az_ids[az] = map(
        lambda i: i['InstanceId'], 
        filter(
          lambda j: j['AvailabilityZone'] == az,
          self.asg['Instances']
        )
      )
      logger.debug("AZ instances: {}".format(self.asg_az_ids[az]))
    return self.asg_az_ids


class Route53():

  def __init__(self, domain = "", zone_id = ""):
    self.conn = boto3.client('route53')

    self.hosted_zones = None
    self.hosted_zone  = None
    self.domain       = domain
    self.zone_id      = zone_id

    if self.zone_id is "" and self.domain is not "":
      self.getHostedZones()
      self.zone_id = filter(
        lambda z: z['Name'].rstrip('.') == domain, self.hosted_zones
      )[0]['Id'].split('/')[2]
      self.getHostedZone(self.zone_id)
    else:
      self.getHostedZone(self.zone_id)
      self.domain = self.hosted_zone['Name']

    logger.debug("Domain: {}".format(self.domain))
    logger.debug("Zone ID: {}".format(self.zone_id))

  def getHostedZones(self):
    self.hosted_zones = self.conn.list_hosted_zones()['HostedZones']

  def getHostedZone(self, zone_id):
    self.hosted_zone = self.conn.get_hosted_zone(Id = zone_id)

  def getDomain(self, domain):
    return self.domain

  def getZoneId(self):
    return self.zone_id

  def RecordUpsert(self, record_name, ip_addresses = []):
    resource_records = []
    if len(ip_addresses) == 0:
      resource_records = [ { "Value": "127.0.0.1" } ]
    else:
      resource_records = map(lambda i: { "Value": i }, ip_addresses)

    logger.info("Updating {} with {}".format(record_name, ip_addresses))
    changes = {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": record_name,
        "Type": "A",
        "ResourceRecords": resource_records,
        "TTL": R53_RR_TTL
      }
    }
    changeBatch  = { 
      "Comment": "{}".format("fixme"), 
      "Changes": [ changes ]
    }

    logger.debug("Route53 UPSERT:")
    logger.debug(json.dumps(changeBatch, indent = 2))

    if DRY_RUN:
        self.conn.change_resource_record_sets(
          HostedZoneId = self.zone_id,
          ChangeBatch  = changeBatch
        )
    else:
      logger.warning("Not updating {} (DRY_RUN:{})".format(record_name, DRY_RUN))

class EC2():

  def __init__(self, region = REGION):
    self.conn = boto3.client('ec2', region_name = region)

  def getInstancesPrivateIp(self, instance_ids = []):
    if len(instance_ids) == 0:
      return []

    instances = self.conn.describe_instances(
      InstanceIds = instance_ids
    )['Reservations'][0]['Instances']
    logger.debug("Found {} instances".format(len(instances)))
    return map (
      lambda i: i['PrivateIpAddress'], instances
    )

