
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
"""Implementation of enable command for enabling storage intelligence."""

from googlecloudsdk.api_lib.storage import storage_intelligence_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage import flags
from googlecloudsdk.core import log


# TODO: b/369949089 - Remove default universe flag after checking the
# availability of storage intelligence in different universes.


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Enable(base.Command):
  """Enables storage intelligence."""
  detailed_help = {
      'DESCRIPTION': """
          Enable storage intelligence plan for the organization, sub-folder or project
          along with filters. The command sets `STANDARD` edition by default if
          no other edition flags like ``--trial-edition`` are specified.
      """,
      'EXAMPLES': """
          To remove buckets from the storage intelligence plan, Use the following
          command with ``--exclude-bucket-id-regexes'' flag.
          to specify list of bucket id regexes.,\n
            $ {command} --organization=my-org --exclude-bucket-id-regexes="my-bucket-.*"

          To apply location based filters in the storage intelligence plan, Use
          ``--include-locations'' or ``--exclude-locations'' flags to specify allowed
          list of locations or excluded list of locations. The following
          command updates storage intelligence plan of sub-folder `123456` with the
          specified list of included locations.,\n
            $ {command} --sub-folder=123456 --include-locations="us-east1","us-west1"

          The following command enables storage intelligence with Trial edition
          for the given project,\n
            $ {command} --project=my-project --trial-edition
      """,
  }

  @classmethod
  def Args(cls, parser):
    parser.SetSortArgs(False)
    flags.add_storage_intelligence_configs_level_flags(parser)
    settings = parser.add_group(category='SETTINGS')
    flags.add_storage_intelligence_configs_settings_flags(settings)

  def Run(self, args):
    client = storage_intelligence_api.StorageIntelligenceApi()

    if args.project:
      intelligence_config = (
          client.update_project_intelligence_config(
              args.project,
              inherit_from_parent=None,
              trial_edition=args.trial_edition,
              include_locations=args.include_locations,
              exclude_locations=args.exclude_locations,
              include_bucket_id_regexes=args.include_bucket_id_regexes,
              exclude_bucket_id_regexes=args.exclude_bucket_id_regexes,
          )
      )
    elif args.sub_folder:
      intelligence_config = client.update_sub_folder_intelligence_config(
          args.sub_folder,
          inherit_from_parent=None,
          trial_edition=args.trial_edition,
          include_locations=args.include_locations,
          exclude_locations=args.exclude_locations,
          include_bucket_id_regexes=args.include_bucket_id_regexes,
          exclude_bucket_id_regexes=args.exclude_bucket_id_regexes,
      )
    else:
      intelligence_config = client.update_organization_intelligence_config(
          args.organization,
          inherit_from_parent=None,
          trial_edition=args.trial_edition,
          include_locations=args.include_locations,
          exclude_locations=args.exclude_locations,
          include_bucket_id_regexes=args.include_bucket_id_regexes,
          exclude_bucket_id_regexes=args.exclude_bucket_id_regexes,
      )

    log.status.Print(
        'Successfully enabled storage intelligence plan for {}.\n'.format(
            intelligence_config.name
        )
    )
    return intelligence_config
