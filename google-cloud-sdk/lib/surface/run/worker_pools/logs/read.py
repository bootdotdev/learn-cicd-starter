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
"""Command to read logs for a worker pool."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from googlecloudsdk.api_lib.logging import common
from googlecloudsdk.api_lib.logging import formatter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.logs import read as read_logs_lib
from googlecloudsdk.command_lib.run import flags
from googlecloudsdk.core import log

FormatLog = formatter.FormatLog


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Read(base.Command):
  """Read logs for a Cloud Run worker pool."""

  detailed_help = {
      'DESCRIPTION': """\
          {command} reads log entries. Log entries matching *--log-filter* are
          returned according to the specified --order.
          If the log entries come from multiple logs, then entries from
          different logs might be intermingled in the results.
          """,
      'EXAMPLES': """\
          To read log entries from for a Cloud Run Worker Pool, run:

            $ {command} my-worker-pool

          To read log entries with severity ERROR or higher, run:

            $ {command} my-worker-pool --log-filter="severity>=ERROR"

          To read log entries written in a specific time window, run:

            $ {command} my-worker-pool --log-filter='timestamp<="2015-05-31T23:59:59Z" AND timestamp>="2015-05-31T00:00:00Z"'

          To read up to 10 log entries in your worker pool payloads that include the
          word `SearchText` and format the output in `JSON` format, run:

            $ {command} my-worker-pool --log-filter="textPayload:SearchText" --limit=10 --format=json

          Detailed information about filters can be found at:
          [](https://cloud.google.com/logging/docs/view/advanced_filters)
          """,
  }

  @staticmethod
  def Args(parser):
    parser.add_argument('worker_pool', help='Name for a Cloud Run worker pool.')
    read_logs_lib.LogFilterArgs(parser)
    read_logs_lib.LoggingReadArgs(parser)

  def Run(self, args):
    filters = [args.log_filter] if args.IsSpecified('log_filter') else []
    filters.append('resource.type = %s \n' % 'cloud_run_worker_pool')
    filters.append(
        'resource.labels.worker_pool_name = %s \n' % args.worker_pool
    )
    filters.append(
        'resource.labels.location = %s \n' % flags.GetRegion(args, prompt=True)
    )
    filters.append('severity >= DEFAULT \n')
    filters += read_logs_lib.MakeTimestampFilters(args)

    lines = []

    logs = common.FetchLogs(
        read_logs_lib.JoinFilters(filters),
        order_by=args.order,
        limit=args.limit,
    )

    for log_line in logs:
      output_log = FormatLog(log_line)
      if output_log:
        lines.append(output_log)

    for line in reversed(lines):
      log.out.Print(line)
