# -*- coding: utf-8 -*- #
# Copyright 2020 Google LLC. All Rights Reserved.
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
"""recommender API recommendations list command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import itertools

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.asset import client_util
from googlecloudsdk.api_lib.recommender import locations
from googlecloudsdk.api_lib.recommender import recommendation
from googlecloudsdk.api_lib.recommender import recommenders
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.recommender import flags
from googlecloudsdk.command_lib.run import exceptions
from googlecloudsdk.core import log


DETAILED_HELP = {
    'EXAMPLES':
        """
          Lists recommendations for a Cloud project.
            $ {command} --project=project-id --location=global --recommender=google.compute.instance.MachineTypeRecommender
        """,
}

DISPLAY_FORMAT = """
        table(
          name.basename(): label=RECOMMENDATION_ID,
          primaryImpact.category: label=PRIMARY_IMPACT_CATEGORY,
          stateInfo.state: label=RECOMMENDATION_STATE,
          lastRefreshTime: label=LAST_REFRESH_TIME,
          priority: label=PRIORITY,
          recommenderSubtype: label=RECOMMENDER_SUBTYPE,
          description: label=DESCRIPTION
        )
    """


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class List(base.ListCommand):
  r"""List recommendations for Google Cloud resources.

  This command lists all recommendations for the specified Google Cloud
  resource, location, and recommender. If a recommender or location is not
  specified, recommendations for all supported recommenders or locations,
  respectively, are listed. If the `--recursive` flag is set,
  recommendations for child resources and projects are also listed.
  Supported recommenders can be found here:
  https://cloud.google.com/recommender/docs/recommenders.
  """

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command.
    """
    flags.AddParentFlagsToParser(parser)
    parser.add_argument(
        '--location',
        metavar='LOCATION',
        required=False,
        help=(
            'Location to list recommendations for. If no location is specified,'
            ' recommendations for all supported locations are listed.'
            ' Not specifying a location can add 15-20 seconds to the runtime.'
        ),
    )
    parser.add_argument(
        '--recommender',
        metavar='RECOMMENDER',
        required=False,
        help=(
            'Recommender to list recommendations for. If no recommender is'
            ' specified, recommendations for all supported recommenders are'
            ' listed. Supported recommenders can be found here:'
            ' https://cloud.google.com/recommender/docs/recommenders'
            ' Not specifying a recommender can add 15-20 seconds to the'
            ' runtime.'
        ),
    )
    parser.add_argument(
        '--recursive',
        required=False,
        action=arg_parsers.StoreTrueFalseAction,
        help=("""
            In addition to listing the recommendations for the specified
            organization or folder, recursively list all of
            the recommendations for the resource's child resources, including
            their descendants (for example, a folder's sub-folders), and for the
            resource's child projects. For example, when using the
            `--recursive` flag and specifying an organization, the response
            lists all of the recommendations associated with that
            organization, all of the recommendations associated with that
            organization's folders and sub-folders, and all of the
            recommendations associated with that organization's child
            projects.  The maximum number of resources (organization,
            folders, projects, and descendant resources) that can be accessed at
            once with the `--recursive` flag is 100. For a larger
            number of nested resources, use
            [BigQuery export](https://cloud.google.com/recommender/docs/bq-export/export-recommendations-to-bq).
            Using `--recursive` can add 15-20 seconds per resource to the
            runtime.
            """),
    )
    parser.display_info.AddFormat(DISPLAY_FORMAT)

  def setArgs(self, args):
    """Setups up args to search all resources under a project, folder, or organization.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      (argparse.Namespace) args with additional parameters setup
    """

    args.read_mask = '*'
    args.asset_types = [
        # gcloud-disable-gdu-domain
        'cloudresourcemanager.googleapis.com/Project',
        # gcloud-disable-gdu-domain
        'cloudresourcemanager.googleapis.com/Folder'
    ]
    args.order_by = 'createTime'
    args.query = '*'
    if args.project:
      args.scope = 'projects/' + args.project
    if args.organization:
      args.scope = 'organizations/' + args.organization
    if args.folder:
      args.scope = 'folders/' + args.folder

    return args

  def read(self, asset_in):
    if isinstance(asset_in, list):
      return asset_in[0]
    else:
      return asset_in

  def AddResource(self, resource_location) -> bool:
    if resource_location not in self.resource_locations:
      self.resource_locations.append(resource_location)
      return True
    return False

  def searchAllResources(self, args):
    """Search all nested resources under a project, folder, or organization.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      (List): a list of all Google Cloud resource,location pairs
    """

    args = self.setArgs(args)
    client = client_util.AssetSearchClient(client_util.DEFAULT_API_VERSION)
    resources = list(client.SearchAllResources(args))
    self.resource_locations = []

    for r in resources:
      parent_resource = f'{self.read(args.scope)}/locations/{r.location}'
      if 'project' not in parent_resource:
        self.AddResource(parent_resource)

      # gcloud-disable-gdu-domain
      if r.assetType == 'cloudresourcemanager.googleapis.com/Project':
        self.AddResource(f'{self.read(r.project)}/locations/{r.location}')

      # gcloud-disable-gdu-domain
      if (
          r.assetType == 'cloudresourcemanager.googleapis.com/Folder'
          and self.AddResource(f'{self.read(r.folders)}/locations/{r.location}')
      ):
        args.scope = self.read(r.folders)
        resources.extend(client.SearchAllResources(args))
      if len(self.resource_locations) > 100:
        raise exceptions.UnsupportedOperationError(
            'The maximum number of resources (organizations, folders, projects,'
            ' and descendant resources) that can be accessed to list'
            ' recommendations is 100. To access'
            ' a larger number of resources, use BigQuery Export.'
        )
    return self.resource_locations

  def CollectAssets(self, args):
    """Iterate through search all resources response and collects unique Google Cloud resouce,location pairs.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      (List): a list of all Google Cloud resource,location pairs
    """

    # Collect Assets and Locations
    log.status.Print('Collecting Resources... This may take some time...')
    if args.recursive:
      resource_locations = self.searchAllResources(args)
    else:
      if args.location is None:
        loc_client = locations.CreateClient(self.ReleaseTrack())
        resource_locations = [
            loc.name
            for loc in loc_client.List(
                args.page_size,
                project=args.project,
                organization=args.organization,
                folder=args.folder,
                billing_account=args.billing_account,
            )
        ]
      else:
        resource_locations = [
            flags.GetResourceSegment(args) + f'/locations/{args.location}'
        ]
    return resource_locations

  def ListRecommenders(self, args):
    """List all Recommenders.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      (list) all recommenders in a list of strings
    """

    recommenders_client = recommenders.CreateClient(self.ReleaseTrack())
    recommenders_response = recommenders_client.List(args.page_size)
    return list(recommenders_response)

  def GetRecommendations(self, args, asset_recommenders):
    """Collects all recommendations for a given Google Cloud Resource.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.
      asset_recommenders: list, The list of Google Cloud resource recommender
        URL to collect recommendations

    Returns:
      (Recommendations) a iterator for all returned recommendations
    """

    recommendations = []
    recommendations_client = recommendation.CreateClient(self.ReleaseTrack())

    resource_prev = None
    location_prev = None
    for resource, location, recommender in asset_recommenders:
      if resource != resource_prev or location != location_prev:
        log.status.Print(f'Reading Recommendations for: {resource} {location}')
      resource_prev = resource
      location_prev = location
      parent_name = '/'.join([resource, location, recommender])
      new_recommendations = recommendations_client.List(
          parent_name, args.page_size
      )
      try:  # skip recommenders that the user does not have access to.
        peek = next(new_recommendations)  # execute first element of generator
      except (
          apitools_exceptions.HttpBadRequestError,
          apitools_exceptions.BadStatusCodeError,
          StopIteration,
      ):
        continue
      recommendations = itertools.chain(
          recommendations, (peek,), new_recommendations
      )

    return recommendations

  def Run(self, args):
    """Run 'gcloud recommender recommendations list'.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      The list of recommendations for this project.
    """

    # Collect Assets and Locations
    resource_locations = self.CollectAssets(args)

    # collect recommendations for all recommenders
    asset_recommenders = []
    for asset in resource_locations:
      tokens = asset.split('/')
      resource = '/'.join(tokens[:2])
      location = '/'.join(tokens[2:4])
      if args.recommender is not None:
        asset_recommenders.append(
            (resource, location, f'recommenders/{args.recommender}')
        )
      else:  # loop through all recommenders
        asset_recommenders.extend([
            (resource, location, f'recommenders/{response.name}')
            for response in self.ListRecommenders(args)
        ])

    return self.GetRecommendations(args, asset_recommenders)


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class ListOriginal(base.ListCommand):
  r"""List operations for a recommendation.

  This command lists all recommendations for a given Google Cloud entity ID,
  location, and recommender. Supported recommenders can be found here:
  https://cloud.google.com/recommender/docs/recommenders.
  The following Google Cloud entity types are supported: project,
  billing_account, folder and organization.
  """

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command.
    """
    flags.AddParentFlagsToParser(parser)
    parser.add_argument(
        '--location',
        metavar='LOCATION',
        required=True,
        help='Location to list recommendations for.',
    )
    parser.add_argument(
        '--recommender',
        metavar='RECOMMENDER',
        required=True,
        help=(
            'Recommender to list recommendations for. Supported recommenders'
            ' can be found here:'
            ' https://cloud.google.com/recommender/docs/recommenders.'
        ),
    )
    parser.display_info.AddFormat(DISPLAY_FORMAT)

  def Run(self, args):
    """Run 'gcloud recommender recommendations list'.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      The list of recommendations for this project.
    """
    recommendations_client = recommendation.CreateClient(self.ReleaseTrack())
    parent_name = flags.GetRecommenderName(args)

    return recommendations_client.List(parent_name, args.page_size)
