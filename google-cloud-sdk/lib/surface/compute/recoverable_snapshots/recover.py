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
"""Command for recovering recoverable snapshots."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.recoverable_snapshots import flags as recoverable_snapshots_flags


def _AlphaArgs(parser):
  Recover.RecoverableSnapshotArg = (
      recoverable_snapshots_flags.MakeRecoverableSnapshotArg(plural=False)
  )
  Recover.RecoverableSnapshotArg.AddArgument(parser, operation_type='recover')
  parser.add_argument(
      '--snapshot-name',
      help=(
          'Name of the snapshot after the recovery. If not provided, the '
          'snapshot will be recovered with the original name.'
      ),
  )


@base.Hidden
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class Recover(base.Command):
  """Recovers a Compute Engine recoverable snapshot."""

  @staticmethod
  def Args(parser):
    _AlphaArgs(parser)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    messages = client.messages

    recoverable_snapshot_ref = (
        Recover.RecoverableSnapshotArg.ResolveAsResource(
            args,
            holder.resources,
            scope_lister=compute_flags.GetDefaultScopeLister(client),
            default_scope=compute_scope.ScopeEnum.GLOBAL,
        )
    )

    request = messages.ComputeRecoverableSnapshotsRecoverRequest(
        project=recoverable_snapshot_ref.project,
        recoverableSnapshot=recoverable_snapshot_ref.Name(),
        snapshotName=args.snapshot_name,
    )

    return client.MakeRequests(
        [(client.apitools_client.recoverableSnapshots, 'Recover', request)],
        no_followup=True,
    )[0]


Recover.detailed_help = {
    'DESCRIPTION': """\
    Recovers the specified global recoverable snapshot.
    If `--snapshot-name` is provided, the snapshot will be recovered with
    that name. Otherwise, it will be recovered with the original name.
    """,
    'EXAMPLES': """\
    To recover a recoverable snapshot named `recoverable-snapshot-1` with
    the original name, run:
      $ {command} recoverable-snapshot-1
    To recover a recoverable snapshot named `recoverable-snapshot-1` with
    a new name `new-snapshot-name`, run:
      $ {command} recoverable-snapshot-1 --snapshot-name=new-snapshot-name
    """,
}
