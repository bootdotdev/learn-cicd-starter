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
"""Command for creating snapshot groups."""


from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.operations import poller
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags
from googlecloudsdk.command_lib.compute.snapshot_groups import flags as snap_flags
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources


def _CommonArgs(parser):
  """Add arguments used for parsing in all command tracks."""
  parser.add_argument('name', help='The name of the snapshot group.')
  snap_flags.SOURCE_INSTANT_SNAPSHOT_GROUP_ARG.AddArgument(parser)
  base.ASYNC_FLAG.AddToParser(parser)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class Create(base.Command):
  """Create a Compute Engine snapshot group."""

  @staticmethod
  def Args(parser):
    _CommonArgs(parser)

  def Run(self, args):
    return self._Run(args)

  def _Run(
      self,
      args,
  ):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client.apitools_client
    messages = holder.client.messages
    sg_ref = holder.resources.Parse(
        args.name,
        params={
            'project': properties.VALUES.core.project.GetOrFail,
        },
        collection='compute.snapshotGroups',
    )

    sg_message = messages.SnapshotGroup(
        name=sg_ref.Name()
    )

    isg_ref = snap_flags.SOURCE_INSTANT_SNAPSHOT_GROUP_ARG.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=flags.GetDefaultScopeLister(holder.client),
    )
    sg_message.sourceInstantSnapshotGroup = isg_ref.SelfLink()

    request = messages.ComputeSnapshotGroupsInsertRequest(
        snapshotGroup=sg_message, project=sg_ref.project
    )
    result = client.snapshotGroups.Insert(request)
    operation_ref = resources.REGISTRY.Parse(
        result.name,
        params={'project': sg_ref.project},
        collection='compute.globalOperations',
    )
    if args.async_:
      log.UpdatedResource(
          operation_ref,
          kind='gce snapshot group {0}'.format(sg_ref.Name()),
          is_async=True,
          details=(
              'Use [gcloud compute operations describe] command '
              'to check the status of this operation.'
          ),
      )
      return result
    operation_poller = poller.Poller(client.snapshotGroups, sg_ref)
    return waiter.WaitFor(
        operation_poller,
        operation_ref,
        'Creating gce snapshot group {0}'.format(sg_ref.Name()),
    )
