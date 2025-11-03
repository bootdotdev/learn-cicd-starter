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
"""Surface for listing alerts."""

from googlecloudsdk.api_lib.monitoring import alerts
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.monitoring import resource_args


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class List(base.ListCommand):
  """List alerts."""

  CLIENT_SIDE_FILTERS = False

  detailed_help = {
      'API REFERENCE': """\
          This command uses the monitoring/v3 API. The full documentation for this
          API can be found at: https://cloud.google.com/monitoring/api/""",
      'DESCRIPTION': 'List alerts for a project.',
      'EXAMPLES': """\
      To list all open alerts:

        $ {command} --filter="state='OPEN'"

      To order alerts by when the alert was opened:

        $ {command} --sort-by=openTime

      To order alerts by when the alert was opened in reverse order:

        $ {command} --sort-by="~openTime"

      To list alerts for a specific policy:

        $ {command} --filter="policy.displayName='My Policy'"

      More information can be found at
      https://cloud.google.com/sdk/gcloud/reference/topic/filters""",
  }

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    resource_args.AddProjectResourceArg(parser, 'list alerts from', True)
    # Provide the resource spec to the base class to potentially help with
    # filter handling.
    super(List, List).Args(parser)

    base.PAGE_SIZE_FLAG.SetDefault(parser, 1000)
    parser.display_info.AddFormat('yaml')
    parser.display_info.AddUriFunc(resource_args.GetAlertResourceUriFunc())

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      The list of alerts.
    """
    project_ref = args.CONCEPTS.project.Parse()
    client = alerts.AlertsClient()

    order_by_string = ','.join(args.sort_by) if args.sort_by else None

    # Pass the filter and order_by to the API client
    response = client.List(
        project_ref,
        a_filter=args.filter,
        order_by=order_by_string,
        page_size=args.page_size,
    )
    return response.alerts
