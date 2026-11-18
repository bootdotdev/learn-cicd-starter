# -*- coding: utf-8 -*- #
# Copyright 2025 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Restores a Compute Disk Backup."""


from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.backupdr import util
from googlecloudsdk.api_lib.backupdr.backups import BackupsClient
from googlecloudsdk.api_lib.backupdr.backups import DiskRestoreConfig
from googlecloudsdk.api_lib.util import exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.backupdr import flags
from googlecloudsdk.command_lib.backupdr.restore import disk_flags
from googlecloudsdk.core import log


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
class Disk(base.Command):
  """Restores a Compute Disk Backup."""

  detailed_help = {
      'BRIEF': 'Restores the specified backup',
      'DESCRIPTION': '{description}',
      'EXAMPLES': """\
        To restore a backup `sample-backup` in project `sample-project` and location `us-central1`,
        with `sample-data-store` and `sample-backup-vault`, and additional target properties, run:

          $ {command} sample-backup --project=sample-project --location=us-central1 --backup-vault=sample-backup-vault --data-source=sample-data-source --<target-properties>
        """,
  }

  @staticmethod
  def Args(parser):
    """Specifies additional command flags.

    Args:
      parser: argparse.Parser: Parser object for command line inputs.
    """
    base.ASYNC_FLAG.AddToParser(parser)
    base.ASYNC_FLAG.SetDefault(parser, True)
    flags.AddBackupResourceArg(
        parser, 'The backup of a resource to be restored.'
    )

    disk_flags.AddNameArg(parser)
    disk_flags.AddTargetZoneArg(parser, False)
    disk_flags.AddTargetRegionArg(parser, False)
    disk_flags.AddTargetProjectArg(parser)
    disk_flags.AddReplicaZonesArg(parser, False)
    disk_flags.AddGuestOsFeaturesArgs(parser, False)
    disk_flags.AddDescriptionArg(parser, False)
    disk_flags.AddLicensesArg(parser, False)
    disk_flags.AddLabelsArg(parser, False)
    disk_flags.AddTypeArg(parser, False)
    disk_flags.AddAccessModeArg(parser, False)
    disk_flags.AddProvisionedIopsArg(parser, False)
    disk_flags.AddProvisionedThroughputArg(parser, False)
    disk_flags.AddArchitectureArg(parser, False)
    disk_flags.AddStoragePoolArg(parser, False)
    disk_flags.AddSizeArg(parser, False)
    disk_flags.AddConfidentialComputeArg(parser, False)
    disk_flags.AddResourcePoliciesArg(parser, False)
    disk_flags.AddKmsKeyArg(parser, False)

  def _ParseResourcePolicies(self, resource_policies, project, zone):
    """Parses the resource policies flag."""
    resource_policy_uris = []
    for policy in resource_policies:
      if not policy.startswith('projects/'):
        region = zone.rsplit('-', 1)[0]
        policy = 'projects/{}/regions/{}/resourcePolicies/{}'.format(
            project, region, policy
        )
      resource_policy_uris.append(policy)
    return resource_policy_uris

  def Run(self, args):
    """Constructs and sends request.

    Args:
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the .Args() method.

    Returns:
      ProcessHttpResponse of the request made.
    """
    client = BackupsClient()
    is_async = args.async_

    backup = args.CONCEPTS.backup.Parse()
    restore_config = DiskRestoreConfig()
    restore_config['Name'] = args.name
    restore_config['TargetProject'] = args.target_project
    if args.target_zone:
      restore_config['TargetZone'] = args.target_zone
    if args.target_region:
      restore_config['TargetRegion'] = args.target_region
    if args.replica_zones:
      restore_config['ReplicaZones'] = args.replica_zones
    if args.guest_os_features:
      restore_config['GuestOsFeatures'] = args.guest_os_features
    if args.licenses:
      restore_config['Licenses'] = args.licenses
    if args.description:
      restore_config['Description'] = args.description
    if args.type:
      restore_config['Type'] = args.type
    if args.access_mode:
      restore_config['AccessMode'] = args.access_mode
    if args.provisioned_iops:
      restore_config['ProvisionedIops'] = args.provisioned_iops
    if args.provisioned_throughput:
      restore_config['ProvisionedThroughput'] = args.provisioned_throughput
    if args.architecture:
      restore_config['Architecture'] = args.architecture
    if args.storage_pool:
      restore_config['StoragePool'] = args.storage_pool
    if args.size:
      restore_config['Size'] = args.size
    if args.kms_key:
      restore_config['KmsKey'] = args.kms_key
    if args.labels:
      restore_config['Labels'] = args.labels
      restore_config['ConfidentialCompute'] = args.confidential_compute
    if args.resource_policies:
      restore_config['ResourcePolicies'] = self._ParseResourcePolicies(
          args.resource_policies, args.target_project, args.target_zone
      )
    try:
      operation = client.RestoreDisk(backup, restore_config)
    except apitools_exceptions.HttpError as e:
      raise exceptions.HttpException(e, util.HTTP_ERROR_FORMAT) from e

    if is_async:
      log.RestoredResource(
          backup.Name(),
          kind='backup',
          is_async=True,
          details=util.ASYNC_OPERATION_MESSAGE.format(operation.name),
      )
      return operation

    # For sync operation
    return client.WaitForOperation(
        operation_ref=client.GetOperationRef(operation),
        message=(
            'Restoring backup'
            ' [{}].'
            ' (This operation could take upto 15 minutes.)'.format(
                backup.Name()
            )
        ),
        has_result=False,
    )
