# -*- coding: utf-8 -*- #
# Copyright 2021 Google LLC. All Rights Reserved.
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
"""Command for creating network firewall policy rules."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import firewall_policy_rule_utils as rule_utils
from googlecloudsdk.api_lib.compute.network_firewall_policies import client
from googlecloudsdk.api_lib.compute.network_firewall_policies import region_client
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.compute.network_firewall_policies import flags
from googlecloudsdk.command_lib.compute.network_firewall_policies import secure_tags_utils


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Create(base.CreateCommand):
  r"""Creates a Compute Engine network firewall policy rule.

  *{command}* is used to create network firewall policy rules.
  """

  NETWORK_FIREWALL_POLICY_ARG = None
  support_network_scopes = False
  support_target_type = False

  @classmethod
  def Args(cls, parser):
    cls.NETWORK_FIREWALL_POLICY_ARG = flags.NetworkFirewallPolicyRuleArgument(
        required=True, operation='create'
    )
    cls.NETWORK_FIREWALL_POLICY_ARG.AddArgument(parser, operation_type='create')
    flags.AddAction(parser)
    flags.AddRulePriority(parser, operation='inserted')
    flags.AddSrcIpRanges(parser)
    flags.AddDestIpRanges(parser)
    flags.AddLayer4Configs(parser, required=True)
    flags.AddDirection(parser)
    flags.AddEnableLogging(parser)
    flags.AddDisabled(parser)
    flags.AddTargetServiceAccounts(parser)
    flags.AddDescription(parser)
    flags.AddSrcSecureTags(
        parser,
        required=False,
        support_network_scopes=cls.support_network_scopes,
    )
    flags.AddTargetSecureTags(parser)
    flags.AddSrcAddressGroups(parser)
    flags.AddDestAddressGroups(parser)
    flags.AddSrcFqdns(parser)
    flags.AddDestFqdns(parser)
    flags.AddSrcRegionCodes(
        parser, support_network_scopes=cls.support_network_scopes
    )
    flags.AddDestRegionCodes(
        parser, support_network_scopes=cls.support_network_scopes
    )
    flags.AddSrcThreatIntelligence(
        parser, support_network_scopes=cls.support_network_scopes
    )
    flags.AddDestThreatIntelligence(
        parser, support_network_scopes=cls.support_network_scopes
    )
    flags.AddSecurityProfileGroup(parser)
    flags.AddTlsInspect(parser)
    if cls.support_network_scopes:
      flags.AddSrcNetworkScope(parser)
      flags.AddSrcNetworks(parser)
      flags.AddDestNetworkScope(parser)
      flags.AddSrcNetworkType(parser)
      flags.AddDestNetworkType(parser)
    if cls.support_target_type:
      flags.AddTargetType(parser)
      flags.AddTargetForwardingRules(parser)

    parser.display_info.AddCacheUpdater(flags.NetworkFirewallPoliciesCompleter)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.NETWORK_FIREWALL_POLICY_ARG.ResolveAsResource(
        args, holder.resources
    )
    network_firewall_policy_rule_client = client.NetworkFirewallPolicyRule(
        ref=ref, compute_client=holder.client
    )
    if hasattr(ref, 'region'):
      network_firewall_policy_rule_client = (
          region_client.RegionNetworkFirewallPolicyRule(
              ref, compute_client=holder.client
          )
      )

    src_ip_ranges = []
    dest_ip_ranges = []
    layer4_configs = []
    target_service_accounts = []
    security_profile_group = None
    tls_inspect = None
    enable_logging = False
    disabled = False
    src_secure_tags = []
    target_secure_tags = []
    src_network_scope = None
    src_networks = []
    dest_network_scope = None
    target_type = None
    target_forwarding_rules = []

    if args.IsSpecified('src_ip_ranges'):
      src_ip_ranges = args.src_ip_ranges
    if args.IsSpecified('dest_ip_ranges'):
      dest_ip_ranges = args.dest_ip_ranges
    if args.IsSpecified('layer4_configs'):
      layer4_configs = args.layer4_configs
    if args.IsSpecified('target_service_accounts'):
      target_service_accounts = args.target_service_accounts
    if args.IsSpecified('enable_logging'):
      enable_logging = args.enable_logging
    if args.IsSpecified('disabled'):
      disabled = args.disabled
    if args.IsSpecified('src_secure_tags'):
      src_secure_tags = secure_tags_utils.TranslateSecureTagsForFirewallPolicy(
          holder.client, args.src_secure_tags
      )
    if args.IsSpecified('target_secure_tags'):
      target_secure_tags = (
          secure_tags_utils.TranslateSecureTagsForFirewallPolicy(
              holder.client, args.target_secure_tags
          )
      )
    if args.IsSpecified('security_profile_group'):
      security_profile_group = args.security_profile_group
    if args.IsSpecified('tls_inspect'):
      tls_inspect = args.tls_inspect

    if self.support_network_scopes:
      if args.IsSpecified('src_network_scope') and args.IsSpecified(
          'src_network_type'
      ):
        raise exceptions.ToolException(
            'At most one of src_network_scope and src_network_type can be'
            ' specified.'
        )
      if args.IsSpecified('dest_network_scope') and args.IsSpecified(
          'dest_network_type'
      ):
        raise exceptions.ToolException(
            'At most one of dest_network_scope and dest_network_type can be'
            ' specified.'
        )
      if args.IsSpecified('src_network_scope'):
        if not args.src_network_scope:
          src_network_scope = (
              holder.client.messages.FirewallPolicyRuleMatcher.SrcNetworkScopeValueValuesEnum.UNSPECIFIED
          )
        else:
          src_network_scope = holder.client.messages.FirewallPolicyRuleMatcher.SrcNetworkScopeValueValuesEnum(
              args.src_network_scope
          )
      if args.IsSpecified('src_networks'):
        src_networks = args.src_networks
      if args.IsSpecified('dest_network_scope'):
        if not args.dest_network_scope:
          dest_network_scope = (
              holder.client.messages.FirewallPolicyRuleMatcher.DestNetworkScopeValueValuesEnum.UNSPECIFIED
          )
        else:
          dest_network_scope = holder.client.messages.FirewallPolicyRuleMatcher.DestNetworkScopeValueValuesEnum(
              args.dest_network_scope
          )
      if args.IsSpecified('src_network_type'):
        # src_network_type and src_network_scope are mutually exclusive so only
        # one of them can be specified.
        if not args.src_network_type:
          src_network_scope = (
              holder.client.messages.FirewallPolicyRuleMatcher.SrcNetworkScopeValueValuesEnum.UNSPECIFIED
          )
        else:
          src_network_scope = holder.client.messages.FirewallPolicyRuleMatcher.SrcNetworkScopeValueValuesEnum(
              args.src_network_type
          )
      if args.IsSpecified('dest_network_type'):
        # dest_network_type and dest_network_scope are mutually exclusive so
        # only one of them can be specified.
        if not args.dest_network_type:
          dest_network_scope = (
              holder.client.messages.FirewallPolicyRuleMatcher.DestNetworkScopeValueValuesEnum.UNSPECIFIED
          )
        else:
          dest_network_scope = holder.client.messages.FirewallPolicyRuleMatcher.DestNetworkScopeValueValuesEnum(
              args.dest_network_type
          )

    layer4_config_list = rule_utils.ParseLayer4Configs(
        layer4_configs, holder.client.messages
    )
    if self.support_network_scopes:
      matcher = holder.client.messages.FirewallPolicyRuleMatcher(
          srcIpRanges=src_ip_ranges,
          destIpRanges=dest_ip_ranges,
          layer4Configs=layer4_config_list,
          srcSecureTags=src_secure_tags,
          srcNetworkScope=src_network_scope,
          srcNetworks=src_networks,
          destNetworkScope=dest_network_scope,
      )
    else:
      matcher = holder.client.messages.FirewallPolicyRuleMatcher(
          srcIpRanges=src_ip_ranges,
          destIpRanges=dest_ip_ranges,
          layer4Configs=layer4_config_list,
          srcSecureTags=src_secure_tags,
      )

    if args.IsSpecified('src_address_groups'):
      matcher.srcAddressGroups = args.src_address_groups
    if args.IsSpecified('dest_address_groups'):
      matcher.destAddressGroups = args.dest_address_groups
    if args.IsSpecified('src_fqdns'):
      matcher.srcFqdns = args.src_fqdns
    if args.IsSpecified('dest_fqdns'):
      matcher.destFqdns = args.dest_fqdns
    if args.IsSpecified('src_region_codes'):
      matcher.srcRegionCodes = args.src_region_codes
    if args.IsSpecified('dest_region_codes'):
      matcher.destRegionCodes = args.dest_region_codes
    if args.IsSpecified('src_threat_intelligence'):
      matcher.srcThreatIntelligences = args.src_threat_intelligence
    if args.IsSpecified('dest_threat_intelligence'):
      matcher.destThreatIntelligences = args.dest_threat_intelligence
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
    if self.support_target_type:
      if args.IsSpecified('target_type'):
        target_type = (
            holder.client.messages.FirewallPolicyRule.TargetTypeValueValuesEnum(
                args.target_type
            )
        )
      if args.IsSpecified('target_forwarding_rules'):
        target_forwarding_rules = args.target_forwarding_rules

    firewall_policy_rule = holder.client.messages.FirewallPolicyRule(
        priority=rule_utils.ConvertPriorityToInt(args.priority),
        action=args.action,
        match=matcher,
        direction=traffic_direct,
        targetServiceAccounts=target_service_accounts,
        description=args.description,
        enableLogging=enable_logging,
        disabled=disabled,
        targetSecureTags=target_secure_tags,
        securityProfileGroup=security_profile_group,
        tlsInspect=tls_inspect,
    )
    if self.support_target_type:
      firewall_policy_rule.targetType = target_type
      firewall_policy_rule.targetForwardingRules = target_forwarding_rules

    return network_firewall_policy_rule_client.CreateRule(
        firewall_policy=args.firewall_policy,
        firewall_policy_rule=firewall_policy_rule,
    )


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class CreateBeta(Create):
  r"""Creates a Compute Engine network firewall policy rule.

  *{command}* is used to create network firewall policy rules.
  """

  support_network_scopes = True
  support_target_type = False


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CreateAlpha(Create):
  r"""Creates a Compute Engine network firewall policy rule.

  *{command}* is used to create network firewall policy rules.
  """

  support_network_scopes = True
  support_target_type = True


Create.detailed_help = {
    'EXAMPLES': """\
    To create a rule with priority ``10'' in a global network firewall policy
    with name ``my-policy'' and description ``example rule'', run:

        $ {command} 10 --firewall-policy=my-policy --action=allow --description="example rule" --global-firewall-policy

    To create a rule with priority ``10'' in a regional network firewall policy
    with name ``my-region-policy'' and description ``example rule'', in
    region ``region-a'', run:

        $ {command} 10 --firewall-policy=my-policy --action=allow --description="example rule"
    """,
}
