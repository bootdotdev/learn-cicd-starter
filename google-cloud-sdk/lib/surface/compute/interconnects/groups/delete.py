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

"""Command for deleting interconnect groups."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import utils
from googlecloudsdk.api_lib.compute.interconnects.groups import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.interconnects.groups import flags
from googlecloudsdk.core import properties

DETAILED_HELP = {
    'DESCRIPTION': """\
        *{command}* is used to delete interconnect groups.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To delete an interconnect group, run:

          $ {command} example-interconnect-group"

        Although not shown in this example, you can delete multiple interconnect
        groups in a single command.
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Delete(base.DeleteCommand):
  """Delete Compute Engine interconnect groups.

  *{command}* deletes Compute Engine interconnect groups. Interconnect groups
   can be deleted even if they are referenced by interconnects. Each
   interconnect in the group will be updated to remove its reference to this
   group.
  """

  INTERCONNECT_GROUP_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.INTERCONNECT_GROUP_ARG = flags.InterconnectGroupArgument(plural=True)
    cls.INTERCONNECT_GROUP_ARG.AddArgument(parser, operation_type='delete')

  def Collection(self):
    return 'compute.interconnectGroups'

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    refs = self.INTERCONNECT_GROUP_ARG.ResolveAsResource(args, holder.resources)
    project = properties.VALUES.core.project.GetOrFail()
    utils.PromptForDeletion(refs)

    requests = []
    for ref in refs:
      interconnect_group = client.InterconnectGroup(
          ref, project, compute_client=holder.client
      )
      requests.extend(interconnect_group.Delete(only_generate_request=True))

    return holder.client.MakeRequests(requests)


Delete.detailed_help = DETAILED_HELP
