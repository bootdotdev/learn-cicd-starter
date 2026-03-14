# -*- coding: utf-8 -*- #
# Copyright 2024 Google LLC. All Rights Reserved.
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
"""Command to describe Rollout in a project."""

from googlecloudsdk.api_lib.container.fleet.packages import rollouts as apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet.packages import flags
from googlecloudsdk.command_lib.container.fleet.packages import utils
from googlecloudsdk.core import log

_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To view Rollout `20240318` for `cert-manager-app` in `us-central1`, run:

          $ {command} 20240318 --fleet-package=cert-manager-app --location=us-central1
        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Describe(base.DescribeCommand):
  """Describe Rollout resource."""

  detailed_help = _DETAILED_HELP
  show_less = False
  _api_version = 'v1'

  def Epilog(self, resources_were_displayed):
    if resources_were_displayed and self.show_less:
      log.status.Print('\nRollout messages too long? Try --less.')

  @staticmethod
  def Args(parser):
    parser.display_info.AddTransforms(
        {'all_messages': utils.TransformAllClusterLevelMessages}
    )
    parser.display_info.AddTransforms(
        {'trim_message': utils.TransformTrimClusterLevelMessages}
    )
    flags.AddNameFlag(parser)
    flags.AddFleetPackageFlag(parser)
    flags.AddLocationFlag(parser)
    flags.AddLessFlag(parser)

  def Run(self, args):
    """Run the describe command."""
    client = apis.RolloutsClient(self._api_version)

    output = client.Describe(
        fleet_package=args.fleet_package,
        project=flags.GetProject(args),
        location=flags.GetLocation(args),
        rollout=args.name,
    )
    if not args.format:
      utils.FormatForRolloutsDescribe(output, args, args.less)
      if output.info and output.info.message:
        if not args.less:
          self.show_less = True
    return output


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class DescribeBeta(Describe):
  """Describe Rollout resource."""

  _api_version = 'v1beta'


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class DescribeAlpha(Describe):
  """Describe Rollout resource."""

  _api_version = 'v1alpha'
