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
"""Command to fetch backups for a resource type."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.backupdr import backups
from googlecloudsdk.api_lib.util import common_args
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.backupdr import flags
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.core import log


BackupsClient = (
    backups.BackupsClient
)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.Hidden
class FetchForResourceType(base.ListCommand):
  """Fetch Backups for a given resource type and location."""

  detailed_help = {
      'BRIEF': (
          'List backups in a specified location'
          ' and resource type in a project.'
      ),
      'DESCRIPTION': (
          '{description} List backups for the specified resource type for a '
          'data source.'
      ),
      'EXAMPLES': """\
        To list backups for Cloud SQL instance resources for data source `my-data-source` with location `us-central1` under backup vault, `my-vault`.

          $ {command} sqladmin.googleapis.com/Instance --data-source=my-data-source --backup-vault=my-vault --location=us-central1
        """,
  }

  DEFAULT_LIST_FORMAT = """
    table(
        name.basename():label=NAME,
        description:label=DESCRIPTION,
        createTime:label=CREATE_TIME,
        enforcedRetentionEndTime:label=ENFORCED_RETENTION_END_TIME,
        state:label=STATE,
        backupType:label=BACKUP_TYPE,
        expireTime:label=EXPIRE_TIME,
        resourceSizeBytes:label=RESOURCE_SIZE_BYTES
        )
        """

  @staticmethod
  def Args(parser):
    parser.add_argument(
        'resource_type',
        help=(
            'Resource type for which backup plan associations should be'
            ' fetched.'
        ),
    )
    concept_parsers.ConceptParser.ForResource(
        '--data-source',
        flags.GetDataSourceResourceSpec(),
        'Data source for which backups should be fetched.',
        required=True).AddToParser(parser)
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
    resource_type = args.resource_type
    data_source_ref = args.CONCEPTS.data_source.Parse()
    try:
      client = BackupsClient()
      result = client.FetchForResourceType(
          data_source_ref,
          resource_type,
          filter_expression=args.filter,
          page_size=args.page_size,
          order_by=self._Validate_and_Parse_SortBy(args),
      )
      if result and result.backups:
        return result.backups  # Return the list directly
      else:
        return []  # Return an empty list
    except Exception as e:  # pylint: disable=broad-except
      log.error(f'Error fetching backups : {e}')
      raise e  # Raise the exception
