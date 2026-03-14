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
"""Command for updating the KMS key of a persistent disk."""


from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.disks import flags as disks_flags

DETAILED_HELP = {
    'brief': 'Rotate the KMS key of a persistent disk to the primary version.',
    'DESCRIPTION': """
        * {command} * updates the KMS key of a Compute Engine persistent disk
        by rotating it to the primary version of the key.
    """,
    'EXAMPLES': """
        To rotate the KMS key of a disk named example-disk-1 to the primary version, run:

          $ {command} example-disk-1 --zone us-central1-a
    """,
}


def _CommonArgs(parser):
  """Add arguments used for parsing in all command tracks."""
  disks_flags.MakeDiskArg(plural=False).AddArgument(parser)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class UpdateKmsKey(base.Command):
  """Rotate the KMS key of a persistent disk to the primary version."""

  @classmethod
  def Args(cls, parser):
    _CommonArgs(parser)

  @classmethod
  def _GetApiHolder(cls, no_http=False):
    return base_classes.ComputeApiHolder(cls.ReleaseTrack(), no_http)

  def Run(self, args):
    return self._Run(args)

  def _Run(self, args):
    """Issues request for updating the KMS key of a disk."""
    compute_holder = self._GetApiHolder()
    client = compute_holder.client
    messages = client.messages
    resources = compute_holder.resources

    disk_ref = disks_flags.MakeDiskArg(plural=False).ResolveAsResource(
        args, resources
    )

    if disk_ref.Collection() == 'compute.disks':
      service = client.apitools_client.disks
      request = messages.ComputeDisksUpdateKmsKeyRequest(
          project=disk_ref.project,
          zone=disk_ref.zone,
          disk=disk_ref.Name(),
      )
      return client.MakeRequests([(service, 'UpdateKmsKey', request)])
    elif disk_ref.Collection() == 'compute.regionDisks':
      service = client.apitools_client.regionDisks
      request = messages.ComputeRegionDisksUpdateKmsKeyRequest(
          project=disk_ref.project,
          region=disk_ref.region,
          disk=disk_ref.Name(),
      )
      return client.MakeRequests([(service, 'UpdateKmsKey', request)])


UpdateKmsKey.detailed_help = DETAILED_HELP
