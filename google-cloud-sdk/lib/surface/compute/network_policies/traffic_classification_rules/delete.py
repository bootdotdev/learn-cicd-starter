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
"""Command for deleting network policy rules."""


from typing import ClassVar

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.network_policies import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.network_policies import flags
from googlecloudsdk.command_lib.compute.network_policies import rules_utils


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Delete(base.DeleteCommand):
  """Deletes a Compute Engine network policy rule.

  *{command}* is used to delete network policy rules.
  """

  NETWORK_POLICY_ARG: ClassVar[compute_flags.ResourceArgument]

  @classmethod
  def Args(cls, parser):
    cls.NETWORK_POLICY_ARG = flags.NetworkPolicyRuleArgument(
        required=True, operation='delete'
    )
    cls.NETWORK_POLICY_ARG.AddArgument(parser, operation_type='delete')
    flags.AddArgsRemoveRule(parser)
    parser.display_info.AddCacheUpdater(flags.NetworkPoliciesCompleter)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.NETWORK_POLICY_ARG.ResolveAsResource(args, holder.resources)
    network_policy_rule_client = client.NetworkPolicyRule(
        ref=ref, compute_client=holder.client
    )

    return network_policy_rule_client.DeleteRule(
        network_policy=args.network_policy,
        priority=rules_utils.ConvertPriorityToInt(args.priority),
    )


Delete.detailed_help = {
    'EXAMPLES': """\
    To delete a rule with priority ``10'' in a network policy
    with name ``my-policy'', in region ``region-a'', run:

      $ {command} --priority=10 --network-policy=my-policy \
        --network-policy-region=region-a
    """,
}
