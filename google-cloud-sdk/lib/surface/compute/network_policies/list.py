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
"""Command for listing network policies."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import itertools

from apitools.base.py import list_pager
from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import lister
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.network_policies import flags
from googlecloudsdk.core import properties


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class List(base.ListCommand):
  """List Compute Engine network policies.

  *{command}* is used to list network policies. A network policy is a set of
  rules that controls network traffic classification.
  """

  @classmethod
  def Args(cls, parser):
    parser.display_info.AddFormat("""\
      table(
        name,
        region.basename(),
        description
      )
      """)
    lister.AddRegionsArgWithoutBaseArgs(parser)
    parser.display_info.AddCacheUpdater(flags.NetworkPoliciesCompleter)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client.apitools_client
    messages = client.MESSAGES_MODULE

    if args.project:
      project = args.project
    else:
      project = properties.VALUES.core.project.GetOrFail()

    # List RNPs in given regions
    if args.regions:
      regional_generators = [
          list_pager.YieldFromList(
              client.regionNetworkPolicies,
              messages.ComputeRegionNetworkPoliciesListRequest(
                  project=project, region=region.strip()
              ),
              field='items',
              limit=args.limit,
              batch_size=None,
          )
          for region in args.regions
      ]
      return itertools.chain.from_iterable(regional_generators)

    # Aggregated network policies for all regions defined in project
    request = messages.ComputeRegionNetworkPoliciesAggregatedListRequest(
        project=project, returnPartialSuccess=True
    )

    network_policies, next_page_token = _GetListPage(client, request)
    while next_page_token:
      request.pageToken = next_page_token
      list_page, next_page_token = _GetListPage(client, request)
      network_policies += list_page

    return network_policies


def _GetListPage(client, request):
  response = client.regionNetworkPolicies.AggregatedList(request)
  network_policy_chain = itertools.chain.from_iterable(
      network_policy_in_scope.value.networkPolicies
      for network_policy_in_scope in response.items.additionalProperties
  )
  return list(network_policy_chain), response.nextPageToken


List.detailed_help = {
    'EXAMPLES': """\
    To list regional network policies under project ``my-project'',
    specify a list of regions with ``--regions'':

      $ {command} --project=my-project --regions="region-a, region-b"

    To list all network policies under project
    ``my-project'', omit ``--regions'':

      $ {command} --project=my-project
    """,
}
