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

"""Command for updating ZoneVmExtensionPolicies."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.zone_vm_extension_policies import flags


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Update(base.UpdateCommand):
  """Update a Compute Engine zone VM extension policy."""

  detailed_help = {
      'brief': 'Update a Compute Engine zone VM extension policy.',
      'EXAMPLES': """
     To update a zone VM extension policy, run:

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
    Update.ZoneVmExtensionPoliciesArg = flags.MakeZoneVmExtensionPolicyArg()
    Update.ZoneVmExtensionPoliciesArg.AddArgument(
        parser, operation_type='update'
    )
    flags.AddExtensionPolicyArgs(parser)

  def Run(self, args):
    r"""Run the Update command.

    Args:
      args: argparse.Namespace, The arguments to this command.

    Returns:
      Response calling the ZoneVmExtensionPoliciesService.Update API.
    """
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    messages = holder.client.messages

    resource_ref = Update.ZoneVmExtensionPoliciesArg.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(client),
    )
    flags.ParseExtensionConfigs(
        args.extensions, args.config, args.config_from_file
    )
    flags.ParseExtensionVersions(args.extensions, args.version)
    zve_policy = flags.BuildZoneVmExtensionPolicy(resource_ref, args, messages)
    return client.MakeRequests([(
        client.apitools_client.zoneVmExtensionPolicies,
        'Update',
        messages.ComputeZoneVmExtensionPoliciesUpdateRequest(
            project=resource_ref.project,
            zone=resource_ref.zone,
            vmExtensionPolicy=resource_ref.Name(),
            vmExtensionPolicyResource=zve_policy,
        ),
    )])
