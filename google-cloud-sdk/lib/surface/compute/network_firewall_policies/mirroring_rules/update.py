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
"""Command for updating network firewall policy packet mirroring rules."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import firewall_policy_rule_utils as rule_utils
from googlecloudsdk.api_lib.compute.network_firewall_policies import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.network_firewall_policies import flags
from googlecloudsdk.command_lib.compute.network_firewall_policies import secure_tags_utils


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Update(base.UpdateCommand):
  r"""Updates a Compute Engine network firewall policy packet mirroring rule.

  *{command}* is used to update network firewall policy packet mirroring rules.
  """

  NETWORK_FIREWALL_POLICY_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.NETWORK_FIREWALL_POLICY_ARG = (
        flags.NetworkFirewallPolicyPacketMirroringRuleArgument(
            required=True, operation='update'
        )
    )
    cls.NETWORK_FIREWALL_POLICY_ARG.AddArgument(parser)
    flags.AddPacketMirroringAction(parser, required=False)
    flags.AddRulePriority(parser, operation='updated')
    flags.AddSrcIpRanges(parser)
    flags.AddDestIpRanges(parser)
    flags.AddLayer4Configs(parser)
    flags.AddDirection(parser)
    flags.AddDisabled(parser)
    flags.AddGlobalFirewallPolicy(parser)
    flags.AddDescription(parser)
    flags.AddNewPriority(parser, operation='update')
    flags.AddMirroringSecurityProfileGroup(parser)
    flags.AddTargetSecureTags(parser)

  def Run(self, args):
    clearable_arg_name_to_field_name = {
        'src_ip_ranges': 'match.srcIpRanges',
        'dest_ip_ranges': 'match.destIpRanges',
        'security_profile_group': 'securityProfileGroup',
        'target_secure_tags': 'targetSecureTags',
    }
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.NETWORK_FIREWALL_POLICY_ARG.ResolveAsResource(
        args, holder.resources
    )
    network_firewall_policy_rule_client = (
        client.NetworkFirewallPolicyPacketMirroringRule(
            ref=ref, compute_client=holder.client
        )
    )

    priority = rule_utils.ConvertPriorityToInt(args.priority)
    src_ip_ranges = []
    dest_ip_ranges = []
    layer4_config_list = []
    security_profile_group = None
    target_secure_tags = []
    disabled = None
    should_setup_match = False
    traffic_direct = None
    cleared_fields = []
    for arg in clearable_arg_name_to_field_name:
      if args.IsKnownAndSpecified(arg) and not args.GetValue(arg):
        cleared_fields.append(clearable_arg_name_to_field_name[arg])
    if args.IsSpecified('src_ip_ranges'):
      src_ip_ranges = args.src_ip_ranges
      should_setup_match = True
    if args.IsSpecified('dest_ip_ranges'):
      dest_ip_ranges = args.dest_ip_ranges
      should_setup_match = True
    if args.IsSpecified('layer4_configs'):
      should_setup_match = True
      layer4_config_list = rule_utils.ParseLayer4Configs(
          args.layer4_configs, holder.client.messages
      )
    if args.IsSpecified('disabled'):
      disabled = args.disabled
    if args.IsSpecified('new_priority'):
      new_priority = rule_utils.ConvertPriorityToInt(args.new_priority)
    else:
      new_priority = priority
    matcher = holder.client.messages.FirewallPolicyRuleMatcher(
        srcIpRanges=src_ip_ranges,
        destIpRanges=dest_ip_ranges,
        layer4Configs=layer4_config_list,
    )
    if args.IsSpecified('security_profile_group'):
      security_profile_group = args.security_profile_group
    elif (
        args.IsSpecified('action')
        and args.action != 'apply_security_profile_group'
    ):
      cleared_fields.append('securityProfileGroup')
    # If not need to construct a new matcher.
    if not should_setup_match:
      matcher = None

    if args.IsSpecified('direction'):
      if args.direction == 'INGRESS':
        traffic_direct = (
            holder.client.messages.FirewallPolicyRule.DirectionValueValuesEnum.INGRESS
        )
      else:
        traffic_direct = (
            holder.client.messages.FirewallPolicyRule.DirectionValueValuesEnum.EGRESS
        )
    if args.IsSpecified('target_secure_tags'):
      target_secure_tags = (
          secure_tags_utils.TranslateSecureTagsForFirewallPolicy(
              holder.client, args.target_secure_tags
          )
      )

    firewall_policy_rule = holder.client.messages.FirewallPolicyRule(
        priority=new_priority,
        action=args.action,
        match=matcher,
        direction=traffic_direct,
        description=args.description,
        disabled=disabled,
        securityProfileGroup=security_profile_group,
        targetSecureTags=target_secure_tags,
    )

    with holder.client.apitools_client.IncludeFields(cleared_fields):
      return network_firewall_policy_rule_client.UpdateRule(
          priority=priority,
          firewall_policy=args.firewall_policy,
          firewall_policy_rule=firewall_policy_rule,
          only_generate_request=False,
      )


Update.detailed_help = {
    'EXAMPLES': """\
    To update a rule with priority ``10'' in a global network firewall policy
    with name ``my-policy'' to change the action to ``mirror'' and description to
    ``new example rule'', run:

      $ {command} 10 --firewall-policy=my-policy --action=mirror --description="new example rule"
    """,
}
