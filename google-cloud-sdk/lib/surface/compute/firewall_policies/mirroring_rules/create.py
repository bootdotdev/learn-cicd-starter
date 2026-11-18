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
"""Command for creating organization firewall policy rules."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import firewall_policy_rule_utils as rule_utils
from googlecloudsdk.api_lib.compute.firewall_policies import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.firewall_policies import firewall_policies_utils
from googlecloudsdk.command_lib.compute.firewall_policies import flags
import six


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class Create(base.CreateCommand):
  r"""Creates a Compute Engine firewall policy packet mirroring rule.

  *{command}* is used to create organization firewall policy packet mirroring
  rules.
  """

  FIREWALL_POLICY_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.FIREWALL_POLICY_ARG = flags.FirewallPolicyRuleArgument(
        required=True, operation='create'
    )
    cls.FIREWALL_POLICY_ARG.AddArgument(parser, operation_type='create')
    flags.AddPacketMirroringAction(parser)
    flags.AddFirewallPolicyId(parser, operation='inserted')
    flags.AddSrcIpRanges(parser)
    flags.AddDestIpRanges(parser)
    flags.AddLayer4Configs(parser, required=True)
    flags.AddDirection(parser)
    flags.AddDisabled(parser)
    flags.AddTargetResources(parser)
    flags.AddMirroringSecurityProfileGroup(parser)
    flags.AddDescription(parser)
    flags.AddOrganization(parser, required=False)
    parser.display_info.AddCacheUpdater(flags.FirewallPoliciesCompleter)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.FIREWALL_POLICY_ARG.ResolveAsResource(
        args, holder.resources, with_project=False
    )
    org_firewall_policy = client.OrgFirewallPolicy(
        ref=ref,
        compute_client=holder.client,
        resources=holder.resources,
        version=six.text_type(self.ReleaseTrack()).lower(),
    )
    firewall_policy_rule_client = client.OrgFirewallPolicyPacketMirroringRule(
        ref=ref,
        compute_client=holder.client,
        resources=holder.resources,
        version=six.text_type(self.ReleaseTrack()).lower(),
    )
    src_ip_ranges = []
    dest_ip_ranges = []
    layer4_configs = []
    target_resources = []
    security_profile_group = None
    disabled = False
    if args.IsSpecified('src_ip_ranges'):
      src_ip_ranges = args.src_ip_ranges
    if args.IsSpecified('dest_ip_ranges'):
      dest_ip_ranges = args.dest_ip_ranges
    if args.IsSpecified('layer4_configs'):
      layer4_configs = args.layer4_configs
    if args.IsSpecified('target_resources'):
      target_resources = args.target_resources
    if args.IsSpecified('security_profile_group'):
      security_profile_group = (
          firewall_policies_utils.BuildSecurityProfileGroupUrl(
              security_profile_group=args.security_profile_group,
              optional_organization=args.organization,
              firewall_policy_client=org_firewall_policy,
              firewall_policy_id=args.firewall_policy,
          )
      )

    if args.IsSpecified('disabled'):
      disabled = args.disabled

    layer4_config_list = rule_utils.ParseLayer4Configs(
        layer4_configs, holder.client.messages
    )

    matcher = holder.client.messages.FirewallPolicyRuleMatcher(
        srcIpRanges=src_ip_ranges,
        destIpRanges=dest_ip_ranges,
        layer4Configs=layer4_config_list,
    )

    traffic_direct = (
        holder.client.messages.FirewallPolicyRule.DirectionValueValuesEnum.INGRESS
    )
    if args.IsSpecified('direction'):
      if args.direction == 'INGRESS':
        traffic_direct = (
            holder.client.messages.FirewallPolicyRule.DirectionValueValuesEnum.INGRESS
        )
      else:
        traffic_direct = (
            holder.client.messages.FirewallPolicyRule.DirectionValueValuesEnum.EGRESS
        )

    firewall_policy_rule = holder.client.messages.FirewallPolicyRule(
        priority=rule_utils.ConvertPriorityToInt(ref.Name()),
        action=args.action,
        match=matcher,
        direction=traffic_direct,
        targetResources=target_resources,
        securityProfileGroup=security_profile_group,
        description=args.description,
        disabled=disabled,
    )

    firewall_policy_id = firewall_policies_utils.GetFirewallPolicyId(
        firewall_policy_rule_client,
        args.firewall_policy,
        organization=args.organization,
    )
    return firewall_policy_rule_client.CreateRule(
        firewall_policy=firewall_policy_id,
        firewall_policy_rule=firewall_policy_rule,
    )


Create.detailed_help = {
    'EXAMPLES': """\
    To create a packet mirroring rule with priority ``10" in an organization firewall policy with ID
    ``123456789", run:

      $ {command} 10 --firewall-policy=123456789 --action=mirror --security-profile-group=organizations/123/locations/global/securityProfileGroups/custom-security-profile-group
      --description=example-rule
    """,
}
