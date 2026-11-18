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
"""Implementation of describe command for getting storage intelligence configuration."""

from googlecloudsdk.api_lib.storage import storage_intelligence_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage import flags


# TODO: b/369949089 - Remove default universe flag after checking the
# availability of storage intelligence in different universes.
@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Describe(base.DescribeCommand):
  """Describes storage intelligence configuration."""

  detailed_help = {
      'DESCRIPTION': """
          Describe storage intelligence config for the organization, sub-folder
          or project.
      """,
      'EXAMPLES': """
          The following command describes storage intelligence config for the sub-folder with
          id `123456`. \n
            $ {command} --sub-folder=123456
      """,
  }

  @classmethod
  def Args(cls, parser):
    flags.add_storage_intelligence_configs_level_flags(parser)

  def Run(self, args):
    client = storage_intelligence_api.StorageIntelligenceApi()

    if args.sub_folder:
      return client.get_sub_folder_intelligence_config(args.sub_folder)
    elif args.project:
      return client.get_project_intelligence_config(args.project)
    elif args.organization:
      return client.get_organization_intelligence_config(args.organization)
