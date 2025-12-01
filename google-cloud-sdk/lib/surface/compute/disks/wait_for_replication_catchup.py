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
"""Command for waiting for the asynchronous replication of a disk-pair to catch up."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags
from googlecloudsdk.command_lib.compute.disks import flags as disks_flags

DETAILED_HELP = {
    'brief': (
        'Provides the operation id for the asynchronous replication of a'
        ' Compute Engine persistent disk-pair that can be used to wait for the'
        ' replication to catch up.'
    ),
    'DESCRIPTION': """\
        *{command}* fetches the operation id that can be used to track the
        status of async replication for a Compute Engine persistent disk-pair.
        The operation id can be used to wait for the replication to catch up.
        This command can be invoked only on the primary disk.
        """,
    'EXAMPLES': """\
        Note: The max-wait-duration is optional. If not specified, the default
        value would be picked up from the API.
        Wait for replication catchup can only be invoked on the primary scope.
        To wait for the replication catchup for the primary disk 'my-disk-1' in
        zone 'us-east1-a' under project 'my-project1' to catch up with the
        secondary disk 'my-disk-2' in zone 'us-west1-a' in any project, the
        following command can be used (with custom wait duration of 20s):

          $ {command} my-disk-1 --zone=us-east1-a --project=my-project1 --max-wait-duration=20s
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class WaitForReplicationCatchUp(base.Command):
  """Wait for the Asynchronous Replication of Compute Engine persistent disk-pair to complete."""

  disks_arg = disks_flags.MakeDiskArg(plural=False)
  detailed_help = DETAILED_HELP

  @classmethod
  def Args(cls, parser) -> None:
    """Set the arguments for this command.

    Args:
      parser: An argument parser object that is used to add arguments that can
        be specified on the command line.

    Returns:
      None
    """
    WaitForReplicationCatchUp.disks_arg.AddArgument(parser)
    parser.add_argument(
        '--max-wait-duration',
        help='Maximum duration to wait for the replication catchup.',
    )

  @classmethod
  def _GetApiHolder(
      cls, no_http: bool = False
  ) -> base_classes.ComputeApiHolder:
    """Get the compute client API holder instance.

    Args:
      no_http: Whether to disable http.

    Returns:
      A ComputeApiHolder object.
    """
    return base_classes.ComputeApiHolder(cls.ReleaseTrack(), no_http)

  def Run(self, args) -> None:
    """Method that runs the command.

    Validates the arguments passed to the command and triggers the API call.

    Args:
      args: The arguments that were provided to this command invocation.

    Returns:
      None
    """
    compute_holder = self._GetApiHolder()
    client = compute_holder.client

    disk_ref = WaitForReplicationCatchUp.disks_arg.ResolveAsResource(
        args,
        compute_holder.resources,
        scope_lister=flags.GetDefaultScopeLister(client),
    )

    if disk_ref.Collection() == 'compute.disks':
      wait_for_replication_catchup_request = None
      if args.IsSpecified('max_wait_duration'):
        wait_for_replication_catchup_request = (
            client.messages.WaitForReplicationCatchUpRequest(
                maxWaitDuration=args.max_wait_duration
            )
        )
      request = client.messages.ComputeDisksWaitForReplicationCatchUpRequest(
          disk=disk_ref.Name(),
          project=disk_ref.project,
          zone=disk_ref.zone,
          waitForReplicationCatchUpRequest=wait_for_replication_catchup_request,
      )
      request = (
          client.apitools_client.disks,
          'WaitForReplicationCatchUp',
          request,
      )
    else:
      region_wait_for_replication_catchup_request = None
      if args.IsSpecified('max_wait_duration'):
        region_wait_for_replication_catchup_request = (
            client.messages.RegionWaitForReplicationCatchUpRequest(
                maxWaitDuration=args.max_wait_duration
            )
        )
      request = client.messages.ComputeRegionDisksWaitForReplicationCatchUpRequest(
          disk=disk_ref.Name(),
          project=disk_ref.project,
          region=disk_ref.region,
          regionWaitForReplicationCatchUpRequest=region_wait_for_replication_catchup_request,
      )
      request = (
          client.apitools_client.regionDisks,
          'WaitForReplicationCatchUp',
          request,
      )
    return client.MakeRequests([request])
