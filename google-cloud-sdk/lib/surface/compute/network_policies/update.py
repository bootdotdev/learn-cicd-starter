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
"""Command for updating network policies."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import argparse
from typing import ClassVar

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.network_policies import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.network_policies import flags


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Update(base.UpdateCommand):
  """Update a Compute Engine network policy.

  *{command}* is used to update network policies. A network
  policy is a set of rules that classifies network traffic.
  """

  NETWORK_POLICY_ARG: ClassVar[compute_flags.ResourceArgument]

  @classmethod
  def Args(cls, parser: argparse.ArgumentParser):
    cls.NETWORK_POLICY_ARG = flags.NetworkPolicyArgument(
        required=True, operation='update'
    )
    cls.NETWORK_POLICY_ARG.AddArgument(parser, operation_type='update')
    flags.AddArgsUpdateNetworkPolicy(parser)

  def Run(self, args: argparse.Namespace):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.NETWORK_POLICY_ARG.ResolveAsResource(args, holder.resources)

    network_policy_client = client.NetworkPolicy(
        ref, compute_client=holder.client
    )

    new_network_policy = holder.client.messages.NetworkPolicy(
        description=args.description,
    )
    return network_policy_client.Update(network_policy=new_network_policy)


Update.detailed_help = {
    'EXAMPLES': """\
    To update a network policy with name ``my-policy'',
    to change the description to ``New description'', run:

      $ {command} my-policy \
          --description='New description' \
          --region=my-region
    """,
}
