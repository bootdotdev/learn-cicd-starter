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
"""Implementation of disable command for disabling management hub."""

from googlecloudsdk.api_lib.storage import management_hub_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage import flags
from googlecloudsdk.core import log


# TODO: b/369949089 - Remove default universe flag after checking the
# availability of management hub in different universes.
@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Disable(base.Command):
  """Disables Management Hub."""

  detailed_help = {
      'DESCRIPTION': """
          Disable management hub for the organization, sub-folder or project.
      """,
      'EXAMPLES': """
          The following command disables management hub for the project. \n
            ${command} --project=my-project
      """,
  }

  @classmethod
  def Args(cls, parser):
    flags.add_management_hub_level_flags(parser)

  def Run(self, args):
    client = management_hub_api.ManagementHubApi()

    if args.sub_folder:
      management_hub = client.disable_sub_folder_management_hub(args.sub_folder)
    elif args.project:
      management_hub = client.disable_project_management_hub(args.project)
    else:
      management_hub = client.disable_organization_management_hub(
          args.organization
      )

    log.status.Print(
        'Successfully disabled management hub plan for {}.\n'.format(
            management_hub.name
        )
    )
    return management_hub
