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

"""Command for listing spokes."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.network_connectivity import networkconnectivity_api
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import parser_arguments
from googlecloudsdk.command_lib.network_connectivity import filter_rewrite
from googlecloudsdk.command_lib.network_connectivity import flags


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class QueryStatus(base.ListCommand):
  """Query the status of Private Service Connect propagation for a hub."""

  @staticmethod
  def Args(parser: parser_arguments.ArgumentInterceptor):
    # Remove URI flag to match surface spec
    base.URI_FLAG.RemoveFromParser(parser)
    flags.AddHubResourceArg(
        parser, """to query Private Service Connect propagation for"""
    )
    # TODO(b/347697136): remove list of values and instead link to documentation
    parser.add_argument(
        '--group-by',
        help="""
        Comma-separated list of resource field key names to group by. Aggregated
        values will be displayed for each group. If `--group-by` is set, the value
        of the `--sort-by` flag must be the same as or a subset of the `--group-by`
        flag.

        Accepted values are:
        - 'psc_propagation_status.source_spoke'
        - 'psc_propagation_status.source_group'
        - 'psc_propagation_status.source_forwarding_rule'
        - 'psc_propagation_status.target_spoke'
        - 'psc_propagation_status.target_group'
        - 'psc_propagation_status.code'
        """,
    )
    parser.display_info.AddFormat("""
      table(
        pscPropagationStatus.sourceForwardingRule.basename(),
        pscPropagationStatus.sourceSpoke.basename(),
        pscPropagationStatus.sourceGroup.basename(),
        pscPropagationStatus.targetSpoke.basename(),
        pscPropagationStatus.targetGroup.basename(),
        pscPropagationStatus.code:label=CODE,
        count)
        """)

  def Run(self, args):
    valid_fields = {
        'psc_propagation_status.source_spoke',
        'psc_propagation_status.source_group',
        'psc_propagation_status.source_forwarding_rule',
        'psc_propagation_status.target_spoke',
        'psc_propagation_status.target_group',
        'psc_propagation_status.code',
    }
    release_track = self.ReleaseTrack()
    client = networkconnectivity_api.HubsClient(release_track)
    hub_ref = args.CONCEPTS.hub.Parse()
    group_by_fields: list[str] = []
    if args.group_by:
      group_by_fields: list[str] = args.group_by.replace(' ', '').split(',')
      if not all((x in valid_fields) for x in group_by_fields):
        raise ValueError(
            'Invalid group-by fields: {} valid fields are:\n{}'.format(
                ', '.join(sorted((set(group_by_fields) - valid_fields))),
                '\n'.join(sorted(valid_fields)),
            )
        )

    filter_expression = ''
    # this extracts the filter expression from the args.filter string
    # then sets it to an empty string to bypass client-side filtering
    if args.filter:
      _, filter_expression = filter_rewrite.BackendFilterRewrite().Rewrite(
          args.filter
      )
    args.filter = ''

    sort_by_fields = []
    if args.sort_by:
      sort_by_fields: list[str] = args.sort_by
      if not all((x in valid_fields) for x in sort_by_fields):
        raise ValueError(
            'Invalid sort-by fields: {}, valid fields are:\n{}'.format(
                ', '.join(sorted((set(sort_by_fields) - valid_fields))),
                '\n'.join(sorted(valid_fields)),
            )
        )

    limit = 5000
    if args.limit:
      limit = args.limit

    page_size = 100
    if args.page_size:
      page_size = args.page_size

    return client.QueryHubStatus(
        hub_ref,
        filter_expression=filter_expression,
        group_by=','.join(group_by_fields),
        order_by=','.join(sort_by_fields),
        page_size=page_size,
        limit=limit,
    )


QueryStatus.detailed_help = {
    'EXAMPLES': """ \
  To query the Private Service Connect propagation status of a hub, run:

        $ {command} HUB

  To query the Private Service Connect propagation status of a hub grouped by source spoke and code, run:

        $ {command} HUB --group-by="psc_propagation_status.source_spoke,psc_propagation_status.code"

  To query the Private Service Connect propagation status of a hub sorted by the source forwarding rule, run:

        $ {command} HUB --sort-by="psc_propagation_status.source_forwarding_rule"

  """,
    'API REFERENCE': """ \
  This command uses the networkconnectivity/v1 API. The full documentation
  for this API can be found at:
  https://cloud.google.com/network-connectivity/docs/reference/networkconnectivity/rest
  """,
}
