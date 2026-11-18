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

"""Command for deleting GlobalVmExtensionPolicies."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.global_vm_extension_policies import flags
from googlecloudsdk.core import properties


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Delete(base.DeleteCommand):
  """Delete a Compute Engine global VM extension policy."""

  detailed_help = {
      'brief': 'Delete a Compute Engine global VM extension policy.',
      'EXAMPLES': """
     To delete a global VM extension policy, run:

       $ {command} test-policy-name
   """,
  }

  @staticmethod
  def Args(parser):
    Delete.GlobalVmExtensionPoliciesArg = flags.MakeGlobalVmExtensionPolicyArg()
    Delete.GlobalVmExtensionPoliciesArg.AddArgument(
        parser, operation_type='delete'
    )
    flags.AddRolloutInputArgs(parser)
    flags.AddRolloutRetryUUID(parser)

  def Run(self, args):
    r"""Run the Delete command.

    Args:
      args: argparse.Namespace, The arguments to this command.

    Returns:
      Response calling the GlobalVmExtensionPoliciesService.Delete API.
    """
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    messages = holder.client.messages

    resource_ref = Delete.GlobalVmExtensionPoliciesArg.ResolveAsResource(
        args,
        holder.resources
    )
    rollout_operation_input = flags.BuildRolloutOperationInput(args, messages)
    flags.InsertRetryUuid(args, rollout_operation_input=rollout_operation_input)
    return client.MakeRequests([(
        client.apitools_client.globalVmExtensionPolicies,
        'Delete',
        messages.ComputeGlobalVmExtensionPoliciesDeleteRequest(
            project=resource_ref.project,
            globalVmExtensionPolicy=resource_ref.Name(),
            globalVmExtensionPolicyRolloutOperationRolloutInput=rollout_operation_input,
        ),
    )])
