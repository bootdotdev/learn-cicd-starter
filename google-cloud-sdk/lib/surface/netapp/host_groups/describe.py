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
"""Describe a Cloud NetApp Host Group."""

from googlecloudsdk.api_lib.netapp.host_groups import client as host_groups_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp import flags
from googlecloudsdk.command_lib.util.concepts import concept_parsers


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.Hidden
class Describe(base.DescribeCommand):
  """Describe a Cloud NetApp Host Group."""

  detailed_help = {
      'DESCRIPTION': """\
          Describe a Cloud NetApp Host Group.
          """,
      'EXAMPLES': """\
          The following command describes a Host Group named NAME in the given location:

              $ {command} NAME --location=us-central1
          """,
  }

  @staticmethod
  def Args(parser):
    concept_parsers.ConceptParser(
        [flags.GetHostGroupPresentationSpec('The Host Group to describe.')]
    ).AddToParser(parser)

  def Run(self, args):
    """Get a Cloud NetApp Host Group in the current project."""
    host_group_ref = args.CONCEPTS.host_group.Parse()

    client = host_groups_client.HostGroupsClient(
        release_track=self.ReleaseTrack()
    )
    return client.GetHostGroup(host_group_ref)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.Hidden
class DescribeBeta(Describe):
  """Describe a Cloud NetApp Host Group."""

  _RELEASE_TRACK = base.ReleaseTrack.BETA


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.Hidden
class DescribeAlpha(DescribeBeta):
  """Describe a Cloud NetApp Host Group."""

  _RELEASE_TRACK = base.ReleaseTrack.ALPHA
