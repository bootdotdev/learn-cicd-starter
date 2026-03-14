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
"""Command for creating network policy rules."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

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
class Create(base.CreateCommand):
  r"""Creates a Compute Engine network policy rule.

  *{command}* is used to create network policy rules.
  """

  NETWORK_POLICY_ARG: ClassVar[compute_flags.ResourceArgument]

  @classmethod
  def Args(cls, parser):
    cls.NETWORK_POLICY_ARG = flags.NetworkPolicyRuleArgument(
        required=True, operation='create'
    )
    cls.NETWORK_POLICY_ARG.AddArgument(parser, operation_type='create')
    flags.AddArgsAddRule(parser)
    parser.display_info.AddCacheUpdater(flags.NetworkPoliciesCompleter)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.NETWORK_POLICY_ARG.ResolveAsResource(args, holder.resources)
    network_policy_rule_client = client.NetworkPolicyRule(
        ref=ref, compute_client=holder.client
    )

    name = None
    description = None
    priority = None
    src_ip_ranges = []
    dest_ip_ranges = []
    layer4_configs = []
    target_service_accounts = []
    disabled = False
    target_secure_tags = []
    dscp_value = None
    dscp_mode = self._GetDscpMode(holder.client.messages, args.dscp_mode)
    traffic_class = self._GetTrafficClass(
        holder.client.messages, args.traffic_class
    )

    if args.IsSpecified('name'):
      name = args.name
    if args.IsSpecified('description'):
      description = args.description
    if args.IsSpecified('priority'):
      priority = args.priority
    if args.IsSpecified('src_ip_ranges'):
      src_ip_ranges = args.src_ip_ranges
    if args.IsSpecified('dest_ip_ranges'):
      dest_ip_ranges = args.dest_ip_ranges
    if args.IsSpecified('layer4_configs'):
      layer4_configs = args.layer4_configs
    if args.IsSpecified('target_service_accounts'):
      target_service_accounts = args.target_service_accounts
    if args.IsSpecified('disabled'):
      disabled = args.disabled
    if args.IsSpecified('dscp_value'):
      dscp_value = args.dscp_value
    if args.IsSpecified('target_secure_tags'):
      target_secure_tags = rules_utils.TranslateSecureTags(
          holder.client, args.target_secure_tags
      )
    layer4_config_list = rules_utils.ParseLayer4Configs(
        layer4_configs, holder.client.messages
    )

    matcher = (
        holder.client.messages.NetworkPolicyTrafficClassificationRuleMatcher(
            srcIpRanges=src_ip_ranges,
            destIpRanges=dest_ip_ranges,
            layer4Configs=layer4_config_list,
        )
    )

    network_policy_rule = holder.client.messages.NetworkPolicyTrafficClassificationRule(
        priority=rules_utils.ConvertPriorityToInt(priority),
        action=holder.client.messages.NetworkPolicyTrafficClassificationRuleAction(
            type=args.action,
            trafficClass=traffic_class,
            dscpMode=dscp_mode,
            dscpValue=dscp_value,
        ),
        match=matcher,
        targetServiceAccounts=target_service_accounts,
        description=description,
        ruleName=name,
        disabled=disabled,
        targetSecureTags=target_secure_tags,
    )

    return network_policy_rule_client.CreateRule(
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


Create.detailed_help = {
    'EXAMPLES': """\
    To create a traffic classification rule with priority ``10'' in a network
    policy with name ``my-policy'' and description ``example rule'', in
    region ``region-a'', run:

        $ {command} \
        --priority=10 \
        --action=apply_traffic_classification \
        --network-policy=my-policy \
        --network-policy-region=region-a \
        --dest-ip-ranges=11.0.0.0/8 \
        --description="example rule" \
        --traffic-class tc1
        --dscp-mode custom
        --dscp-value 3
        --layer4-configs=tcp:80,udp
    """,
}
