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
"""Import firewall policy rules command."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.firewall_policies import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.firewall_policies import firewall_policies_utils
from googlecloudsdk.command_lib.compute.firewall_policies import flags
from googlecloudsdk.command_lib.export import util as export_util
from googlecloudsdk.core.console import console_io
import six

DETAILED_HELP = {
    'DESCRIPTION': """\
        Imports Firewall Policy rules configuration from a file.
        """,
    'EXAMPLES': """\
        Firewall Policy rules can be imported by running:

          $ {command} FIREWALL_POLICY --source=<path-to-file>
            --organization=<organization>
        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Import(base.Command):
  """Import Compute Engine organization firewall policy rules.

  Imports organization firewall policy rules configuration from a file.
  """

  NETWORK_FIREWALL_POLICY_ARG = None
  detailed_help = DETAILED_HELP

  @classmethod
  def GetApiVersion(cls):
    """Returns the API version based on the release track."""
    if cls.ReleaseTrack() == base.ReleaseTrack.ALPHA:
      return 'alpha'
    elif cls.ReleaseTrack() == base.ReleaseTrack.BETA:
      return 'beta'
    return 'v1'

  @classmethod
  def GetSchemaPath(cls, for_help=False):
    """Returns the resource schema path."""
    return export_util.GetSchemaPath(
        'compute',
        cls.GetApiVersion(),
        'FirewallPolicy',
        for_help=for_help,
    )

  @classmethod
  def Args(cls, parser):
    cls.FIREWALL_POLICY_ARG = flags.FirewallPolicyArgument(
        required=True, operation='imports rules to'
    )
    cls.FIREWALL_POLICY_ARG.AddArgument(parser, operation_type='export-rules')
    parser.add_argument(
        '--organization',
        help=(
            'Organization in which the organization firewall policy rules'
            ' import to. Must be set if FIREWALL_POLICY is short name.'
        ),
    )
    export_util.AddImportFlags(parser, cls.GetSchemaPath(for_help=True))

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    firewall_policy_ref = self.FIREWALL_POLICY_ARG.ResolveAsResource(
        args, holder.resources, with_project=False
    )
    org_firewall_policy = client.OrgFirewallPolicy(
        ref=firewall_policy_ref,
        compute_client=holder.client,
        resources=holder.resources,
        version=six.text_type(self.ReleaseTrack()).lower(),
    )

    data = console_io.ReadFromFileOrStdin(args.source or '-', binary=False)

    firewall_policy_rules = export_util.Import(
        message_type=holder.client.messages.FirewallPolicy,
        stream=data,
        schema_path=self.GetSchemaPath(),
    )

    fp_id = firewall_policies_utils.GetFirewallPolicyId(
        org_firewall_policy,
        firewall_policy_ref.Name(),
        organization=args.organization,
    )

    existing_firewall_policy = org_firewall_policy.Describe(
        fp_id=fp_id, only_generate_request=False
    )[0]

    console_io.PromptContinue(
        message='Firewall Policy rules will be overwritten.', cancel_on_no=True
    )

    firewall_policy = holder.client.messages.FirewallPolicy(
        fingerprint=existing_firewall_policy.fingerprint,
        rules=firewall_policy_rules.rules,
        packetMirroringRules=firewall_policy_rules.packetMirroringRules,
    )

    return org_firewall_policy.Update(
        fp_id=fp_id,
        only_generate_request=False,
        firewall_policy=firewall_policy,
    )
