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

"""Command for describing disk settings."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.disk_settings import flags
from googlecloudsdk.core import properties


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
@base.UniverseCompatible
class Describe(base.DescribeCommand):
  """Describe a Google Compute Engine disk setting."""

  @staticmethod
  def Args(parser):
    flags.AddDiskSettingArg(parser)
    flags.detailed_help = detailed_help
    parser.display_info.AddFormat(
        'yaml(accessLocation.policy,'
        'accessLocation.locations.list(show="keys"),defaultResourcePolicies)'
    )

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    if args.zone:
      service = client.apitools_client.diskSettings
      request = client.messages.ComputeDiskSettingsGetRequest(
          project=properties.VALUES.core.project.GetOrFail(), zone=args.zone
      )
    else:
      service = client.apitools_client.regionDiskSettings
      request = client.messages.ComputeRegionDiskSettingsGetRequest(
          project=properties.VALUES.core.project.GetOrFail(), region=args.region
      )
    return client.MakeRequests([(service, 'Get', request)])[0]


detailed_help = {
    'brief': 'Describe a Google Compute Engine disk setting',
    'DESCRIPTION': """\
      *{command}* display the Google Compute Engine disk setting in current scope of current project.
      """,
}
