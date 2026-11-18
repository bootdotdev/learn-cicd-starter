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

"""List Cloud NetApp Host Groups."""

from googlecloudsdk.api_lib.netapp.host_groups import client as host_groups_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp import flags
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.core import properties


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.Hidden
class List(base.ListCommand):
  """List Cloud NetApp Host Groups."""

  _RELEASE_TRACK = base.ReleaseTrack.GA

  detailed_help = {
      'DESCRIPTION': """\
          Lists Cloud NetApp Host Groups.
          """,
      'EXAMPLES': """\
          The following command lists all Host Groups in the given location:

              $ {command} --location=us-central1
          """,
  }

  @staticmethod
  def Args(parser):
    concept_parsers.ConceptParser([
        flags.GetResourceListingLocationPresentationSpec(
            'The location in which to list Host Groups.'
        )
    ]).AddToParser(parser)

  def Run(self, args):
    """Run the list command."""
    # Ensure that project is set before parsing location resource.
    properties.VALUES.core.project.GetOrFail()

    location_ref = args.CONCEPTS.location.Parse().RelativeName()
    client = host_groups_client.HostGroupsClient(
        release_track=self._RELEASE_TRACK
    )
    return client.ListHostGroups(location_ref)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.Hidden
class ListBeta(List):
  """List Cloud NetApp Host Groups."""

  _RELEASE_TRACK = base.ReleaseTrack.BETA


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.Hidden
class ListAlpha(ListBeta):
  """List Cloud NetApp Host Groups."""

  _RELEASE_TRACK = base.ReleaseTrack.ALPHA
