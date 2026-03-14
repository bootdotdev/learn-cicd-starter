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
"""Command for creating interconnect attachment groups."""

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
        *{command}* is used to create interconnect attachment groups. An
        interconnect attachment group connects a set of redundant interconnect
        attachments between Google and the customer.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To create an interconnect attachment group capable of
        PRODUCTION_CRITICAL, run:

          $ {command} example-attachment-group
          --intended-availability-sla=PRODUCTION_CRITICAL
          --description="Example interconnect attachment group"

        It is easy to add members to an existing interconnect attachment group
        after creation using the *add-members* command.

        To create an interconnect attachment group capable of
        PRODUCTION_NON_CRITICAL, with two members at creation time, run:

          $ {command} example-attachment-group
          --intended-availability-sla=PRODUCTION_NON_CRITICAL
          --attachments=region-1/attachment-1,region-2/attachment-2
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Create(base.CreateCommand):
  """Create a Compute Engine interconnect attachment group.

  *{command}* is used to create interconnect attachment groups. An interconnect
  attachment group connects a set of redundant interconnect attachments between
  Google and the customer.
  """

  ATTACHMENT_GROUP_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.ATTACHMENT_GROUP_ARG = flags.InterconnectAttachmentGroupArgument(
        plural=False
    )
    cls.ATTACHMENT_GROUP_ARG.AddArgument(parser, operation_type='create')
    flags.AddDescription(parser)
    flags.AddIntendedAvailabilitySlaForCreate(parser)
    flags.GetMemberInterconnectAttachmentsForCreate(parser)

  def Collection(self):
    return 'compute.interconnectAttachmentGroups'

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.ATTACHMENT_GROUP_ARG.ResolveAsResource(args, holder.resources)
    project = properties.VALUES.core.project.GetOrFail()
    attachment_group = client.InterconnectAttachmentGroup(
        ref, project, compute_client=holder.client, resources=holder.resources
    )
    availability_sla = flags.GetIntendedAvailabilitySla(
        holder.client.messages, args.intended_availability_sla
    )
    attachments = flags.ParseAttachments(args.attachments)

    return attachment_group.Create(
        description=args.description,
        availability_sla=availability_sla,
        attachments=attachments,
    )


Create.detailed_help = DETAILED_HELP
