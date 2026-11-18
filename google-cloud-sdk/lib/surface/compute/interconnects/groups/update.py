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
"""Command for updating interconnect groups."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.interconnects.groups import client
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.compute.interconnects.groups import flags
from googlecloudsdk.core import properties

DETAILED_HELP = {
    'DESCRIPTION': """\
        *{command}* is used to update interconnect groups.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To update an interconnect group example-interconnect-group's intended
        topology capability to PRODUCTION_CRITICAL, run:

          $ {command} example-interconnect-group
          --intended-topology-capability=PRODUCTION_CRITICAL

        To update an interconnect group example-interconnect-group's description
        to "example interconnect group description", run:

          $ {command} example-interconnect-group
          --description="example interconnect group description"

        To update an interconnect group example-interconnect-group's member
        interconnects to interconnect-1 and interconnect-2, run:

          $ {command} example-interconnect-group
          --interconnects=interconnect-1,interconnect-2
          --update-mask=interconnects

        Although you can add or remove member interconnects using this command,
        it is recommended to add or remove member interconnects using the
        *add-members* and *remove-members* commands.
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Update(base.UpdateCommand):
  """Update a Compute Engine interconnect group.

  *{command}* is used to update interconnect groups. An interconnect group
  represents a set of redundant interconnects between Google and the customer.
  """

  INTERCONNECT_GROUP_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.INTERCONNECT_GROUP_ARG = flags.InterconnectGroupArgument(plural=False)
    cls.INTERCONNECT_GROUP_ARG.AddArgument(parser, operation_type='update')
    flags.AddDescription(parser)
    flags.AddIntendedTopologyCapabilityForUpdate(parser)
    flags.GetMemberInterconnectsForUpdate(parser)
    flags.AddUpdateMask(parser)

  def Collection(self):
    return 'compute.interconnectGroups'

  def Run(self, args):
    if (
        args.description is None
        and args.intended_topology_capability is None
        and not args.interconnects
    ):
      raise exceptions.MinimumArgumentException(
          ['--description', '--intended-topology-capability', '--interconnects']
      )
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.INTERCONNECT_GROUP_ARG.ResolveAsResource(args, holder.resources)
    project = properties.VALUES.core.project.GetOrFail()
    interconnect_group = client.InterconnectGroup(
        ref, project, compute_client=holder.client, resources=holder.resources
    )
    topology_capability = None
    if args.intended_topology_capability is not None:
      topology_capability = flags.GetTopologyCapability(
          holder.client.messages, args.intended_topology_capability
      )

    return interconnect_group.Patch(
        description=args.description,
        topology_capability=topology_capability,
        interconnects=args.interconnects,
        update_mask=args.update_mask,
    )

Update.detailed_help = DETAILED_HELP
