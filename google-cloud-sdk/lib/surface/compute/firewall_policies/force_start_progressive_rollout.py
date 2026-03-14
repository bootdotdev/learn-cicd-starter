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
"""Command for replacing the rules of organization firewall policies."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.firewall_policies import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.firewall_policies import firewall_policies_utils
from googlecloudsdk.command_lib.compute.firewall_policies import flags
import six


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class ForceStartProgressiveRollout(base.UpdateCommand):
  """Starts a new rollout of organization firewall policy."""

  FIREWALL_POLICY_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.FIREWALL_POLICY_ARG = flags.FirewallPolicyArgument(
        required=True, operation='start a new rollout of'
    )
    cls.FIREWALL_POLICY_ARG.AddArgument(
        parser, operation_type='force-start-progressive-rollout'
    )
    flags.AddArgsForceStartProgressiveRollout(parser)

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
    dest_fp_id = firewall_policies_utils.GetFirewallPolicyId(
        org_firewall_policy, ref.Name(), organization=args.organization
    )
    return org_firewall_policy.ForceStartProgressiveRollout(
        firewall_policy=dest_fp_id,
        only_generate_request=False,
    )


ForceStartProgressiveRollout.detailed_help = {
    'EXAMPLES': """\
    To start a new rollout of an organization firewall policy with ID ``123456789", run:

      $ {command} 123456789
    """,
    'IAM PERMISSIONS': """\
    To start rollout of a firewall policy, the user must have the following
    permission:
    *`compute.firewallPolicies.update`,
    *`compute.firewallPolicies.use',
    *'compute.organizations.setFirewallPolicy'.

    To find predefined roles that contain those permissions, see the [Compute
    Engine IAM roles](https://cloud.google.com/compute/docs/access/iam).
      """,
}
