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
"""Import network firewall policy rules command."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.network_firewall_policies import client
from googlecloudsdk.api_lib.compute.network_firewall_policies import region_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.network_firewall_policies import flags
from googlecloudsdk.command_lib.export import util as export_util
from googlecloudsdk.core.console import console_io


DETAILED_HELP = {
    'DESCRIPTION': """\
        Imports Firewall Policy rules configuration from a file.
        """,
    'EXAMPLES': """\
        Firewall Policy rules can be imported by running:

          $ {command} FIREWALL_POLICY --source=<path-to-file> --global
        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Import(base.Command):
  """Import a Compute Engine network firewall policy rules.

  Imports network firewall policy rules configuration from a file.
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
    cls.NETWORK_FIREWALL_POLICY_ARG = flags.NetworkFirewallPolicyArgument(
        required=True, operation='import rules to'
    )
    cls.NETWORK_FIREWALL_POLICY_ARG.AddArgument(
        parser, operation_type='import-rules'
    )
    export_util.AddImportFlags(parser, cls.GetSchemaPath(for_help=True))

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    firewall_policy_ref = self.NETWORK_FIREWALL_POLICY_ARG.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(client),
    )
    network_firewall_policy_client = client.NetworkFirewallPolicy(
        firewall_policy_ref, compute_client=holder.client
    )
    if hasattr(firewall_policy_ref, 'region'):
      network_firewall_policy_client = (
          region_client.RegionNetworkFirewallPolicy(
              firewall_policy_ref, compute_client=holder.client
          )
      )

    data = console_io.ReadFromFileOrStdin(args.source or '-', binary=False)

    firewall_policy_rules = export_util.Import(
        message_type=holder.client.messages.FirewallPolicy,
        stream=data,
        schema_path=self.GetSchemaPath(),
    )

    existing_firewall_policy = network_firewall_policy_client.Describe(
        only_generate_request=False
    )[0]

    console_io.PromptContinue(
        message='Firewall Policy rules will be overwritten.', cancel_on_no=True
    )

    firewall_policy = holder.client.messages.FirewallPolicy(
        fingerprint=existing_firewall_policy.fingerprint,
        rules=firewall_policy_rules.rules,
        packetMirroringRules=firewall_policy_rules.packetMirroringRules,
    )
    return network_firewall_policy_client.Update(
        firewall_policy=firewall_policy, only_generate_request=False
    )
