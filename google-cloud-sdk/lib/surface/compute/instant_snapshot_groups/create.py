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
"""Create instant snapshot group command."""


from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.instant_snapshot_groups import flags as isg_flags

DETAILED_HELP = {  # Dict[str, str]
    'brief': 'Create an instant snapshot group.',
    'DESCRIPTION': """\
    *{command}* creates an instant snapshot group of the consistency group.  An Instant Snapshot Group is a Point In Time view of the constituent disks of a Consistency Group, they are stored in-place as Instant Snapshots on the corresponding disks.
    """,
    'EXAMPLES': """\
    To create an instant snapshot group 'my-instant-snapshot-group' in zone 'us-east1-a' from a consistency group 'my-consistency-group' in region 'us-east1', run:
        $ {command} my-instant-snapshot-group --zone us-east1-a --source-consistency-group=regions/us-east1/resourcePolicies/policy1
    """,
}


def _SourceArgs(parser):
  isg_flags.AddSourceConsistencyGroupArg(parser)


def _CommonArgs(parser):
  """A helper function to build args based on different API version."""
  Create.ISG_ARG = isg_flags.MakeInstantSnapshotGroupArg()
  Create.ISG_ARG.AddArgument(parser, operation_type='create')
  _SourceArgs(parser)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class Create(base.Command):
  """Create a Compute Engine instant snapshot group."""

  @classmethod
  def Args(cls, parser):
    _CommonArgs(parser)

  @classmethod
  def _GetApiHolder(cls, no_http=False):
    return base_classes.ComputeApiHolder(cls.ReleaseTrack())

  def _Run(self, args):
    compute_holder = self._GetApiHolder()
    client = compute_holder.client
    messages = client.messages

    isg_ref = Create.ISG_ARG.ResolveAsResource(args, compute_holder.resources)
    requests = []
    source_cg_url = getattr(args, 'source_consistency_group', None)
    if isg_ref.Collection() == 'compute.instantSnapshotGroups':
      instant_snapshot_group = messages.InstantSnapshotGroup(
          name=isg_ref.Name(), sourceConsistencyGroup=source_cg_url
      )
      request = messages.ComputeInstantSnapshotGroupsInsertRequest(
          instantSnapshotGroup=instant_snapshot_group,
          project=isg_ref.project,
          zone=isg_ref.zone,
      )
      request = (
          client.apitools_client.instantSnapshotGroups,
          'Insert',
          request,
      )
    elif isg_ref.Collection() == 'compute.regionInstantSnapshotGroups':
      instant_snapshot_group = messages.InstantSnapshotGroup(
          name=isg_ref.Name(), sourceConsistencyGroup=source_cg_url,
      )
      request = messages.ComputeRegionInstantSnapshotGroupsInsertRequest(
          instantSnapshotGroup=instant_snapshot_group,
          project=isg_ref.project,
          region=isg_ref.region,
      )
      request = (
          client.apitools_client.regionInstantSnapshotGroups,
          'Insert',
          request,
      )

    requests.append(request)
    return client.MakeRequests(requests)

  def Run(self, args):
    return self._Run(args)
