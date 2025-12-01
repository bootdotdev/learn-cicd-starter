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
"""Command for creating interconnect groups."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.interconnects.groups import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.interconnects.groups import flags
from googlecloudsdk.core import properties

DETAILED_HELP = {
    'DESCRIPTION': """\
        *{command}* is used to create interconnect groups. An interconnect group
        connects a set of redundant interconnects between Google and the
        customer.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To create an interconnect group capable of PRODUCTION_CRITICAL, run:

          $ {command} example-interconnect-group
          --intended-topology-capability=PRODUCTION_CRITICAL
          --description="Example interconnect group"

        It is easy to add members to an existing interconnect group after
        creation using the *add-members* command.

        To create an interconnect group capable of PRODUCTION_NON_CRITICAL, with
        two members at creation time, run:

          $ {command} example-interconnect-group
          --intended-topology-capability=PRODUCTION_NON_CRITICAL
          --interconnects=interconnect-1,interconnect-2
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Create(base.CreateCommand):
  """Create a Compute Engine interconnect group.

  *{command}* is used to create interconnect groups. An interconnect group
  connects a set of redundant interconnects between Google and the customer.
  """

  INTERCONNECT_GROUP_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.INTERCONNECT_GROUP_ARG = flags.InterconnectGroupArgument(plural=False)
    cls.INTERCONNECT_GROUP_ARG.AddArgument(parser, operation_type='create')
    flags.AddDescription(parser)
    flags.AddIntendedTopologyCapabilityForCreate(parser)
    flags.GetMemberInterconnectsForCreate(parser)

  def Collection(self):
    return 'compute.interconnectGroups'

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.INTERCONNECT_GROUP_ARG.ResolveAsResource(args, holder.resources)
    project = properties.VALUES.core.project.GetOrFail()
    interconnect_group = client.InterconnectGroup(
        ref, project, compute_client=holder.client, resources=holder.resources
    )
    topology_capability = flags.GetTopologyCapability(
        holder.client.messages, args.intended_topology_capability
    )

    return interconnect_group.Create(
        description=args.description,
        topology_capability=topology_capability,
        interconnects=args.interconnects,
    )


Create.detailed_help = DETAILED_HELP
