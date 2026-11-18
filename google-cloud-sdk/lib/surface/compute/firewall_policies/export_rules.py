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
"""Export firewall policy rules command."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import sys

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.firewall_policies import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.firewall_policies import firewall_policies_utils
from googlecloudsdk.command_lib.compute.firewall_policies import flags
from googlecloudsdk.command_lib.export import util as export_util
from googlecloudsdk.core.util import files
import six

DETAILED_HELP = {
    'DESCRIPTION': """\
        Exports Firewall Policy rules configuration to a file.
        """,
    'EXAMPLES': """\
        Firewall Policy rules can be exported by running:

          $ {command} FIREWALL_POLICY --destination=<path-to-file>
            --organization=<organization>
        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Export(base.Command):
  """Export Compute Engine organization firewall policy rules.

  Exports organization firewall policy rules configuration to a file.
  This configuration can be imported at a later time.
  """

  FIREWALL_POLICY_ARG = None
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
        required=True, operation='export rules from'
    )
    cls.FIREWALL_POLICY_ARG.AddArgument(parser, operation_type='export-rules')
    parser.add_argument(
        '--organization',
        help=(
            'Organization in which the organization firewall policy rules'
            ' export from. Must be set if FIREWALL_POLICY is short name.'
        ),
    )
    export_util.AddExportFlags(parser, cls.GetSchemaPath(for_help=True))

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

    fp_id = firewall_policies_utils.GetFirewallPolicyId(
        org_firewall_policy,
        firewall_policy_ref.Name(),
        organization=args.organization,
    )

    firewall_policy = org_firewall_policy.Describe(
        fp_id=fp_id, only_generate_request=False
    )[0]

    # only rules are exported
    firewall_policy_rules = holder.client.messages.FirewallPolicy(
        rules=firewall_policy.rules
    )

    if args.destination:
      with files.FileWriter(args.destination) as stream:
        export_util.Export(
            message=firewall_policy_rules,
            stream=stream,
            schema_path=self.GetSchemaPath(),
        )
    else:
      export_util.Export(
          message=firewall_policy_rules,
          stream=sys.stdout,
          schema_path=self.GetSchemaPath(),
      )
