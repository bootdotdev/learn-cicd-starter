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
"""Delete a Cloud NetApp Host Group."""

from googlecloudsdk.api_lib.netapp.host_groups import client as host_groups_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp import flags
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
@base.Hidden
class Delete(base.DeleteCommand):
  """Delete a Cloud NetApp Host Group."""

  detailed_help = {
      'DESCRIPTION': """\
          Delete a Cloud NetApp Host Group.
          """,
      'EXAMPLES': """\
          The following command deletes a Host Group named NAME:

              $ {command} NAME --location=us-central1

          To delete a Host Group named NAME asynchronously, run the following command:

              $ {command} NAME --location=us-central1 --async
          """,
  }

  @staticmethod
  def Args(parser):
    """Add args for deleting a Host Group."""
    concept_parsers.ConceptParser([
        flags.GetHostGroupPresentationSpec('The Host Group to delete.')
    ]).AddToParser(parser)
    flags.AddResourceAsyncFlag(parser)

  def Run(self, args):
    """Delete a Cloud NetApp Host Group in the current project."""
    host_group_ref = args.CONCEPTS.host_group.Parse()

    if not args.quiet:
      delete_warning = (
          'You are about to delete a Host Group {}.\nAre you sure?'.format(
              host_group_ref.RelativeName()
          )
      )
      if not console_io.PromptContinue(message=delete_warning):
        return None

    client = host_groups_client.HostGroupsClient(self.ReleaseTrack())
    result = client.DeleteHostGroup(host_group_ref, args.async_)
    if args.async_:
      command = 'gcloud {} netapp host-groups list'.format(
          self.ReleaseTrack().prefix
      )
      log.status.Print(
          'Check the status of the deletion by listing all host groups:\n  '
          '$ {} '.format(command)
      )
    return result
