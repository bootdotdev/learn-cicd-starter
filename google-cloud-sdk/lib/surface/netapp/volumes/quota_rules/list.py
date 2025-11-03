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

"""List Cloud NetApp Volume Quota Rules."""

from googlecloudsdk.api_lib.netapp.volumes.quota_rules import client as quota_rules_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp import flags
from googlecloudsdk.command_lib.netapp.volumes.quota_rules import flags as quota_rules_flags
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.core import properties


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class List(base.ListCommand):
  """List Cloud NetApp Volume QuotaRules."""

  _RELEASE_TRACK = base.ReleaseTrack.GA

  detailed_help = {
      'DESCRIPTION': """\
          Lists Cloud NetApp Volume QuotaRules.
          """,
      'EXAMPLES': """\
          The following command lists all QuotaRules in the given location and volume:

              $ {command} --location=us-central1 --volume=vol1
          """,
  }

  @staticmethod
  def Args(parser):
    concept_parsers.ConceptParser([
        flags.GetResourceListingLocationPresentationSpec(
            'The location in which to list Volume QuotaRules.')
    ]).AddToParser(parser)
    quota_rules_flags.AddQuotaRuleVolumeArg(parser, required=True)

  def Run(self, args):
    """Run the list command."""
    # Ensure that project is set before parsing location resource.
    properties.VALUES.core.project.GetOrFail()

    volume_ref = args.CONCEPTS.volume.Parse().RelativeName()
    client = quota_rules_client.QuotaRulesClient(
        release_track=self._RELEASE_TRACK
    )
    return list(client.ListQuotaRules(volume_ref, limit=args.limit))


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class ListBeta(List):
  """List Cloud NetApp Volume QuotaRules."""

  _RELEASE_TRACK = base.ReleaseTrack.BETA
