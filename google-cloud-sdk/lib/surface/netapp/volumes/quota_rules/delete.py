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
"""Delete a Cloud NetApp Volume Quota Rule."""

from googlecloudsdk.api_lib.netapp.volumes.quota_rules import client as quota_rules_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp import flags
from googlecloudsdk.command_lib.netapp.volumes.quota_rules import flags as quota_rules_flags
from googlecloudsdk.command_lib.util.concepts import concept_parsers

from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Delete(base.DeleteCommand):
  """Delete a Cloud NetApp Volume QuotaRule."""

  _RELEASE_TRACK = base.ReleaseTrack.GA

  detailed_help = {
      'DESCRIPTION': """\
          Delete a Cloud NetApp Volume QuotaRule.
          """,
      'EXAMPLES': """\
          The following command deletes a QuotaRule named NAME using the required arguments:

              $ {command} NAME --location=us-central1 --volume=vol1

          To delete a QuotaRule named NAME asynchronously, run the following command:

              $ {command} NAME --location=us-central1 --volume=vol1 --async
          """,
  }

  @staticmethod
  def Args(parser):
    """Add args for deleting a Quota Rule."""
    concept_parsers.ConceptParser([
        flags.GetQuotaRulePresentationSpec('The Quota Rule to delete.')
    ]).AddToParser(parser)
    quota_rules_flags.AddQuotaRuleVolumeArg(parser)
    flags.AddResourceAsyncFlag(parser)

  def Run(self, args):
    """Delete a Cloud NetApp Volume QuotaRule in the current project."""
    quota_rule_ref = args.CONCEPTS.quota_rule.Parse()

    if not args.quiet:
      delete_warning = (
          'You are about to delete a QuotaRule {}.\nAre you sure?'.format(
              quota_rule_ref.RelativeName()
          )
      )
      if not console_io.PromptContinue(message=delete_warning):
        return None

    client = quota_rules_client.QuotaRulesClient(self._RELEASE_TRACK)
    result = client.DeleteQuotaRule(quota_rule_ref, args.async_)
    if args.async_:
      command = 'gcloud {} netapp volumes quota-rules list'.format(
          self.ReleaseTrack().prefix
      )
      log.status.Print(
          'Check the status of the deletion by listing all quota rules:\n  '
          '$ {} '.format(command)
      )
    return result


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class DeleteBeta(Delete):
  """Delete a Cloud NetApp Volume Quota Rule."""

  _RELEASE_TRACK = base.ReleaseTrack.BETA
