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
"""Command for describing snapshots groups."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.snapshot_groups import flags as sg_flags


def _CommonArgs(parser):
  """Set Args based on Release Track."""
  Describe.SnapshotGroupArg = sg_flags.MakeSnapshotGroupArg()
  Describe.SnapshotGroupArg.AddArgument(parser, operation_type='describe')


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class Describe(base.DescribeCommand):
  """Describe a Compute Engine snapshot group."""

  @staticmethod
  def Args(parser):
    _CommonArgs(parser)

  def Run(self, args):
    return self._Run(args)

  def _Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    sg_ref = Describe.SnapshotGroupArg.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(client)
    )

    request = client.messages.ComputeSnapshotGroupsGetRequest(
        **sg_ref.AsDict())

    return client.MakeRequests([(client.apitools_client.snapshotGroups, 'Get',
                                 request)])[0]
