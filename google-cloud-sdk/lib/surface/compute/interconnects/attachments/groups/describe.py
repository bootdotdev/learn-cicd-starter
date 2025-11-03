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
"""Command for describing interconnect attachment groups."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.interconnects.attachments.groups import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.interconnects.attachments.groups import flags
from googlecloudsdk.core import properties

DETAILED_HELP = {
    'DESCRIPTION': """\
        *{command}* is used to describe interconnect attachment groups.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To describe an interconnect attachment group, run:

          $ {command} example-attachment-group
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Describe(base.DescribeCommand):
  """Describe a Compute Engine interconnect attachment group.

  *{command}* displays all data associated with Compute Engine
  interconnect attachment group in a project.
  """

  ATTACHMENT_GROUP_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.ATTACHMENT_GROUP_ARG = flags.InterconnectAttachmentGroupArgument()
    cls.ATTACHMENT_GROUP_ARG.AddArgument(parser, operation_type='describe')

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.ATTACHMENT_GROUP_ARG.ResolveAsResource(args, holder.resources)
    project = properties.VALUES.core.project.GetOrFail()

    attachment_group = client.InterconnectAttachmentGroup(
        ref, project, compute_client=holder.client
    )
    return attachment_group.Describe()


Describe.detailed_help = DETAILED_HELP
