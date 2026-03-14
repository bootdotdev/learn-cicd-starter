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
"""Command to fetch data source references for a resource type."""

from googlecloudsdk.api_lib.backupdr import data_source_references
from googlecloudsdk.api_lib.util import common_args
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.backupdr import flags
from googlecloudsdk.core import log


DataSourceReferencesClient = data_source_references.DataSourceReferencesClient


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
class FetchForResourceType(base.ListCommand):
  """Fetch Data Source References for a given resource type and location."""

  detailed_help = {
      'BRIEF': (
          'List data source references in a specified location and resource'
          ' type in a project.'
      ),
      'DESCRIPTION': (
          '{description} Show all configuration data associated with the'
          ' specified data source reference.'
      ),
      'EXAMPLES': """\
        To list data source references for Cloud SQL with location `us-central1` in project `test-project`, run:

          $ {command} sqladmin.googleapis.com/Instance --location="us-central1" --project="test-project"
        """,
  }

  DEFAULT_LIST_FORMAT = """
    table(
        name.basename():label=NAME,
        dataSourceGcpResourceInfo.type:label=RESOURCE_TYPE,
        dataSourceGcpResourceInfo.gcpResourcename:label=RESOURCE_NAME,
        dataSource:label=DATA_SOURCE,
        dataSourceBackupConfigState:label=BACKUP_CONFIG_STATE,
        dataSourceGcpResourceInfo.location:label=LOCATION
        )
        """

  @staticmethod
  def Args(parser):
    """Specifies additional command flags.

    Args:
      parser: argparse.Parser: Parser object for command line inputs.
    """
    parser.add_argument(
        '--location',
        required=True,
        help='Location for which data source references should be fetched.',
    )
    parser.add_argument(
        'resource_type',
        help=(
            'Resource type for which data source references should be fetched.'
        ),
    )
    flags.AddOutputFormat(parser, FetchForResourceType.DEFAULT_LIST_FORMAT)

  def _Validate_and_Parse_SortBy(self, args):
    """Validates and parses the sort_by argument.

    Args:
      args: The arguments that were provided to the command.

    Returns:
      The parsed order_by string, or None if no sort_by argument was provided.

    Raises:
      exceptions.InvalidArgumentException: If the sort_by argument is invalid.
    """
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
          'Invalid sort_by argument. Only sort_by name/Name is supported.',
      )
    order_by_fields[0] = 'name'
    order_by = ' '.join(order_by_fields)
    return order_by

  def Run(self, args):
    """Run the command.

    Args:
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the Args method.

    Returns:
      List of data source references.

    Raises:
      exceptions.Error: If the API call fails.
    """
    location = args.location
    resource_type = args.resource_type
    try:
      client = DataSourceReferencesClient()
      result = client.FetchForResourceType(
          location,
          resource_type,
          filter_expression=args.filter,
          page_size=args.page_size,
          order_by=self._Validate_and_Parse_SortBy(args),
      )
      if result and result.dataSourceReferences:
        data_source_refs = result.dataSourceReferences
        return data_source_refs
      return []  # Return an empty list
    except Exception as e:  # pylint: disable=broad-except
      log.error(f'Error fetching data source references: {e}')
      raise  # Raise the exception
