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

"""Create a Cloud NetApp Volume Quota Rule."""

from googlecloudsdk.api_lib.netapp.volumes.quota_rules import client as quota_rules_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp.volumes.quota_rules import flags as quota_rules_flags
from googlecloudsdk.command_lib.util.args import labels_util

from googlecloudsdk.core import log


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Create(base.CreateCommand):
  """Create a Cloud NetApp Volume Quota Rule."""

  _RELEASE_TRACK = base.ReleaseTrack.GA

  detailed_help = {
      'DESCRIPTION': """\
          Create a Cloud NetApp Volume Quota Rule.
          """,
      'EXAMPLES': """\
          The following command creates a default `user` Quota Rule named NAME using the required arguments:

              $ {command} NAME --location=us-central1 --volume=vol1 --type=DEFAULT_USER_QUOTA --disk-limit-mib=200


          The following command creates a default `group` Quota Rule named NAME using the required arguments:

              $ {command} NAME --location=us-central1 --volume=vol1 --type=DEFAULT_GROUP_QUOTA --disk-limit-mib=200


          The following command creates an individual user Quota Rule named NAME for user with UID '100' using the required arguments:

              $ {command} NAME --location=us-central1 --volume=vol1 --type=INDIVIDUAL_USER_QUOTA --target=100 --disk-limit-mib=200


          The following command creates an individual group Quota Rule named NAME for group with GID '1001' using the required arguments:

              $ {command} NAME --location=us-central1 --volume=vol1 --type=INDIVIDUAL_GROUP_QUOTA --target=1001 --disk-limit-mib=200

          """,
  }

  @staticmethod
  def Args(parser):
    quota_rules_flags.AddQuotaRuleCreateArgs(parser)

  def Run(self, args):
    """Create a Cloud NetApp Volume Quota Rule in the current project."""
    quota_rule_ref = args.CONCEPTS.quota_rule.Parse()

    volume_ref = args.CONCEPTS.volume.Parse().RelativeName()
    client = quota_rules_client.QuotaRulesClient(self._RELEASE_TRACK)

    quota_rule_type = quota_rules_flags.GetQuotaRuleTypeEnumFromArg(
        args.type, client.messages
    )
    labels = labels_util.ParseCreateArgs(
        args, client.messages.QuotaRule.LabelsValue
    )

    quota_rule = client.ParseQuotaRuleConfig(
        name=quota_rule_ref.RelativeName(),
        quota_rule_type=quota_rule_type,
        target=args.target,
        disk_limit_mib=args.disk_limit_mib,
        description=args.description,
        labels=labels,
    )

    result = client.CreateQuotaRule(
        quota_rule_ref, volume_ref, args.async_, quota_rule
    )
    if args.async_:
      command = 'gcloud {} netapp volumes quota-rules list'.format(
          self.ReleaseTrack().prefix
      )
      log.status.Print(
          'Check the status of the new quota rule by listing all quota rules:\n'
          '$ {} '.format(command)
      )
    return result


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class CreateBeta(Create):
  """Create a Cloud NetApp Volume Quota Rule."""

  _RELEASE_TRACK = base.ReleaseTrack.BETA
