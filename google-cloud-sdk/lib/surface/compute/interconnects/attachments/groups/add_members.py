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

"""Command for adding interconnect attachments to an interconnect attachment group."""

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
        *{command}* is used to add member interconnect attachments to an
        interconnect attachment group.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To add attachment-1 and attachment-2 to interconnect attachment group
        example-attachment-group, run:

          $ {command} example-attachment-group
          --attachments=region-1/attachment-1,region-2/attachment-2
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class AddMembers(base.UpdateCommand):
  """Add member interconnect attachments to a Compute Engine interconnect attachment group.

  *{command}* adds member interconnect attachments to a Compute Engine
  interconnect attachment group.
  """

  ATTACHMENT_GROUP_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.ATTACHMENT_GROUP_ARG = flags.InterconnectAttachmentGroupArgument(
        plural=False
    )
    cls.ATTACHMENT_GROUP_ARG.AddArgument(parser, operation_type='update')
    flags.GetMemberInterconnectAttachments(parser)

  def Collection(self):
    return 'compute.interconnectAttachmentGroups'

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.ATTACHMENT_GROUP_ARG.ResolveAsResource(args, holder.resources)
    project = properties.VALUES.core.project.GetOrFail()

    attachment_group = client.InterconnectAttachmentGroup(
        ref, project, compute_client=holder.client, resources=holder.resources
    )

    attachments = set()
    attachment_group_attachments = attachment_group.Describe().attachments
    if attachment_group_attachments is not None:
      attachments = set(
          property.key
          for property in attachment_group_attachments.additionalProperties
      )
    attachments |= set(args.attachments)

    return attachment_group.Patch(
        attachments=flags.ParseAttachments(sorted(list(attachments))),
    )


AddMembers.detailed_help = DETAILED_HELP
