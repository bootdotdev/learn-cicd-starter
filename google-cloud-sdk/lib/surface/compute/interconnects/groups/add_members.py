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

"""Command for adding member interconnects to an interconnect group."""

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
        *{command}* is used to add member interconnects to an interconnect
        group.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To add interconnects interconnect1 and interconnect2 to interconnect
        group example-interconnect-group, run:

          $ {command} example-interconnect-group
          --interconnects=interconnect1,interconnect2
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class AddMembers(base.UpdateCommand):
  """Add member interconnects to a Compute Engine interconnect group.

  *{command}* adds member interconnects to a Compute Engine interconnect group.
  """

  INTERCONNECT_GROUP_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.INTERCONNECT_GROUP_ARG = flags.InterconnectGroupArgument(plural=False)
    cls.INTERCONNECT_GROUP_ARG.AddArgument(parser, operation_type='update')
    flags.GetMemberInterconnects(parser)

  def Collection(self):
    return 'compute.interconnectGroups'

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.INTERCONNECT_GROUP_ARG.ResolveAsResource(args, holder.resources)
    project = properties.VALUES.core.project.GetOrFail()

    interconnect_group = client.InterconnectGroup(
        ref, project, compute_client=holder.client, resources=holder.resources
    )

    interconnects = set()
    interconnect_group_interconnects = (
        interconnect_group.Describe().interconnects
    )
    if interconnect_group_interconnects is not None:
      interconnects = set(
          property.key
          for property in interconnect_group_interconnects.additionalProperties
      )
    interconnects |= set(args.interconnects)

    return interconnect_group.Patch(
        interconnects=sorted(list(interconnects)),
    )


AddMembers.detailed_help = DETAILED_HELP
