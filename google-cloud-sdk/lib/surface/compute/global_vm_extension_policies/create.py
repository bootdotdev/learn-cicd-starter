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

"""Command for creating GlobalVmExtensionPolicies."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.global_vm_extension_policies import flags


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Create(base.CreateCommand):
  """Create a Compute Engine global VM extension policy."""

  detailed_help = {
      'brief': 'Create a Compute Engine global VM extension policy.',
      'EXAMPLES': """
     To create a global VM extension policy, run:

       $ {command} test-policy-name \
        --description="test policy" \
        --extensions=extension1,extension2 \
        --version=extension1=version1,extension2=version2 \
        --config=extension1="config1",extension2="config2" \
        --inclusion-labels=env=prod \
        --inclusion-labels=env=preprod,workload=load-test \
        --priority=1000
   """,
  }

  @staticmethod
  def Args(parser):
    Create.GlobalVmExtensionPoliciesArg = flags.MakeGlobalVmExtensionPolicyArg()
    Create.GlobalVmExtensionPoliciesArg.AddArgument(
        parser, operation_type='create'
    )
    flags.AddExtensionPolicyArgs(parser)

  def Run(self, args):
    r"""Run the create command.

    Args:
      args: argparse.Namespace, The arguments to this command.

    Returns:
      Response calling the GlobalVmExtensionPoliciesService.Insert API.
    """
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    messages = holder.client.messages
    resource_ref = Create.GlobalVmExtensionPoliciesArg.ResolveAsResource(
        args,
        holder.resources,
    )

    gve_policy = flags.BuildGlobalVmExtensionPolicy(
        resource_ref, args, messages
    )
    return client.MakeRequests([(
        client.apitools_client.globalVmExtensionPolicies,
        'Insert',
        messages.ComputeGlobalVmExtensionPoliciesInsertRequest(
            project=resource_ref.project,
            globalVmExtensionPolicy=gve_policy,
        ),
    )])
