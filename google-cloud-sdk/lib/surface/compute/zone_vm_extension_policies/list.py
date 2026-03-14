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

"""Command for listing ZoneVmExtensionPolicies."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.zone_vm_extension_policies import flags
from googlecloudsdk.core import properties


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class List(base.ListCommand):
  """List Compute Engine zone VM extension policies."""

  detailed_help = {
      'brief': 'List Compute Engine zone VM extension policies.',
      'EXAMPLES': """
     To list all zone VM extension policy, run:

       $ {command} --zone=<zone>
   """,
  }

  @staticmethod
  def Args(parser):
    flags.AddZoneFlag(parser)

  def Run(self, args):
    r"""Run the List command.

    Args:
      args: argparse.Namespace, The arguments to this command.

    Returns:
      Response calling the ZoneVmExtensionPoliciesService.List API.
    """
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    messages = holder.client.messages
    return client.MakeRequests([(
        client.apitools_client.zoneVmExtensionPolicies,
        'List',
        messages.ComputeZoneVmExtensionPoliciesListRequest(
            project=properties.VALUES.core.project.GetOrFail(),
            zone=args.zone
        ),
    )])
