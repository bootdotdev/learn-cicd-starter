# -*- coding: utf-8 -*- #
# Copyright 2015 Google LLC. All Rights Reserved.
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
"""Command for listing backend buckets."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import lister
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import completers
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.backend_buckets import flags


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.UniverseCompatible
class List(base.ListCommand):
  """List backend buckets."""

  _support_regional_global_flags = False

  @classmethod
  def Args(cls, parser):
    if cls._support_regional_global_flags:
      List.detailed_help = base_classes.GetGlobalRegionalListerHelp(
          'backend buckets'
      )

    parser.display_info.AddFormat(flags.DEFAULT_LIST_FORMAT)
    if cls._support_regional_global_flags:
      lister.AddMultiScopeListerFlags(
          parser, zonal=False, regional=True, global_=True
      )
    else:
      lister.AddBaseListerArgs(parser)
    parser.display_info.AddCacheUpdater(completers.InstancesCompleter)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    if self._support_regional_global_flags:
      request_data = lister.ParseMultiScopeFlags(
          args,
          holder.resources,
          default_scope_set=compute_scope.ScopeEnum.GLOBAL,
      )
      list_implementation = lister.MultiScopeLister(
          client,
          regional_service=client.apitools_client.regionBackendBuckets,
          global_service=client.apitools_client.backendBuckets,
      )
    else:
      request_data = lister.ParseNamesAndRegexpFlags(args, holder.resources)
      list_implementation = lister.GlobalLister(
          client, client.apitools_client.backendBuckets
      )

    return lister.Invoke(request_data, list_implementation)


List.detailed_help = base_classes.GetGlobalListerHelp('backend buckets')


@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.UniverseCompatible
class ListBeta(List):
  """List backend buckets."""

  _support_regional_global_flags = False


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class ListAlpha(ListBeta):
  """List backend buckets."""

  _support_regional_global_flags = True
