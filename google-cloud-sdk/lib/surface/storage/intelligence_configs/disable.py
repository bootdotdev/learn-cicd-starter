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
"""Implementation of disable command for disabling storage intelligence."""

from googlecloudsdk.api_lib.storage import storage_intelligence_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage import flags
from googlecloudsdk.core import log


# TODO: b/369949089 - Remove default universe flag after checking the
# availability of storage intelligence in different universes.
@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Disable(base.Command):
  """Disables storage intelligence."""

  detailed_help = {
      'DESCRIPTION': """
          Disable storage intelligence for the organization, sub-folder or project.
      """,
      'EXAMPLES': """
          The following command disables storage intelligence for the project. \n
            $ {command} --project=my-project
      """,
  }

  @classmethod
  def Args(cls, parser):
    flags.add_storage_intelligence_configs_level_flags(parser)

  def Run(self, args):
    client = storage_intelligence_api.StorageIntelligenceApi()

    if args.sub_folder:
      intelligence_config = client.disable_sub_folder_intelligence_config(
          args.sub_folder
      )
    elif args.project:
      intelligence_config = client.disable_project_intelligence_config(
          args.project
      )
    else:
      intelligence_config = client.disable_organization_intelligence_config(
          args.organization
      )

    log.status.Print(
        'Successfully disabled storage intelligence plan for {}.\n'.format(
            intelligence_config.name
        )
    )
    return intelligence_config
