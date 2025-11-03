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

"""Updates a Cloud NetApp Volume QuotaRule."""

from googlecloudsdk.api_lib.netapp.volumes.quota_rules import client as quota_rules_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp.volumes.quota_rules import flags as quota_rules_flags
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Update(base.UpdateCommand):
  """Update a Cloud NetApp Volume QuotaRule."""

  _RELEASE_TRACK = base.ReleaseTrack.GA

  detailed_help = {
      'DESCRIPTION': """\
          Update a Cloud NetApp Volume QuotaRule and its specified parameters.
          """,
      'EXAMPLES': """\
          The following command updates a QuotaRule named NAME and its specified parameters:

              $ {command} NAME --location=us-central1 --description="new" --disk-limit-mib=100 --update-labels=key2=val2 --volume=vol1
          """,
  }

  @staticmethod
  def Args(parser):
    quota_rules_flags.AddQuotaRuleUpdateArgs(parser)

  def Run(self, args):
    """Update a Cloud NetApp Volume QuotaRule in the current project."""
    quota_rule_ref = args.CONCEPTS.quota_rule.Parse()

    client = quota_rules_client.QuotaRulesClient(self._RELEASE_TRACK)
    labels_diff = labels_util.Diff.FromUpdateArgs(args)
    original_quota_rule = client.GetQuotaRule(quota_rule_ref)

    # Update labels
    if labels_diff.MayHaveUpdates():
      labels = labels_diff.Apply(
          client.messages.QuotaRule.LabelsValue, original_quota_rule.labels
      ).GetOrNone()
    else:
      labels = None

    quota_rule = client.ParseUpdatedQuotaRuleConfig(
        original_quota_rule,
        disk_limit_mib=args.disk_limit_mib,
        description=args.description,
        labels=labels,
    )

    updated_fields = []
    # add possible updated quota rule fields
    # TODO(b/243601146) add config mapping and separate config file for update
    if args.IsSpecified('description'):
      updated_fields.append('description')
    # Need a check for labels is not None. GetOrNone returns None if there are
    # no updates to labels. If that's the case, make sure not to include the
    # labels field in the field mask of the update command. Otherwise, it's
    # possible to inadvertently clear the labels on the resource.
    if (labels is not None) and (
        args.IsSpecified('update_labels')
        or args.IsSpecified('remove_labels')
        or args.IsSpecified('clear_labels')
    ):
      updated_fields.append('labels')
    if args.IsSpecified('disk_limit_mib'):
      updated_fields.append('diskLimitMib')

    update_mask = ','.join(updated_fields)
    result = client.UpdateQuotaRule(
        quota_rule_ref, quota_rule, update_mask, args.async_
    )
    if args.async_:
      command = 'gcloud {} netapp volumes quota-rules list'.format(
          self.ReleaseTrack().prefix
      )
      log.status.Print(
          'Check the status of the updated quota rule by listing all quota'
          ' rules:\n  $ {} '.format(command)
      )
    return result


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class UpdateBeta(Update):
  """Update a Cloud NetApp Volume Quota Rule."""

  _RELEASE_TRACK = base.ReleaseTrack.BETA
