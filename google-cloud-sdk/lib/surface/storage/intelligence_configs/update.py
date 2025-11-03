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
"""Implementation of update command for updating storage intelligence configuration."""

from googlecloudsdk.api_lib.storage import storage_intelligence_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage import flags
from googlecloudsdk.core import log


# TODO: b/369949089 - Remove default universe flag after checking the
# availability of storage intelligence in different universes.
@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Update(base.Command):
  """Updates storage intelligence configuration."""

  detailed_help = {
      'DESCRIPTION': """
          Update storage intelligence configuration for the organization, sub-folder
          or project. The command sets `STANDARD` edition by default if no other
          edition flags like ``--trial-edition`` or ``--inherit-from-parent``
          are specified.
      """,
      'EXAMPLES': """
          To limit buckets in the storage intelligence configuration, Use the following
          command with ``--include-bucket-id-regexes'' flag.
          to specify list of bucket ids and bucket id regexes.,\n
            $ {command} --organization=my-org --include-bucket-id-regexes=my-bucket-.*

          To apply location based filters in the storage intelligence configuration, Use
          ``--include-locations'' or ``--exclude-locations'' flags to specify allowed
          list of locations or excluded list of locations. The following
          command updates storage intelligence configuration of sub-folder `123456` with the
          specified list of excluded locations.,\n
            $ {command} --sub-folder=123456 --exclude-locations=us-east1,us-west1

          The following command updates storage intelligence for the given project by
          inheriting existing storage intelligence configuration from the hierarchical parent
          resource.,\n
            $ {command} --project=my-project --inherit-from-parent

          To clear included locations from the project storage intelligence, Use the
          following command.,\n
            $ {command} --project=my-project --include-locations=

      """,
  }

  @classmethod
  def Args(cls, parser):
    parser.SetSortArgs(False)
    flags.add_storage_intelligence_configs_level_flags(parser)
    update_group = parser.add_group(
        category='UPDATE', mutex=True, required=True
    )
    update_group.add_argument(
        '--inherit-from-parent',
        action='store_true',
        help=(
            'Specifies storage intelligence config to be inherited from parent.'
        ),
    )
    settings = update_group.add_group(category='SETTINGS')
    flags.add_storage_intelligence_configs_settings_flags(settings)

  def Run(self, args):
    client = storage_intelligence_api.StorageIntelligenceApi()

    if args.project:
      intelligence_config = (
          client.update_project_intelligence_config(
              args.project,
              inherit_from_parent=args.inherit_from_parent,
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
          inherit_from_parent=args.inherit_from_parent,
          trial_edition=args.trial_edition,
          include_locations=args.include_locations,
          exclude_locations=args.exclude_locations,
          include_bucket_id_regexes=args.include_bucket_id_regexes,
          exclude_bucket_id_regexes=args.exclude_bucket_id_regexes,
      )
    else:
      intelligence_config = client.update_organization_intelligence_config(
          args.organization,
          inherit_from_parent=args.inherit_from_parent,
          trial_edition=args.trial_edition,
          include_locations=args.include_locations,
          exclude_locations=args.exclude_locations,
          include_bucket_id_regexes=args.include_bucket_id_regexes,
          exclude_bucket_id_regexes=args.exclude_bucket_id_regexes,
      )

    log.status.Print(
        'Successfully updated storage intelligence plan for {}.\n'.format(
            intelligence_config.name
        )
    )
    return intelligence_config
