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
"""Command for updating interconnect attachment groups."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.interconnects.attachments.groups import client
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.compute.interconnects.attachments.groups import flags
from googlecloudsdk.core import properties

DETAILED_HELP = {
    'DESCRIPTION': """\
        *{command}* is used to update interconnect attachment groups.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To update an interconnect attachment group example-attachment-group's
        intended availability SLA to PRODUCTION_CRITICAL, run:

          $ {command} example-attachment-group
          --intended-availability-sla=PRODUCTION_CRITICAL

        To update an interconnect attachment group example-attachment-group's
        description to "example attachment group description", run:

          $ {command} example-attachment-group
          --description="example attachment group description"

        To update an interconnect attachment group example-attachment-group's
        member attachments to attachment-1 and attachment-2, run:

          $ {command} example-attachment-group
          --attachments=region-1/attachment-1,region-2/attachment-2
          --update-mask=attachments

        Although you can add or remove member attachments using this command, it
        is recommended to add or remove member attachments using the
        *add-members* and *remove-members* commands.
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Update(base.UpdateCommand):
  """Update a Compute Engine interconnect attachment group.

  *{command}* is used to update interconnect attachment groups. An interconnect
  attachment group connects a set of redundant interconnect attachments between
  Google and the customer.
  """

  ATTACHMENT_GROUP_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.ATTACHMENT_GROUP_ARG = flags.InterconnectAttachmentGroupArgument(
        plural=False
    )
    cls.ATTACHMENT_GROUP_ARG.AddArgument(parser, operation_type='update')
    flags.AddDescription(parser)
    flags.AddIntendedAvailabilitySlaForUpdate(parser)
    flags.GetMemberInterconnectAttachmentsForCreate(parser)
    flags.AddUpdateMask(parser)

  def Collection(self):
    return 'compute.interconnectAttachmentGroups'

  def Run(self, args):
    if (
        args.description is None
        and args.intended_availability_sla is None
        and not args.attachments
    ):
      raise exceptions.MinimumArgumentException(
          ['--description', '--intended-availability-sla', '--attachments']
      )
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

    return attachment_group.Patch(
        description=args.description,
        availability_sla=availability_sla,
        attachments=attachments,
        update_mask=args.update_mask,
    )


Update.detailed_help = DETAILED_HELP
