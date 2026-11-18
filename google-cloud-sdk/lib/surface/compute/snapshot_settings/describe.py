# -*- coding: utf-8 -*- #
# Copyright 2024 Google Inc. All Rights Reserved.
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

"""Command for describing snapshot settings."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.snapshot_settings import flags
from googlecloudsdk.core import properties


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.UniverseCompatible
class Describe(base.DescribeCommand):
  """Describe snapshot settings."""

  @staticmethod
  def Args(parser):
    parser.display_info.AddFormat(
        'yaml(storageLocation.policy,'
        ' storageLocation.locations.list(show="keys"))'
    )

  def Run(self, args):
    return self._Run(args)

  def _Run(self, args, support_region=False):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    if support_region and args.region:
      service = client.apitools_client.regionSnapshotSettings
      request = client.messages.ComputeRegionSnapshotSettingsGetRequest(
          project=properties.VALUES.core.project.GetOrFail(), region=args.region
      )
    else:
      service = client.apitools_client.snapshotSettings
      request = client.messages.ComputeSnapshotSettingsGetRequest(
          project=properties.VALUES.core.project.GetOrFail()
      )
    return client.MakeRequests([(service, 'Get', request)])[0]


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class DescribeAlphaAndBeta(Describe):
  """Describe snapshot settings."""

  @staticmethod
  def Args(parser):
    flags.AddSnapshotSettingArg(parser)
    parser.display_info.AddFormat(
        'yaml(accessLocation.policy,'
        'accessLocation.locations.list(show="keys"),storageLocation.policy,'
        'storageLocation.locations.list(show="keys"))'
    )

  def Run(self, args):
    return self._Run(
        args,
        support_region=True,
    )


Describe.detailed_help = {
    'brief': 'Describe snapshot settings.',
    'DESCRIPTION': """\
      Describe the snapshot settings of a project.
      """,
    'EXAMPLES': """\
    To display the snapshot settings of a project called my-project, run:

        $ {command} --project=my-project
            """,
    'API REFERENCE': """\
      This command uses the compute/alpha or compute/beta or comptue/v1 API. The full documentation for this API
     can be found at: https://cloud.google.com/compute/""",
}
