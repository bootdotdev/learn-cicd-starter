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
"""Implementation of update command for updating management hub."""

from googlecloudsdk.api_lib.storage import management_hub_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage import flags
from googlecloudsdk.core import log


# TODO: b/369949089 - Remove default universe flag after checking the
# availability of management hub in different universes.
@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Update(base.Command):
  """Updates Management Hub."""

  detailed_help = {
      'DESCRIPTION': """
          Update management hub plan for the organization, sub-folder
           or project.
      """,
      'EXAMPLES': """
          To limit buckets in the management hub plan, Use the following
          command with ``--include-bucket-ids'' and ``--include-bucket-regexes'' flags
          to specify list of bucket ids and bucket id regexes.,\n
            ${command} --organization=my-org --include-bucket-ids=my-bucket --include-bucket-regexes=my-bucket-.*

          To apply location based filters in the management hub plan, Use
          ``--include-locations'' or ``--exclude-locations'' flags to specify allowed
          list of locations or excluded list of locations. The following
          command updates management hub plan of sub-folder `123456` with the
          specified list of excluded locations.,\n
            ${command} --sub-folder=123456 --exclude-locations=us-east1,us-west1

          The following command updates management hub for the given project by
          inheriting existing management hub plan from the hierarchical parent
          resource.,\n
            ${command} --project=my-project --inherit-from-parent

          To clear included locations from the project management hub, Use the
          following command.,\n
            ${command} --project=my-project --include-locations=

          To clear excluded bucket ids from the project management hub and to
          replace existing excluded bucket ids regexes, Use the following
          command.,\n
            ${command} --project=my-project --exclude-bucket-id-regexes="test1*","test2*" --exclude-bucket-ids=""

          Alternatively, use the following command to do same operation since
          the absense of cloud storage bucket filter flags will be considered
          as empty list,\n
            ${command} --project=my-project --exclude-bucket-id-regexes="test1*","test2*"
      """,
  }

  @classmethod
  def Args(cls, parser):
    parser.SetSortArgs(False)
    flags.add_management_hub_level_flags(parser)
    update_group = parser.add_group(
        category='UPDATE', mutex=True, required=True
    )
    update_group.add_argument(
        '--inherit-from-parent',
        action='store_true',
        help='Specifies management hub config to be inherited from parent.',
    )
    filters = update_group.add_group(category='FILTER')
    flags.add_management_hub_filter_flags(filters)

  def Run(self, args):

    if args.project:
      management_hub = (
          management_hub_api.ManagementHubApi().update_project_management_hub(
              args.project,
              inherit_from_parent=args.inherit_from_parent,
              include_locations=args.include_locations,
              exclude_locations=args.exclude_locations,
              include_bucket_ids=args.include_bucket_ids,
              exclude_bucket_ids=args.exclude_bucket_ids,
              include_bucket_id_regexes=args.include_bucket_id_regexes,
              exclude_bucket_id_regexes=args.exclude_bucket_id_regexes,
          )
      )
    elif args.sub_folder:
      management_hub = (
          management_hub_api.ManagementHubApi().update_sub_folder_management_hub(
              args.sub_folder,
              inherit_from_parent=args.inherit_from_parent,
              include_locations=args.include_locations,
              exclude_locations=args.exclude_locations,
              include_bucket_ids=args.include_bucket_ids,
              exclude_bucket_ids=args.exclude_bucket_ids,
              include_bucket_id_regexes=args.include_bucket_id_regexes,
              exclude_bucket_id_regexes=args.exclude_bucket_id_regexes,
          )
      )
    else:
      management_hub = (
          management_hub_api.ManagementHubApi().update_organization_management_hub(
              args.organization,
              inherit_from_parent=args.inherit_from_parent,
              include_locations=args.include_locations,
              exclude_locations=args.exclude_locations,
              include_bucket_ids=args.include_bucket_ids,
              exclude_bucket_ids=args.exclude_bucket_ids,
              include_bucket_id_regexes=args.include_bucket_id_regexes,
              exclude_bucket_id_regexes=args.exclude_bucket_id_regexes,
          )
      )

    log.status.Print(
        'Successfully updated management hub plan for {}.\n'.format(
            management_hub.name
        )
    )
    return management_hub
