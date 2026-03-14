# -*- coding: utf-8 -*- #
# Copyright 2024 Google LLC. All Rights Reserved.
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
"""Restores a Compute Instance Backup."""


from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.backupdr import util
from googlecloudsdk.api_lib.backupdr.backups import BackupsClient
from googlecloudsdk.api_lib.backupdr.backups import ComputeRestoreConfig
from googlecloudsdk.api_lib.util import exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.backupdr import flags
from googlecloudsdk.command_lib.backupdr.restore import compute_flags
from googlecloudsdk.core import log


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
class Compute(base.Command):
  """Restores a Compute Engine VM Backup."""

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

    compute_flags.AddNameArg(parser)
    compute_flags.AddTargetZoneArg(parser)
    compute_flags.AddTargetProjectArg(parser)
    compute_flags.AddNetworkInterfaceArg(parser, False)
    compute_flags.AddServiceAccountArg(parser, False)
    compute_flags.AddScopesArg(parser, False)
    compute_flags.AddCreateDiskArg(parser, False)
    compute_flags.AddDescriptionArg(parser, False)
    compute_flags.AddMetadataArg(parser, False)
    compute_flags.AddLabelsArg(parser, False)
    compute_flags.AddTagsArg(parser, False)
    compute_flags.AddMachineTypeArg(parser, False)
    compute_flags.AddHostnameArg(parser, False)
    compute_flags.AddEnableUefiNetworkingArg(parser, False)
    compute_flags.AddThreadsPerCoreArg(parser, False)
    compute_flags.AddVisibleCoreCountArg(parser, False)
    compute_flags.AddAcceleratorArg(parser, False)
    compute_flags.AddMinCpuPlatform(parser, False)
    # Scheduling Flags
    compute_flags.AddMaintenancePolicyArg(parser, False)
    compute_flags.AddPreemptibleArg(parser, False)
    compute_flags.AddRestartOnFailureArg(parser, False)
    compute_flags.AddMinNodeCpuArg(parser, False)
    compute_flags.AddProvisioningModelArg(parser, False)
    compute_flags.AddInstanceTerminationActionArg(parser, False)
    compute_flags.AddLocalSsdRecoveryTimeoutArg(parser, False)
    compute_flags.AddNodeAffinityFileArg(parser, False)

    compute_flags.AddReservationArgs(parser, False)
    compute_flags.AddEnableDisplayDeviceArg(parser, False)
    compute_flags.AddCanIpForwardArg(parser, False)
    compute_flags.AddPrivateIpv6GoogleAccessArg(parser, False)
    compute_flags.AddNetworkPerformanceConfigsArg(parser, False)
    compute_flags.AddConfidentialComputeArg(parser, False)
    compute_flags.AddDeletionProtectionArg(parser, False)
    compute_flags.AddResourceManagerTagsArg(parser, False)
    compute_flags.AddResourcePoliciesArg(parser, False)
    compute_flags.AddKeyRevocationActionTypeArg(parser, False)
    compute_flags.AddInstanceKmsKeyArg(parser, False)

  def _ParseResourcePolicies(self, resource_policies, project, zone):
    """Parses the resource policies flag."""
    resource_policy_uris = []
    for policy in resource_policies:
      if not policy.startswith('projects/'):
        region = zone.rsplit('-', 1)[0]
        policy = (
            'projects/{}/regions/{}/resourcePolicies/{}'.format(
                project, region, policy
            )
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
    restore_config = ComputeRestoreConfig()
    restore_config['Name'] = args.name
    restore_config['TargetZone'] = args.target_zone
    restore_config['TargetProject'] = args.target_project
    if args.network_interface:
      restore_config['NetworkInterfaces'] = args.network_interface
    if args.service_account:
      restore_config['ServiceAccount'] = args.service_account
    if args.scopes:
      restore_config['Scopes'] = args.scopes
    restore_config['NoScopes'] = args.no_scopes if args.no_scopes else False
    if args.create_disk:
      restore_config['CreateDisks'] = args.create_disk
    if args.description:
      restore_config['Description'] = args.description
    if args.metadata:
      restore_config['Metadata'] = args.metadata
    if args.labels:
      restore_config['Labels'] = args.labels
    if args.tags:
      restore_config['Tags'] = args.tags
    if args.machine_type:
      if not args.machine_type.startswith('projects/'):
        args.machine_type = 'projects/{}/zones/{}/machineTypes/{}'.format(
            args.target_project, args.target_zone, args.machine_type
        )
      restore_config['MachineType'] = args.machine_type
    if args.hostname:
      restore_config['Hostname'] = args.hostname
    if args.enable_uefi_networking is not None:
      restore_config['EnableUefiNetworking'] = args.enable_uefi_networking
    if args.threads_per_core:
      restore_config['ThreadsPerCore'] = args.threads_per_core
    if args.visible_core_count:
      restore_config['VisibleCoreCount'] = args.visible_core_count
    if args.accelerator:
      if not args.accelerator['type'].startswith('projects/'):
        args.accelerator['type'] = (
            'projects/{}/zones/{}/acceleratorTypes/{}'.format(
                args.target_project, args.target_zone, args.accelerator['type']
            )
        )
      restore_config['Accelerator'] = args.accelerator
    if args.min_cpu_platform:
      restore_config['MinCpuPlatform'] = args.min_cpu_platform
    if args.maintenance_policy:
      restore_config['MaintenancePolicy'] = args.maintenance_policy
    if args.preemptible is not None:
      restore_config['Preemptible'] = args.preemptible
    if args.restart_on_failure is not None:
      restore_config['RestartOnFailure'] = args.restart_on_failure
    if args.min_node_cpu:
      restore_config['MinNodeCpus'] = args.min_node_cpu
    if args.provisioning_model:
      restore_config['ProvisioningModel'] = args.provisioning_model
    if args.instance_termination_action:
      restore_config['InstanceTerminationAction'] = (
          args.instance_termination_action
      )
    if args.local_ssd_recovery_timeout:
      restore_config['LocalSsdRecoveryTimeout'] = (
          args.local_ssd_recovery_timeout
      )
    if args.node_affinity_file:
      restore_config['NodeAffinityFile'] = args.node_affinity_file
    if args.reservation_affinity:
      restore_config['ReservationAffinity'] = args.reservation_affinity
    if args.reservation:
      restore_config['Reservation'] = args.reservation
    if args.enable_display_device is not None:
      restore_config['EnableDisplayDevice'] = args.enable_display_device
    if args.can_ip_forward is not None:
      restore_config['CanIpForward'] = args.can_ip_forward
    if args.private_ipv6_google_access_type:
      restore_config['PrivateIpv6GoogleAccessType'] = (
          args.private_ipv6_google_access_type
      )
    if args.network_performance_configs:
      restore_config['NetworkPerformanceConfigs'] = (
          args.network_performance_configs
      )
    if args.confidential_compute:
      restore_config['ConfidentialCompute'] = args.confidential_compute
    if args.deletion_protection is not None:
      restore_config['DeletionProtection'] = args.deletion_protection
    if args.resource_manager_tags:
      restore_config['ResourceManagerTags'] = args.resource_manager_tags
    if args.resource_policies:
      restore_config['ResourcePolicies'] = self._ParseResourcePolicies(
          args.resource_policies, args.target_project, args.target_zone
      )
    if args.key_revocation_action_type:
      restore_config['KeyRevocationActionType'] = (
          args.key_revocation_action_type
      )
    if args.instance_kms_key:
      restore_config['InstanceKmsKey'] = args.instance_kms_key
    try:
      operation = client.RestoreCompute(backup, restore_config)
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
            ' (This operation could take up to 15 minutes.)'.format(
                backup.Name()
            )
        ),
        has_result=False,
    )
