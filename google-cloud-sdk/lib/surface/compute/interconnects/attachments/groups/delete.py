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

"""Command for deleting interconnect attachment groups."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import utils
from googlecloudsdk.api_lib.compute.interconnects.attachments.groups import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.interconnects.attachments.groups import flags
from googlecloudsdk.core import properties

DETAILED_HELP = {
    'DESCRIPTION': """\
        *{command}* is used to delete interconnect attachment groups.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To delete an interconnect attachment group, run:

          $ {command} example-attachment-group"

        Although not shown in this example, you can delete multiple interconnect
        attachment groups in a single command.
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Delete(base.DeleteCommand):
  """Delete Compute Engine interconnect attachment groups.

  *{command}* deletes Compute Engine interconnect attachment groups.
  Interconnect attachment groups can be deleted even if they are referenced by
  interconnect attachments. Each interconnect attachment in the group will be
  updated to remove its reference to this group.
  """

  ATTACHMENT_GROUP_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.ATTACHMENT_GROUP_ARG = flags.InterconnectAttachmentGroupArgument(
        plural=True
    )
    cls.ATTACHMENT_GROUP_ARG.AddArgument(parser, operation_type='delete')

  def Collection(self):
    return 'compute.interconnectAttachmentGroups'

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    refs = self.ATTACHMENT_GROUP_ARG.ResolveAsResource(args, holder.resources)
    project = properties.VALUES.core.project.GetOrFail()
    utils.PromptForDeletion(refs)

    requests = []
    for ref in refs:
      attachment_group = client.InterconnectAttachmentGroup(
          ref, project, compute_client=holder.client
      )
      requests.extend(attachment_group.Delete(only_generate_request=True))

    return holder.client.MakeRequests(requests)


Delete.detailed_help = DETAILED_HELP
