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
"""Command to list locations in the Project."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.apphub import locations as apis
from googlecloudsdk.api_lib.apphub import utils as api_lib_utils
from googlecloudsdk.calliope import base


_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To list all apphub locations, run:

          $ {command}
        """,
}

_FORMAT = """
  table(
    name.scope("locations"):label=ID
  )
"""


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.UniverseCompatible
class ListGA(base.ListCommand):
  """List Apphub locations."""

  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    parser.display_info.AddFormat(_FORMAT)
    parser.display_info.AddUriFunc(
        api_lib_utils.MakeGetUriFunc(
            'apphub.projects.locations',
            release_track=base.ReleaseTrack.GA,
        )
    )

  def Run(self, args):
    """Run the list command."""
    client = apis.LocationsClient(release_track=base.ReleaseTrack.GA)
    project_ref = api_lib_utils.GetProjectRef()
    return client.List(
        limit=args.limit,
        page_size=args.page_size,
        parent=project_ref.RelativeName(),
    )


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class ListAlpha(base.ListCommand):
  """List Apphub locations."""

  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    parser.display_info.AddFormat(_FORMAT)
    parser.display_info.AddUriFunc(
        api_lib_utils.MakeGetUriFunc(
            'apphub.projects.locations',
            release_track=base.ReleaseTrack.ALPHA,
        )
    )

  def Run(self, args):
    """Run the list command."""
    client = apis.LocationsClient(release_track=base.ReleaseTrack.ALPHA)
    project_ref = api_lib_utils.GetProjectRef()
    return client.List(
        limit=args.limit,
        page_size=args.page_size,
        parent=project_ref.RelativeName(),
    )
