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
"""Describe instant snapshot group command."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.instant_snapshot_groups import flags as isg_flags

DETAILED_HELP = {  # Dict[str, str]
    'brief': 'Describe a Compute Engine instant snapshot group',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a Compute
        Engine instant snapshot group in a project.
        """,
    'EXAMPLES': """\
        To describe the instant snapshot group 'instant-snapshot-group-1' in zone 'us-east1-a', run:

            $ {command} instant-snapshot-group-1 --zone=us-east1-a
        """,
}


def _CommonArgs(parser):
  """A helper function to build args based on different API version."""
  Describe.ISG_ARG = isg_flags.MakeInstantSnapshotGroupArg()
  Describe.ISG_ARG.AddArgument(parser, operation_type='describe')


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class Describe(base.DescribeCommand):
  """Describe a Compute Engine instant snapshot group."""

  @classmethod
  def Args(cls, parser):
    _CommonArgs(parser)

  def _Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    messages = client.messages

    isg_ref = Describe.ISG_ARG.ResolveAsResource(args, holder.resources)

    if isg_ref.Collection() == 'compute.instantSnapshotGroups':
      service = client.apitools_client.instantSnapshotGroups
      request_type = messages.ComputeInstantSnapshotGroupsGetRequest
    else:
      service = client.apitools_client.regionInstantSnapshotGroups
      request_type = messages.ComputeRegionInstantSnapshotGroupsGetRequest

    return client.MakeRequests([(service, 'Get',
                                 request_type(**isg_ref.AsDict()))])

  def Run(self, args):
    return self._Run(args)
