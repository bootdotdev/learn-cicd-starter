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
"""Command for deleting snapshot groups."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import utils
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.snapshot_groups import flags

DELETE = 'Delete'

DETAILED_HELP = {
    'EXAMPLES':
        """\
        To delete Compute Engine snapshot groups with the names 'sg-1'
        and 'sg-2', run:

          $ {command} sg-1 sg-2
        """,
}


def _CommonArgs(parser):
  """A helper function to build args for ALPHA API version."""
  Delete.SnapshotGroupArg = flags.MakeSnapshotGroupArg(plural=True)
  Delete.SnapshotGroupArg.AddArgument(parser, operation_type='delete')


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class Delete(base.DeleteCommand):
  """Delete Compute Engine snapshot groups.

  *{command}* deletes one or more Compute Engine snapshot groups.
  """

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    _CommonArgs(parser)

  def Run(self, args):
    return self._Run(args)

  def _Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    snapshot_group_refs = Delete.SnapshotGroupArg.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(client),
        default_scope=compute_scope.ScopeEnum.GLOBAL,
    )

    utils.PromptForDeletion(snapshot_group_refs)
    requests = []
    for snapshot_group_ref in snapshot_group_refs:
      requests.append((
          client.apitools_client.snapshotGroups,
          DELETE,
          client.messages.ComputeSnapshotGroupsDeleteRequest(
              project=snapshot_group_ref.project,
              snapshotGroup=snapshot_group_ref.snapshotGroup,
          ),
      ))

    return client.MakeRequests(requests)
