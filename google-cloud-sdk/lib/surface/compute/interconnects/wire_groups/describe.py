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
"""Command for describing wire groups."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.interconnects.wire_groups import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.interconnects.cross_site_networks import flags as cross_site_network_flags
from googlecloudsdk.command_lib.compute.interconnects.wire_groups import flags
from googlecloudsdk.core import properties


_DETAILED_HELP = {
    'DESCRIPTION': """\
        *{command}* is used to describe a wire group.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To describe a wire group, run:

          $ {command} example-wg --cross-site-network=example-csn
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Describe(base.DescribeCommand):
  """Describe a Compute Engine wire group.

  *{command}* displays all data associated with Compute Engine
  wire group in a project.
  """

  # Framework override.
  detailed_help = _DETAILED_HELP

  WIRE_GROUP_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.CROSS_SITE_NETWORK_ARG = (
        cross_site_network_flags.CrossSiteNetworkArgumentForOtherResource()
    )
    cls.CROSS_SITE_NETWORK_ARG.AddArgument(parser)
    cls.WIRE_GROUP_ARG = flags.WireGroupArgument(plural=False)
    cls.WIRE_GROUP_ARG.AddArgument(parser, operation_type='describe')

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.WIRE_GROUP_ARG.ResolveAsResource(
        args,
        holder.resources,
        default_scope=compute_scope.ScopeEnum.GLOBAL,
        additional_params={'crossSiteNetwork': args.cross_site_network},
    )

    project = properties.VALUES.core.project.GetOrFail()

    wire_group = client.WireGroup(
        ref,
        project=project,
        cross_site_network=args.cross_site_network,
        compute_client=holder.client,
    )
    return wire_group.Describe()
