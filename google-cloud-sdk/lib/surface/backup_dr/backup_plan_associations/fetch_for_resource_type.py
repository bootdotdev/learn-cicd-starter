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
"""Command to fetch backup plan associations for a resource type."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.backupdr import backup_plan_associations
from googlecloudsdk.api_lib.util import common_args
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.backupdr import flags
from googlecloudsdk.core import log


BackupPlanAssociationsClient = (
    backup_plan_associations.BackupPlanAssociationsClient
)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
class FetchForResourceType(base.ListCommand):
  """Fetch Backup Plan Associations for a given resource type and location."""

  detailed_help = {
      'BRIEF': (
          'List backup plan associations in a specified location'
          ' and resource type in a project.'
      ),
      'DESCRIPTION': (
          '{description} List backup plan associations in a specified location'
          ' and resource type in a project.'
      ),
      'EXAMPLES': """\
        To list backup plan associations for Cloud SQL with location `us-central1`, run:

          $ {command} sqladmin.googleapis.com/Instance --location="us-central1"
        """,
  }

  DEFAULT_LIST_FORMAT = """
    table(
        name.basename():label=NAME,
        resource:label=RESOURCE,
        resourceType:label=RESOURCE_TYPE,
        backupPlan:label=BACKUP_PLAN,
        state:label=STATE
        )
        """

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--location',
        required=True,
        help='Location for which backup plan associations should be fetched.',
    )
    parser.add_argument(
        'resource_type',
        help=(
            'Resource type for which backup plan associations should be'
            ' fetched.'
        ),
    )
    flags.AddOutputFormat(parser, FetchForResourceType.DEFAULT_LIST_FORMAT)

  def _Validate_and_Parse_SortBy(self, args):
    order_by = common_args.ParseSortByArg(args.sort_by)
    # Only sort by name is supported by CLH right now.
    if order_by is None:
      return None
    order_by_fields = order_by.split(' ')
    if (
        order_by_fields
        and isinstance(order_by_fields[0], str)
        and order_by_fields[0]
        not in ('name', 'Name')
    ):
      raise exceptions.InvalidArgumentException(
          'sort_by',
          'Invalid sort_by argument. Only sort_by'
          ' name/Name is'
          ' supported.',
      )
    order_by_fields[0] = 'name'
    order_by = ' '.join(order_by_fields)
    return order_by

  def Run(self, args):
    """Run the command."""
    location = args.location
    resource_type = args.resource_type
    try:
      client = BackupPlanAssociationsClient()
      result = client.FetchForResourceType(
          location,
          resource_type,
          filter_expression=args.filter,
          page_size=args.page_size,
          order_by=self._Validate_and_Parse_SortBy(args),
      )
      if result and result.backupPlanAssociations:
        return result.backupPlanAssociations  # Return the list directly
      else:
        return []  # Return an empty list
    except Exception as e:  # pylint: disable=broad-except
      log.error(f'Error fetching backup plan associations : {e}')
      raise e  # Raise the exception
