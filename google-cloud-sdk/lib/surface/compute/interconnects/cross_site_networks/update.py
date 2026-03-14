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
"""Command for updating cross site networks."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.interconnects.cross_site_networks import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.interconnects.cross_site_networks import flags
from googlecloudsdk.core import properties


_DETAILED_HELP = {
    'DESCRIPTION': """\
        *{command}* is used to update cross site networks.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To update a cross site network's description, run:

          $ {command} example-csn --description="New description"
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Update(base.UpdateCommand):
  """Update a Compute Engine cross site network.

  *{command}* is used to update cross site networks. A cross site network
  encapsulates wire groups.
  """

  # Framework override.
  detailed_help = _DETAILED_HELP

  CROSS_SITE_NETWORK_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.CROSS_SITE_NETWORK_ARG = flags.CrossSiteNetworkArgument(plural=False)
    cls.CROSS_SITE_NETWORK_ARG.AddArgument(parser, operation_type='update')
    flags.AddDescription(parser)

  def Collection(self):
    return 'compute.crossSiteNetworks'

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.CROSS_SITE_NETWORK_ARG.ResolveAsResource(args, holder.resources)
    project = properties.VALUES.core.project.GetOrFail()
    cross_site_network = client.CrossSiteNetwork(
        ref,
        project,
        compute_client=holder.client,
        resources=holder.resources,
    )

    return cross_site_network.Patch(description=args.description)
