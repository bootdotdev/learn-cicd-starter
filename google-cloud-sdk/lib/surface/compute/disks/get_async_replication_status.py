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
"""Command for retrieving the status of asynchronous replication for a disk-pair."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags
from googlecloudsdk.command_lib.compute.disks import flags as disks_flags

DETAILED_HELP = {
    'brief': (
        'Retrieves the status of asynchronous replication for a Compute'
        ' Engine persistent disk-pair'
    ),
    'DESCRIPTION': """\
        *{command}* fetches the current status of async replication on a Compute
        Engine persistent disk-pair. This command can be invoked on either the
        primary disk or the secondary-disk but the scope respective to the disk
        must be provided.
        """,
    'EXAMPLES': """\
        Replication status can be fetched by using either the primary or the
        secondary disk. To get the current replication status of the disk-pair
        with the primary disk 'primary-disk-1' in zone 'us-east1-a', and project
        'my-project1' and the secondary disk 'secondary-disk-1' in zone
        'us-west1-a', and the project 'my-project2', the following commands can
        be used:

          $ {command} primary-disk-1 --zone=us-east1-a --project=my-project1
          or
          $ {command} secondary-disk-1 --zone=us-west1-a --project=my-project2
        """,
}


def _CommonArgs(parser):
  """Add arguments used for parsing in all command tracks."""
  GetAsyncReplicationStatus.disks_arg.AddArgument(parser)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class GetAsyncReplicationStatus(base.Command):
  """Get Async Replication Status for Compute Engine persistent disk-pairs in an asynchronous replication ."""

  @classmethod
  def Args(cls, parser):
    GetAsyncReplicationStatus.disks_arg = disks_flags.MakeDiskArg(plural=False)
    _CommonArgs(parser)

  @classmethod
  def _GetApiHolder(cls, no_http=False):
    return base_classes.ComputeApiHolder(cls.ReleaseTrack(), no_http)

  def Run(self, args):
    return self._Run(args)

  def _Run(self, args):
    compute_holder = self._GetApiHolder()
    client = compute_holder.client

    disk_ref = GetAsyncReplicationStatus.disks_arg.ResolveAsResource(
        args,
        compute_holder.resources,
        scope_lister=flags.GetDefaultScopeLister(client),
    )

    request = None
    if disk_ref.Collection() == 'compute.disks':
      request = client.messages.ComputeDisksGetAsyncReplicationStatusRequest(
          disk=disk_ref.Name(),
          project=disk_ref.project,
          zone=disk_ref.zone,
      )
      request = (
          client.apitools_client.disks,
          'GetAsyncReplicationStatus',
          request,
      )
    elif disk_ref.Collection() == 'compute.regionDisks':
      request = (
          client.messages.ComputeRegionDisksGetAsyncReplicationStatusRequest(
              disk=disk_ref.Name(),
              project=disk_ref.project,
              region=disk_ref.region,
          )
      )
      request = (
          client.apitools_client.regionDisks,
          'GetAsyncReplicationStatus',
          request,
      )
    return client.MakeRequests([request])


GetAsyncReplicationStatus.detailed_help = DETAILED_HELP
