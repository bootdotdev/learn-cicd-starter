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
"""Command to list all Fleet Packages in project."""

from googlecloudsdk.api_lib.container.fleet.packages import fleet_packages as apis
from googlecloudsdk.api_lib.container.fleet.packages import rollouts as rollouts_apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet.packages import flags
from googlecloudsdk.command_lib.container.fleet.packages import utils
from googlecloudsdk.command_lib.util.concepts import concept_parsers

_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To view Fleet Package `cert-manager-app` in `us-central1`, run:

          $ {command} cert-manager-app --location=us-central1
        """,
}

_ROLLOUT_BASENAME_INDEX = 7


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Describe(base.DescribeCommand):
  """Describe Package Rollouts Fleet Package."""

  detailed_help = _DETAILED_HELP
  _api_version = 'v1'

  @staticmethod
  def Args(parser):
    concept_parsers.ConceptParser.ForResource(
        'fleet_package',
        flags.GetFleetPackageResourceSpec(),
        'The Fleet Package to describe.',
        required=True,
        prefixes=False,
    ).AddToParser(parser)
    parser.display_info.AddTransforms(
        {'all_messages': utils.TransformAllClusterLevelMessages}
    )
    parser.add_argument(
        '--show-cluster-status',
        required=False,
        action='store_true',
        help='Show more information about the Fleet Package.',
    )

  def Run(self, args):
    """Run the describe command."""
    client = apis.FleetPackagesClient(self._api_version)
    rollouts_client = rollouts_apis.RolloutsClient(self._api_version)
    result = client.Describe(
        project=flags.GetProject(args),
        location=flags.GetLocation(args),
        name=args.fleet_package,
    )
    if args.show_cluster_status:
      info = result.info
      target_rollout = getattr(info, 'activeRollout', None)
      if target_rollout is None:
        target_rollout = getattr(info, 'lastCompletedRollout', None)
      if target_rollout is not None:
        described_rollout = rollouts_client.Describe(
            project=flags.GetProject(args),
            location=flags.GetLocation(args),
            fleet_package=args.fleet_package,
            rollout=target_rollout.split('/')[_ROLLOUT_BASENAME_INDEX],
        )
        if not args.format:
          utils.FormatForRolloutsDescribe(described_rollout, args)
        return described_rollout

    return result


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class DescribeBeta(Describe):
  """Describe Package Rollouts Fleet Package."""

  _api_version = 'v1beta'


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class DescribeAlpha(Describe):
  """Describe Package Rollouts Fleet Package."""

  _api_version = 'v1alpha'
