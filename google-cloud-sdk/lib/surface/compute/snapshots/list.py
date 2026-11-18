# -*- coding: utf-8 -*- #
# Copyright 2014 Google LLC. All Rights Reserved.
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
"""Command for listing snapshots."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import lister
from googlecloudsdk.calliope import base


def _GAArgs(parser):
  """Set Args for GA."""
  parser.display_info.AddFormat("""\
      table(
        name,
        diskSizeGb,
        sourceDisk.scope():label=SRC_DISK,
        status
      )""")
  lister.AddBaseListerArgs(parser)


def _BetaArgs(parser):
  """Set Args based on Release Track."""
  parser.display_info.AddFormat("""\
      table(
        name,
        location().yesno(no="GLOBAL"):label=LOCATION,
        diskSizeGb,
        sourceDisk.scope():label=SRC_DISK,
        status
      )""")
  lister.AddMultiScopeListerFlags(parser, global_=True, regional=True)


def _AlphaArgs(parser):
  """Set Args based on Release Track."""
  parser.display_info.AddFormat("""\
      table(
        name,
        location().yesno(no="GLOBAL"):label=LOCATION,
        diskSizeGb,
        sourceDisk.scope():label=SRC_DISK,
        status
      )""")
  lister.AddMultiScopeListerFlags(parser, global_=True, regional=True)


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.UniverseCompatible
class List(base.ListCommand):
  """List Compute Engine snapshots."""

  @staticmethod
  def Args(parser):
    _GAArgs(parser)

  def Run(self, args):
    return self._Run(args)

  def _Run(self, args, support_region=False):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    if support_region:
      request_data = lister.ParseMultiScopeFlags(args, holder.resources)

      list_implementation = lister.MultiScopeLister(
          client,
          global_service=client.apitools_client.snapshots,
          regional_service=client.apitools_client.regionSnapshots,
          aggregation_service=client.apitools_client.snapshots,
      )

      return lister.Invoke(request_data, list_implementation)
    else:
      request_data = lister.ParseNamesAndRegexpFlags(args, holder.resources)

      list_implementation = lister.GlobalLister(
          client, client.apitools_client.snapshots
      )

      return lister.Invoke(request_data, list_implementation)


List.detailed_help = base_classes.GetGlobalListerHelp('snapshots')


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class ListBeta(List):
  """List Compute Engine snapshots."""

  @classmethod
  def Args(cls, parser):
    _BetaArgs(parser)

  def Run(self, args):
    return self._Run(args, support_region=True)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class ListAlpha(List):
  """List Compute Engine snapshots."""

  @classmethod
  def Args(cls, parser):
    _AlphaArgs(parser)

  def Run(self, args):
    return self._Run(args, support_region=True)
