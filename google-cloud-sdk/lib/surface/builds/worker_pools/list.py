# -*- coding: utf-8 -*- #
# Copyright 2018 Google LLC. All Rights Reserved.
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
"""List worker pools command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.cloudbuild import cloudbuild_util
from googlecloudsdk.api_lib.cloudbuild.v2 import client_util as cloudbuild_v2_util
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources


def _GetWorkerPoolURI(resource):
  if isinstance(resource, dict):
    resource = resource['wp']
  wp = resources.REGISTRY.ParseRelativeName(
      resource.name,
      collection='cloudbuild.projects.locations.workerPools',
      api_version='v1')
  return wp.SelfLink()


def _GetWorkerPoolSecondGenURI(resource):
  if isinstance(resource, dict):
    resource = resource['wp']
  wp = resources.REGISTRY.ParseRelativeName(
      resource.name,
      collection='cloudbuild.projects.locations.workerPoolSecondGen',
      api_version='v2')
  return wp.SelfLink()


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.UniverseCompatible
class List(base.ListCommand):
  """List all worker pools in a Google Cloud project."""

  detailed_help = {
      'DESCRIPTION':
          '{description}',
      'EXAMPLES':
          """\
          To fetch a list of worker pools running in region `us-central1`, run:

            $ {command} --region=us-central1
          """,
  }

  @staticmethod
  def Args(parser):
    """Register flags for this command.

    Args:
      parser: An argparse.ArgumentParser-like object. It is mocked out in order
        to capture some information, but behaves like an ArgumentParser.
    """

    parser.add_argument(
        '--region',
        help='The Cloud region to list worker pools in.')
    parser.display_info.AddFormat("""
          table(
            name.segment(-1),
            createTime.date('%Y-%m-%dT%H:%M:%S%Oz', undefined='-'),
            state
          )
        """)
    parser.display_info.AddUriFunc(_GetWorkerPoolURI)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """

    wp_region = args.region
    wp_page_size = args.page_size
    if not wp_region:
      wp_region = properties.VALUES.builds.region.GetOrFail()
    parent = properties.VALUES.core.project.Get(required=True)

    # Get the parent project ref
    parent_resource = resources.REGISTRY.Create(
        collection='cloudbuild.projects.locations',
        projectsId=parent,
        locationsId=wp_region)

    return _ListWorkerPoolFirstGen(
        parent_resource, wp_page_size, self.ReleaseTrack()
    )


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class ListBeta(List):
  """List all worker pools in a Google Cloud project."""

  @staticmethod
  def Args(parser):
    """Register flags for this command.

    Args:
      parser: An argparse.ArgumentParser-like object. It is mocked out in order
        to capture some information, but behaves like an ArgumentParser.
    """

    parser.add_argument(
        '--region',
        help='The Cloud region to list worker pools in.')
    parser.add_argument(
        '--generation',
        default=1,
        type=int,
        help=('Generation of the worker pool.'))
    parser.display_info.AddFormat("""
          table(
            name.segment(-1),
            createTime.date('%Y-%m-%dT%H:%M:%S%Oz', undefined='-'),
            state
          )
        """)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """

    wp_region = args.region
    wp_page_size = args.page_size
    if not wp_region:
      wp_region = properties.VALUES.builds.region.GetOrFail()
    parent = properties.VALUES.core.project.Get(required=True)

    # Get the parent project ref
    parent_resource = resources.REGISTRY.Create(
        collection='cloudbuild.projects.locations',
        projectsId=parent,
        locationsId=wp_region)

    if args.generation == 1:
      args.GetDisplayInfo().AddUriFunc(_GetWorkerPoolURI)
      return _ListWorkerPoolFirstGen(
          parent_resource, wp_page_size, self.ReleaseTrack()
      )
    if args.generation == 2:
      args.GetDisplayInfo().AddUriFunc(_GetWorkerPoolSecondGenURI)
      return _ListWorkerPoolSecondGen(parent_resource)

    raise exceptions.InvalidArgumentException(
        '--generation',
        'please use one of the following valid generation values: 1, 2',
    )


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class ListAlpha(List):
  """List all worker pools in a Google Cloud project."""

  @staticmethod
  def Args(parser):
    """Register flags for this command.

    Args:
      parser: An argparse.ArgumentParser-like object. It is mocked out in order
        to capture some information, but behaves like an ArgumentParser.
    """

    parser.add_argument(
        '--region',
        help='The Cloud region to list worker pools in.')
    parser.add_argument(
        '--generation',
        default=1,
        type=int,
        help=('Generation of the worker pool.'))
    parser.display_info.AddFormat("""
          table(
            name.segment(-1),
            createTime.date('%Y-%m-%dT%H:%M:%S%Oz', undefined='-'),
            state
          )
        """)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """

    wp_region = args.region
    wp_page_size = args.page_size
    if not wp_region:
      wp_region = properties.VALUES.builds.region.GetOrFail()

    parent = properties.VALUES.core.project.Get(required=True)

    # Get the parent project ref
    parent_resource = resources.REGISTRY.Create(
        collection='cloudbuild.projects.locations',
        projectsId=parent,
        locationsId=wp_region,
    )

    if args.generation == 1:
      args.GetDisplayInfo().AddUriFunc(_GetWorkerPoolURI)
      return _ListWorkerPoolFirstGen(
          parent_resource, wp_page_size, self.ReleaseTrack()
      )
    if args.generation == 2:
      args.GetDisplayInfo().AddUriFunc(_GetWorkerPoolSecondGenURI)
      return _ListWorkerPoolSecondGen(parent_resource)

    raise exceptions.InvalidArgumentException(
        '--generation',
        'please use one of the following valid generation values: 1, 2',
    )


def _ListWorkerPoolSecondGen(parent_resource):
  """List Worker Pool Second Generation.

  Args:
    parent_resource: The parent resource for Worker Pool Second Generation.

  Returns:
    A list of Worker Pool Second Generation resources.
  """
  client = cloudbuild_v2_util.GetClientInstance()
  messages = client.MESSAGES_MODULE

  # Send the List request
  wp_list = client.projects_locations_workerPoolSecondGen.List(
      messages.CloudbuildProjectsLocationsWorkerPoolSecondGenListRequest(
          parent=parent_resource.RelativeName())).workerPoolSecondGen

  return wp_list


def _ListWorkerPoolFirstGen(parent_resource, page_size, release_track):
  """List Worker Pool First Generation.

  Args:
    parent_resource: The parent resource for Worker Pool First Generation.
    page_size: The number of elements to return in each page.
    release_track: The desired value of the enum
      googlecloudsdk.calliope.base.ReleaseTrack.

  Returns:
    A list of Worker Pool First Generation resources.
  """
  client = cloudbuild_util.GetClientInstance(release_track)
  messages = cloudbuild_util.GetMessagesModule(release_track)

  # Send the List request
  wp_list = client.projects_locations_workerPools.List(
      messages.CloudbuildProjectsLocationsWorkerPoolsListRequest(
          parent=parent_resource.RelativeName(), pageSize=page_size
      )
  ).workerPools

  return wp_list
