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

"""Command for getting GlobalVmExtensionPolicies."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.global_vm_extension_policies import flags


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Describe(base.DescribeCommand):
  """Describe a Compute Engine global VM extension policy."""

  detailed_help = {
      'brief': 'Describe a Compute Engine global VM extension policy.',
      'EXAMPLES': """
     To describe a global VM extension policy, run:

       $ {command} test-policy-name
   """,
  }

  @staticmethod
  def Args(parser):
    Describe.GlobalVmExtensionPoliciesArg = flags.MakeGlobalVmExtensionPolicyArg()
    Describe.GlobalVmExtensionPoliciesArg.AddArgument(
        parser, operation_type='describe'
    )

  def Run(self, args):
    r"""Run the Describe command.

    Args:
      args: argparse.Namespace, The arguments to this command.

    Returns:
      Response calling the GlobalVmExtensionPoliciesService.Describe API.
    """
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    messages = holder.client.messages

    resource_ref = Describe.GlobalVmExtensionPoliciesArg.ResolveAsResource(
        args,
        holder.resources
    )

    return client.MakeRequests([(
        client.apitools_client.globalVmExtensionPolicies,
        'Get',
        messages.ComputeGlobalVmExtensionPoliciesGetRequest(
            project=resource_ref.project,
            globalVmExtensionPolicy=resource_ref.Name(),
        ),
    )])

