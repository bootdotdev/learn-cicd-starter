# -*- coding: utf-8 -*- #
# Copyright 2019 Google Inc. All Rights Reserved.
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
"""Command for creating security policies rules."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import org_security_policy_rule_utils as rule_utils
from googlecloudsdk.api_lib.compute.org_security_policies import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.org_security_policies import flags
from googlecloudsdk.command_lib.compute.org_security_policies import org_security_policies_utils
from googlecloudsdk.command_lib.compute.security_policies.rules import flags as rule_flags
import six


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
class Create(base.CreateCommand):
  r"""Create a Compute Engine organizationsecurity policy rule.

  *{command}* is used to create organization security policy rules.
  """

  ORG_SECURITY_POLICY_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.ORG_SECURITY_POLICY_ARG = flags.OrgSecurityPolicyRuleArgument(
        required=True, operation='create')
    cls.ORG_SECURITY_POLICY_ARG.AddArgument(parser, operation_type='create')
    flags.AddAction(parser)
    flags.AddSecurityPolicyId(parser, operation='inserted')
    flags.AddDestIpRanges(parser)
    flags.AddLayer4Configs(parser)
    flags.AddDirection(parser)
    flags.AddEnableLogging(parser)
    flags.AddTargetResources(parser)
    flags.AddTargetServiceAccounts(parser)
    flags.AddDescription(parser)
    flags.AddOrganization(parser, required=False)
    rule_flags.AddMatcher(parser, required=False)
    rule_flags.AddPreview(parser)
    parser.add_argument(
        '--cloud-armor',
        action='store_true',
        default=False,
        help='Specified for Hierarchical Cloud Armor rules.',
    )
    parser.display_info.AddCacheUpdater(flags.OrgSecurityPoliciesCompleter)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.ORG_SECURITY_POLICY_ARG.ResolveAsResource(
        args, holder.resources, with_project=False)
    security_policy_rule_client = client.OrgSecurityPolicyRule(
        ref=ref,
        compute_client=holder.client,
        resources=holder.resources,
        version=six.text_type(self.ReleaseTrack()).lower())
    src_ip_ranges = []
    dest_ip_ranges = []
    dest_ports = []
    layer4_configs = []
    target_resources = []
    target_service_accounts = []
    enable_logging = None
    preview = None
    if args.IsSpecified('src_ip_ranges'):
      src_ip_ranges = args.src_ip_ranges
    if args.IsSpecified('dest_ip_ranges'):
      dest_ip_ranges = args.dest_ip_ranges
    if self.ReleaseTrack() == base.ReleaseTrack.ALPHA and args.IsSpecified(
        'dest_ports'):
      dest_ports = args.dest_ports
    if args.IsSpecified('layer4_configs'):
      layer4_configs = args.layer4_configs
    if args.IsSpecified('target_resources'):
      target_resources = args.target_resources
    if args.IsSpecified('target_service_accounts'):
      target_service_accounts = args.target_service_accounts
    if args.IsSpecified('enable_logging'):
      enable_logging = True
    if args.IsSpecified('preview'):
      preview = True

    dest_ports_list = rule_utils.ParseDestPorts(dest_ports,
                                                holder.client.messages)
    layer4_config_list = rule_utils.ParseLayer4Configs(layer4_configs,
                                                       holder.client.messages)
    traffic_direct = None
    if args.IsSpecified('cloud_armor'):
      if args.IsSpecified('expression'):
        matcher = holder.client.messages.SecurityPolicyRuleMatcher(
            expr=holder.client.messages.Expr(expression=args.expression)
        )
      else:
        matcher = holder.client.messages.SecurityPolicyRuleMatcher(
            versionedExpr=holder.client.messages.SecurityPolicyRuleMatcher.VersionedExprValueValuesEnum.SRC_IPS_V1,
            config=holder.client.messages.SecurityPolicyRuleMatcherConfig(
                srcIpRanges=src_ip_ranges
            ),
        )
    else:
      if self.ReleaseTrack() == base.ReleaseTrack.ALPHA:
        matcher = holder.client.messages.SecurityPolicyRuleMatcher(
            versionedExpr=holder.client.messages.SecurityPolicyRuleMatcher.VersionedExprValueValuesEnum.FIREWALL,
            config=holder.client.messages.SecurityPolicyRuleMatcherConfig(
                srcIpRanges=src_ip_ranges,
                destIpRanges=dest_ip_ranges,
                destPorts=dest_ports_list,
                layer4Configs=layer4_config_list,
            ),
        )
      else:
        matcher = holder.client.messages.SecurityPolicyRuleMatcher(
            versionedExpr=holder.client.messages.SecurityPolicyRuleMatcher.VersionedExprValueValuesEnum.FIREWALL,
            config=holder.client.messages.SecurityPolicyRuleMatcherConfig(
                srcIpRanges=src_ip_ranges,
                destIpRanges=dest_ip_ranges,
                layer4Configs=layer4_config_list,
            ),
        )
      traffic_direct = (
          holder.client.messages.SecurityPolicyRule.DirectionValueValuesEnum.INGRESS
      )
      if args.IsSpecified('direction'):
        if args.direction == 'INGRESS':
          traffic_direct = (
              holder.client.messages.SecurityPolicyRule.DirectionValueValuesEnum.INGRESS
          )
        else:
          traffic_direct = (
              holder.client.messages.SecurityPolicyRule.DirectionValueValuesEnum.EGRESS
          )

    security_policy_rule = holder.client.messages.SecurityPolicyRule(
        priority=rule_utils.ConvertPriorityToInt(ref.Name()),
        action=rule_utils.ConvertAction(args.action),
        match=matcher,
        description=args.description,
        preview=preview)
    if traffic_direct:
      security_policy_rule.direction = traffic_direct
    if target_resources:
      security_policy_rule.targetResources = target_resources
    if target_service_accounts:
      security_policy_rule.targetServiceAccounts = target_service_accounts,
    if enable_logging:
      security_policy_rule.enableLogging = enable_logging

    security_policy_id = org_security_policies_utils.GetSecurityPolicyId(
        security_policy_rule_client,
        args.security_policy,
        organization=args.organization)
    return security_policy_rule_client.Create(
        security_policy=security_policy_id,
        security_policy_rule=security_policy_rule)


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CreateAlpha(Create):
  r"""Create a Compute Engine security policy rule.

  *{command}* is used to create organization security policy rules.
  """

  ORG_SECURITY_POLICY_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.ORG_SECURITY_POLICY_ARG = flags.OrgSecurityPolicyRuleArgument(
        required=True, operation='create')
    cls.ORG_SECURITY_POLICY_ARG.AddArgument(parser, operation_type='create')
    flags.AddAction(parser)
    flags.AddSecurityPolicyId(parser, operation='inserted')
    flags.AddDestIpRanges(parser)
    flags.AddDestPorts(parser)
    flags.AddLayer4Configs(parser)
    flags.AddDirection(parser)
    flags.AddEnableLogging(parser)
    flags.AddTargetResources(parser)
    flags.AddTargetServiceAccounts(parser)
    flags.AddDescription(parser)
    flags.AddOrganization(parser, required=False)
    rule_flags.AddMatcher(parser, required=False)
    rule_flags.AddPreview(parser)
    parser.add_argument(
        '--cloud-armor',
        action='store_true',
        default=False,
        help='Specified for Hierarchical Cloud Armor rules.',
    )
    parser.display_info.AddCacheUpdater(flags.OrgSecurityPoliciesCompleter)


Create.detailed_help = {
    'EXAMPLES': """\
    To create a rule with priority ``10'' in an organization security policy with
    ID ``123456789'', run:

      $ {command} 10 --security-policy=123456789 --action=allow
      --description=example-rule --cloud-armor
    """,
}
