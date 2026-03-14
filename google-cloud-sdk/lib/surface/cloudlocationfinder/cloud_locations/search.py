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
"""CloudLocation search command."""

from apitools.base.py import list_pager
from googlecloudsdk.api_lib.util import apis as core_apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.cloudlocationfinder import flags


@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class Search(base.Command):
  """Search cloudLocations.

  ## EXAMPLES

  To search all cloudLocations for `projects/my-project-id`, run:

    $ {command} --project=my-project-id
  """

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    flags.AddSearchFlags(parser)

  def Run(self, args):
    """Run command.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      Search CloudLocations.
    """
    if self.ReleaseTrack() == base.ReleaseTrack.GA:
      api_version = 'v1'
    else:
      api_version = 'v1alpha'
    client = core_apis.GetClientInstance('cloudlocationfinder', api_version)
    messages = core_apis.GetMessagesModule('cloudlocationfinder', api_version)
    cloud_locations_service = client.projects_locations_cloudLocations
    location = args.CONCEPTS.location.Parse().RelativeName()
    source_cloud_location = (
        args.CONCEPTS.source_cloud_location.Parse().RelativeName()
    )
    request = messages.CloudlocationfinderProjectsLocationsCloudLocationsSearchRequest(
        parent=location,
        pageSize=args.page_size,
        sourceCloudLocation=source_cloud_location,
        query=args.query,
    )
    args.query = ''
    args.order_by = ''
    return list_pager.YieldFromList(
        cloud_locations_service,
        request,
        method='Search',
        field='cloudLocations',
        limit=args.limit if not args.query else None,
        batch_size_attribute='pageSize',
    )


Search.detailed_help = {
    'DESCRIPTION': """
        Search Cloudlocations.
    """,
    'EXAMPLES': """
    To search CloudLocations, run:

        $ {command} --source-cloud-location=aws-us-east-1 --query=display_name=\"us-east4\"
    """,
}
