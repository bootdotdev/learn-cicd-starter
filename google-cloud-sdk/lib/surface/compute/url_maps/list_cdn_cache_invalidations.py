# -*- coding: utf-8 -*- #
# Copyright 2016 Google LLC. All Rights Reserved.
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
"""Command for listing Cloud CDN cache invalidations."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import constants
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import exceptions as compute_exceptions
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.url_maps import flags
from googlecloudsdk.command_lib.compute.url_maps import url_maps_utils
from googlecloudsdk.core import properties
from googlecloudsdk.core.resource import resource_projector


def _DetailedHelp():
  return {
      'brief':
          'List Cloud CDN cache invalidations for a URL map.',
      'DESCRIPTION':
          """\
      List Cloud CDN cache invalidations for a URL map. A cache invalidation
      instructs Cloud CDN to stop using cached content. You can list
      invalidations to check which have completed.
      """,
  }


def _GetUrlMapGetRequest(url_map_ref, client):
  return (client.apitools_client.urlMaps, 'Get',
          client.messages.ComputeUrlMapsGetRequest(
              project=properties.VALUES.core.project.GetOrFail(),
              urlMap=url_map_ref.Name()))


def _Run(args, holder, url_map_arg):
  """Issues requests necessary to list URL map cdn cache invalidations."""
  client = holder.client

  url_map_ref = url_map_arg.ResolveAsResource(
      args, holder.resources, default_scope=compute_scope.ScopeEnum.GLOBAL)
  if url_maps_utils.IsRegionalUrlMapRef(url_map_ref):
    raise compute_exceptions.ArgumentError(
        'Invalid flag [--region]:'
        ' Regional URL maps do not support Cloud CDN caching.'
    )

  get_request = _GetUrlMapGetRequest(url_map_ref, client)

  objects = client.MakeRequests([get_request])
  urlmap_id = objects[0].id
  filter_expr = ('(operationType eq invalidateCache) (targetId eq '
                 '{urlmap_id})').format(urlmap_id=urlmap_id)
  max_results = args.limit or constants.MAX_RESULTS_PER_PAGE
  project = properties.VALUES.core.project.GetOrFail()
  requests = [
      (client.apitools_client.globalOperations, 'AggregatedList',
       client.apitools_client.globalOperations.GetRequestType('AggregatedList')(
           filter=filter_expr,
           maxResults=max_results,
           orderBy='creationTimestamp desc',
           project=project))
  ]
  return resource_projector.MakeSerializable(
      client.MakeRequests(requests=requests))


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class ListCacheInvalidations(base.ListCommand):
  """List Cloud CDN cache invalidations for a URL map."""

  detailed_help = _DetailedHelp()

  @staticmethod
  def _Flags(parser):
    parser.add_argument(
        '--limit',
        type=arg_parsers.BoundedInt(1, 1000, unlimited=False),
        help=(
            'The maximum number of invalidations to list. This has an upper'
            ' limit of 1000. For more results, use Cloud Logging.'
        ),
    )

  @classmethod
  def Args(cls, parser):
    cls.URL_MAP_ARG = flags.GlobalUrlMapArgument()
    cls.URL_MAP_ARG.AddArgument(parser, operation_type='describe')
    parser.display_info.AddFormat("""\
        table(
          description,
          operation_http_status():label=HTTP_STATUS,
          status,
          insertTime:label=TIMESTAMP
        )""")

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    return _Run(args, holder, self.URL_MAP_ARG)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class ListCacheInvalidationsBeta(ListCacheInvalidations):
  pass


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class ListCacheInvalidationsAlpha(ListCacheInvalidationsBeta):
  pass
