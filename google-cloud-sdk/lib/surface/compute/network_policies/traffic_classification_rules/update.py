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
"""Command for updating network policy rules."""

from typing import ClassVar

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.network_policies import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.network_policies import flags
from googlecloudsdk.command_lib.compute.network_policies import rules_utils
from googlecloudsdk.command_lib.util.apis import arg_utils


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Update(base.UpdateCommand):
  r"""Updates a Compute Engine network policy rule.

  *{command}* is used to update network policy rules.
  """

  NETWORK_POLICY_ARG: ClassVar[compute_flags.ResourceArgument]

  @classmethod
  def Args(cls, parser):
    cls.NETWORK_POLICY_ARG = flags.NetworkPolicyRuleArgument(
        required=True, operation='update'
    )
    cls.NETWORK_POLICY_ARG.AddArgument(parser)
    flags.AddArgsUpdateRule(parser)

  def Run(self, args):
    clearable_arg_name_to_field_name = {
        'src_ip_ranges': 'match.srcIpRanges',
        'dest_ip_ranges': 'match.destIpRanges',
        'target_secure_tags': 'targetSecureTags',
    }
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.NETWORK_POLICY_ARG.ResolveAsResource(args, holder.resources)
    network_policy_rule_client = client.NetworkPolicyRule(
        ref=ref, compute_client=holder.client
    )

    priority = rules_utils.ConvertPriorityToInt(args.priority)
    src_ip_ranges = []
    dest_ip_ranges = []
    layer4_config_list = []
    target_service_accounts = []
    disabled = None
    should_setup_match = False
    target_secure_tags = []
    cleared_fields = []
    should_setup_action = False
    traffic_class = None
    dscp_mode = None
    dscp_value = None

    for arg in clearable_arg_name_to_field_name:
      if args.IsKnownAndSpecified(arg) and not args.GetValue(arg):
        cleared_fields.append(clearable_arg_name_to_field_name[arg])

    if args.IsSpecified('traffic_class'):
      should_setup_action = True
      traffic_class = self._GetTrafficClass(
          holder.client.messages, args.traffic_class
      )
    if args.IsSpecified('dscp_mode'):
      should_setup_action = True
      dscp_mode = self._GetDscpMode(holder.client.messages, args.dscp_mode)
    if args.IsSpecified('dscp_value'):
      should_setup_action = True
      dscp_value = args.dscp_value
    if args.IsSpecified('src_ip_ranges'):
      src_ip_ranges = args.src_ip_ranges
      should_setup_match = True
    if args.IsSpecified('dest_ip_ranges'):
      dest_ip_ranges = args.dest_ip_ranges
      should_setup_match = True
    if args.IsSpecified('layer4_configs'):
      should_setup_match = True
      layer4_config_list = rules_utils.ParseLayer4Configs(
          args.layer4_configs, holder.client.messages
      )
    if args.IsSpecified('target_service_accounts'):
      target_service_accounts = args.target_service_accounts
    if args.IsSpecified('disabled'):
      disabled = args.disabled
    if args.IsSpecified('new_priority'):
      new_priority = rules_utils.ConvertPriorityToInt(args.new_priority)
    else:
      new_priority = priority
    if args.IsSpecified('target_secure_tags'):
      target_secure_tags = rules_utils.TranslateSecureTags(
          holder.client, args.target_secure_tags
      )

    if should_setup_match:
      matcher = (
          holder.client.messages.NetworkPolicyTrafficClassificationRuleMatcher(
              srcIpRanges=src_ip_ranges,
              destIpRanges=dest_ip_ranges,
              layer4Configs=layer4_config_list,
          )
      )
    else:
      matcher = None

    if should_setup_action:
      action = (
          holder.client.messages.NetworkPolicyTrafficClassificationRuleAction(
              trafficClass=traffic_class,
              dscpMode=dscp_mode,
              dscpValue=dscp_value,
          )
      )
    else:
      action = None

    network_policy_rule = (
        holder.client.messages.NetworkPolicyTrafficClassificationRule(
            priority=new_priority,
            action=action,
            match=matcher,
            targetServiceAccounts=target_service_accounts,
            description=args.description,
            disabled=disabled,
            targetSecureTags=target_secure_tags,
        )
    )

    with holder.client.apitools_client.IncludeFields(cleared_fields):
      return network_policy_rule_client.UpdateRule(
          priority=priority,
          network_policy=args.network_policy,
          network_policy_rule=network_policy_rule,
      )

  def _GetDscpMode(self, messages, dscp_mode: str):
    return arg_utils.ChoiceToEnum(
        dscp_mode,
        messages.NetworkPolicyTrafficClassificationRuleAction.DscpModeValueValuesEnum,
    )

  def _GetTrafficClass(self, messages, traffic_class: str):
    return arg_utils.ChoiceToEnum(
        traffic_class,
        messages.NetworkPolicyTrafficClassificationRuleAction.TrafficClassValueValuesEnum,
    )


Update.detailed_help = {
    'EXAMPLES': """\
    To update a rule with priority ``10'' in a network policy with name
    ``my-policy'' to change the description to ``new example rule'', run:

      $ {command} \
          --priority=10 \
          --network-policy=my-policy \
          --description="new example rule"
    """,
}
