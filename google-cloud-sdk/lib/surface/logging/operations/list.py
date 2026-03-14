# -*- coding: utf-8 -*- #
# Copyright 2021 Google LLC. All Rights Reserved.
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
"""'logging operations list' command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.logging import util
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.core import log
from googlecloudsdk.core.resource import resource_projector


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.GA, base.ReleaseTrack.BETA, base.ReleaseTrack.ALPHA
)
class List(base.ListCommand):
  """List long running operations."""

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    parser.add_argument(
        '--location', required=True, help='Location of the operations.')
    parser.add_argument(
        '--operation-filter',
        required=True,
        help=arg_parsers.UniverseHelpText(
            default=(
                'Filter expression that specifies the operations to return.'
            ),
            universe_help='Not all operation types are supported.\n',
        ),
    )
    parser.add_argument(
        '--page-token',
        type=str,
        help=(
            'The next_page_token value returned from a previous List request,'
            ' if any.'
        ),
    )
    base.URI_FLAG.RemoveFromParser(parser)
    base.FILTER_FLAG.RemoveFromParser(parser)

    util.AddParentArgs(parser, 'operations to list')

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Yields:
      A list of operations.
    """
    operation_name = util.CreateResourceName(
        util.GetParentFromArgs(args), 'locations', args.location)

    request = util.GetMessages().LoggingProjectsLocationsOperationsListRequest(
        name=operation_name,
        filter=args.operation_filter,
        pageSize=args.page_size,
        pageToken=args.page_token,
    )

    result = util.GetClient().projects_locations_operations.List(request)
    self._cancellation_requested = False
    for operation in result.operations:
      yield operation
      if not self._cancellation_requested:
        serialize_op = resource_projector.MakeSerializable(operation)
        self._cancellation_requested = serialize_op.get('metadata', {}).get(
            'cancellationRequested', '')
    if result.nextPageToken:
      yield result.nextPageToken

  def Epilog(self, resources_were_displayed):
    if self._cancellation_requested:
      log.status.Print(
          'Note: Cancellation happens asynchronously. It may take up to 10 '
          "minutes for the operation's status to change to cancelled.")


List.detailed_help = {
    'DESCRIPTION': """
        Return a list of long running operations in the given LOCATION. The
        operations were scheduled by other gcloud commands.

        For example, a CopyLogEntries operation may be scheduled by the command:
        `gcloud logging copy BUCKET_ID DESTINATION --location=LOCATION`.

        The `--operation-filter` flag is required and must specify the
        `request_type`. Supported request types include but are not limited to:
        `CopyLogEntries`, `CreateBucket` and `UpdateBucket`.

        Additional supported filter expressions include: `operation_start_time`,
        `operation_finish_time` and `operation_state`. These can be combined
        with the case-sensitive keyword `AND` between them.

        For `operation_start_time` and `operation_end_time`, the operators >=,
        >, <=, and < are supported.

        Timestamps must be in either RFC3339 or ISO8601 formats. If the
        timestamp contains a time value, then it must be quoted. For examples:
        "YYYY-MM-DDTHH:MM:SSZ", "YYYY-MM-DDTHH:MM:SS.mmmZ", "YY-MM-DD",
        "YYYY-MM-DDTHH:MM:SS-0000", "YYYY-MM-DDTHH:MM+0000", "YYYY-MM-DD",
        YYYY-MM-DD, YY-MM-DD, etc.

        The `operation_state` filter expression can be used to filter for
        operations that are in a specific state. The value can be one of the
        following: `SCHEDULED`, `WAITING_FOR_PRECONDITIONS`, `RUNNING`,
        `SUCCESS`, `FAILURE`, `CANCELLED`, `PENDING`.

        For `operation_state`, the operators = and != are supported.

        Other filter options are not supported.
        """,
    'EXAMPLES': """\
        To list CopyLogEntries operations, run:

            $ {command} --location=LOCATION --operation-filter='request_type=CopyLogEntries'

        To list CopyLogEntries operations that started after a specified time, run:

            $ {command} --location=LOCATION --operation-filter='request_type=CopyLogEntries AND operation_start_time>="2023-11-20T00:00:00Z"'

        To list CopyLogEntries operations that finished before a specified time, run:

            $ {command} --location=LOCATION --operation-filter='request_type=CopyLogEntries AND operation_finish_time<="2023-11-20T00:00:00Z"'

        To list CopyLogEntries operations that completed successfully, run:

            $ {command} --location=LOCATION --operation-filter='request_type=CopyLogEntries AND operation_state=SUCCESS'

        To list CopyLogEntries operations that have not failed, run:

            $ {command} --location=LOCATION --operation-filter='request_type=CopyLogEntries AND operation_state!=FAILURE'
        """,
}
