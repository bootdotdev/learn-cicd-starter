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
"""Command for updating the KMS key of a persistent snapshot."""


from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.snapshots import flags as snapshots_flags

DETAILED_HELP = {
    'brief': 'Update the KMS key of a Compute Engine snapshot.',
    'DESCRIPTION': """
        * {command}* updates the KMS key of a Compute Engine persistent snapshot.
    """,
    'EXAMPLES': """
        To update the KMS key of a snapshot named example-snapshot-1, run:

          $ {command} example-snapshot-1
    """,
}


def _CommonArgs(parser):
  """Add arguments used for parsing in all command tracks."""
  snapshots_flags.MakeSnapshotArg(plural=False).AddArgument(
      parser, operation_type='update the KMS key for'
  )
  parser.add_argument(
      '--region',
      help='The region of the snapshot to update.',
      required=False,
  )


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class UpdateKmsKey(base.Command):
  """Update the KMS key of a persistent snapshot."""

  @classmethod
  def Args(cls, parser):
    _CommonArgs(parser)

  @classmethod
  def _GetApiHolder(cls, no_http=False):
    return base_classes.ComputeApiHolder(cls.ReleaseTrack(), no_http)

  def Run(self, args):
    compute_holder = self._GetApiHolder()
    client = compute_holder.client
    messages = client.messages

    if args.region:
      snapshot_ref = snapshots_flags.MakeSnapshotArgForRegionalSnapshots(
          plural=False
      ).ResolveAsResource(args, compute_holder.resources)
    else:
      snapshot_ref = snapshots_flags.MakeSnapshotArg(
          plural=False
      ).ResolveAsResource(args, compute_holder.resources)

    if snapshot_ref.Collection() == 'compute.snapshots':
      service = client.apitools_client.snapshots
      request = messages.ComputeSnapshotsUpdateKmsKeyRequest(
          project=snapshot_ref.project,
          snapshot=snapshot_ref.Name(),
      )
      return client.MakeRequests([(service, 'UpdateKmsKey', request)])
    elif snapshot_ref.Collection() == 'compute.regionSnapshots':
      service = client.apitools_client.regionSnapshots
      request = messages.ComputeRegionSnapshotsUpdateKmsKeyRequest(
          project=snapshot_ref.project,
          region=snapshot_ref.region,
          snapshot=snapshot_ref.Name(),
      )
      return client.MakeRequests([(service, 'UpdateKmsKey', request)])


UpdateKmsKey.detailed_help = DETAILED_HELP
