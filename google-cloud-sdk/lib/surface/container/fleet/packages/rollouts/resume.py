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
"""Command to resume a suspended Rollout."""

from googlecloudsdk.api_lib.container.fleet.packages import rollouts as apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet.packages import flags
from googlecloudsdk.command_lib.util.concepts import concept_parsers

_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To resume Rollout `20240318` for `cert-manager-app` in `us-central1`, run:

          $ {command} 20240318 --fleet-package=cert-manager-app --location=us-central1
        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Resume(base.Command):
  """Resume suspended Rollout."""

  detailed_help = _DETAILED_HELP
  _api_version = 'v1'

  @staticmethod
  def Args(parser):
    concept_parsers.ConceptParser.ForResource(
        'rollout',
        flags.GetRolloutResourceSpec(),
        'The rollout to resume.',
        required=True,
        prefixes=False,
    ).AddToParser(parser)
    parser.add_argument(
        '--reason', required=False, help='Reason for resuming rollout.'
    )

  def Run(self, args):
    """Run the resume command."""
    client = apis.RolloutsClient(self._api_version)
    return client.Resume(
        project=flags.GetProject(args),
        location=flags.GetLocation(args),
        fleet_package=args.fleet_package,
        rollout=args.rollout,
        reason=args.reason,
    )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class ResumeBeta(Resume):
  """Resume suspended Rollout."""

  _api_version = 'v1beta'


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class ResumeAlpha(Resume):
  """Resume suspended Rollout."""

  _api_version = 'v1alpha'
