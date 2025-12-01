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
"""Command for deleting recoverable snapshots."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import utils
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.recoverable_snapshots import flags

DELETE = 'Delete'
DETAILED_HELP = {
    'EXAMPLES':
        """\
        To delete Compute Engine recoverable snapshots with the names 'recoverable-snapshot-1'
        and 'recoverable-snapshot-2', run:
          $ {command} recoverable-snapshot-1 recoverable-snapshot-2
        To list all recoverable snapshots that were created before a specific date, use
        the --filter flag with the `{parent_command} list` command.
          $ {parent_command} list --filter="creationTimestamp<'2017-01-01'"
        For more information on how to use --filter with the list command,
        run $ gcloud topic filters.
        """,
}


def _AlphaArgs(parser):
  """A helper function to build args for Alpha API version."""
  Delete.RecoverableSnapshotArg = flags.MakeRecoverableSnapshotArg(
      plural=True
  )
  Delete.RecoverableSnapshotArg.AddArgument(parser, operation_type='delete')


@base.Hidden
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class Delete(base.DeleteCommand):
  """Delete Compute Engine recoverable snapshots.

  *{command}* deletes one or more Compute Engine recoverable snapshots.
  """
  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    _AlphaArgs(parser)

  def Run(self, args):
    return self._Run(args)

  def _Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    recoverable_snapshot_refs = Delete.RecoverableSnapshotArg.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(client),
        default_scope=compute_scope.ScopeEnum.GLOBAL,
    )
    utils.PromptForDeletion(recoverable_snapshot_refs)
    requests = []
    for recoverable_snapshot_ref in recoverable_snapshot_refs:
      requests.append((
          client.apitools_client.recoverableSnapshots,
          DELETE,
          client.messages.ComputeRecoverableSnapshotsDeleteRequest(
              project=recoverable_snapshot_ref.project,
              recoverableSnapshot=recoverable_snapshot_ref.recoverableSnapshot,
          ),
      ))
    return client.MakeRequests(requests)
