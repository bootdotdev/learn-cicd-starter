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
"""Command for getting interconnect group operational status."""

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
        *{command}* is used to get the operational status of an interconnect
        group.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To get the operational status of interconnect group
        example-interconnect-group, run:

          $ {command} example-interconnect-group
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class GetOperationalStatus(base.DescribeCommand):
  """Get the operational status of a Compute Engine interconnect group.

  *{command}* gets the operational status of a Compute Engine
  interconnect group in a project.
  """

  INTERCONNECT_GROUP_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.INTERCONNECT_GROUP_ARG = flags.InterconnectGroupArgument()
    cls.INTERCONNECT_GROUP_ARG.AddArgument(
        parser, operation_type='get operational status'
    )

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.INTERCONNECT_GROUP_ARG.ResolveAsResource(args, holder.resources)
    project = properties.VALUES.core.project.GetOrFail()

    interconnect_group = client.InterconnectGroup(
        ref, project, compute_client=holder.client
    )
    return interconnect_group.GetOperationalStatus()


GetOperationalStatus.detailed_help = DETAILED_HELP
