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
"""Describe a Cloud NetApp Volume Quota Rule."""

from googlecloudsdk.api_lib.netapp.volumes.quota_rules import client as quota_rules_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp import flags
from googlecloudsdk.command_lib.netapp.volumes.quota_rules import flags as quota_rules_flags
from googlecloudsdk.command_lib.util.concepts import concept_parsers


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Describe(base.DescribeCommand):
  """Describe a Cloud NetApp Volume Quota Rule."""

  _RELEASE_TRACK = base.ReleaseTrack.GA

  detailed_help = {
      'DESCRIPTION': """\
          Describe a Cloud NetApp Volume Quota Rule.
          """,
      'EXAMPLES': """\
          The following command describes a Quota Rule named NAME in the given location and volume:

              $ {command} NAME --location=us-central1 --volume=vol1
          """,
  }

  @staticmethod
  def Args(parser):
    concept_parsers.ConceptParser(
        [flags.GetQuotaRulePresentationSpec('The Quota Rule to describe.')]
    ).AddToParser(parser)
    quota_rules_flags.AddQuotaRuleVolumeArg(parser, required=True)

  def Run(self, args):
    """Get a Cloud NetApp Volume Quota Rule in the current project."""
    quota_rule_ref = args.CONCEPTS.quota_rule.Parse()

    client = quota_rules_client.QuotaRulesClient(
        release_track=self._RELEASE_TRACK
    )
    return client.GetQuotaRule(quota_rule_ref)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class DescribeBeta(Describe):
  """Describe a Cloud NetApp Volume Quota Rule."""

  _RELEASE_TRACK = base.ReleaseTrack.BETA
