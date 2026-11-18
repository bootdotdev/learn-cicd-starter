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
"""Describe worker pool command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.cloudbuild import cloudbuild_util
from googlecloudsdk.api_lib.cloudbuild.v2 import client_util as cloudbuild_v2_util
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.UniverseCompatible
class Describe(base.DescribeCommand):
  """Describe a worker pool used by Cloud Build."""

  detailed_help = {
      'DESCRIPTION':
          '{description}',
      'EXAMPLES':
          """\
          To get information about a worker pool named `wp1` in region `us-central1`, run:

            $ {command} wp1 --region=us-central1
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
        help='The Cloud region where the worker pool is.')
    parser.add_argument(
        'WORKER_POOL', help='The ID of the worker pool to describe.')

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """

    return _DescribeWorkerPoolFirstGen(args, self.ReleaseTrack())


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class DescribeBeta(Describe):
  """Describe a worker pool used by Cloud Build."""

  @staticmethod
  def Args(parser):
    """Register flags for this command.

    Args:
      parser: An argparse.ArgumentParser-like object. It is mocked out in order
        to capture some information, but behaves like an ArgumentParser.
    """
    parser.add_argument(
        '--region',
        help='The Cloud region where the worker pool is.')
    parser.add_argument(
        '--generation',
        default=1,
        type=int,
        help=('Generation of the worker pool.'))
    parser.add_argument(
        'WORKER_POOL', help='The ID of the worker pool to describe.')

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """

    if args.generation == 1:
      return _DescribeWorkerPoolFirstGen(args, self.ReleaseTrack())
    if args.generation == 2:
      return _DescribeWorkerPoolSecondGen(args)

    raise exceptions.InvalidArgumentException(
        '--generation',
        'please use one of the following valid generation values: 1, 2',
    )


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class DescribeAlpha(Describe):
  """Describe a worker pool used by Cloud Build."""

  @staticmethod
  def Args(parser):
    """Register flags for this command.

    Args:
      parser: An argparse.ArgumentParser-like object. It is mocked out in order
        to capture some information, but behaves like an ArgumentParser.
    """
    parser.add_argument(
        '--region',
        help='The Cloud region where the worker pool is.')
    parser.add_argument(
        '--generation',
        default=1,
        type=int,
        help=('Generation of the worker pool.'))
    parser.add_argument(
        'WORKER_POOL', help='The ID of the worker pool to describe.')

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """

    if args.generation == 1:
      return _DescribeWorkerPoolFirstGen(args, self.ReleaseTrack())
    if args.generation == 2:
      return _DescribeWorkerPoolSecondGen(args)

    raise exceptions.InvalidArgumentException(
        '--generation',
        'please use one of the following valid generation values: 1, 2',
    )


def _DescribeWorkerPoolSecondGen(args):
  """Describes a Worker Pool Second Generation.

  Args:
    args: an argparse namespace. All the arguments that were provided to the
        create command invocation.

  Returns:
    A Worker Pool Second Generation resource.
  """
  client = cloudbuild_v2_util.GetClientInstance()
  messages = client.MESSAGES_MODULE

  wp_region = args.region
  if not wp_region:
    wp_region = properties.VALUES.builds.region.GetOrFail()

  # Get the workerpool second gen ref
  wp_resource = resources.REGISTRY.Parse(
      None,
      collection='cloudbuild.projects.locations.workerPoolSecondGen',
      api_version=cloudbuild_v2_util.GA_API_VERSION,
      params={
          'projectsId': properties.VALUES.core.project.Get(required=True),
          'locationsId': wp_region,
          'workerPoolSecondGenId': args.WORKER_POOL,
      })

  # Send the Get request
  wp = client.projects_locations_workerPoolSecondGen.Get(
      messages.CloudbuildProjectsLocationsWorkerPoolSecondGenGetRequest(
          name=wp_resource.RelativeName()))

  # Format the workerpool second gen name for display
  try:
    wp.name = cloudbuild_v2_util.WorkerPoolSecondGenShortName(wp.name)
  except ValueError:
    pass  # Must be an old version.

  return wp


def _DescribeWorkerPoolFirstGen(args, release_track):
  """Describes a Worker Pool First Generation.

  Args:
    args: an argparse namespace. All the arguments that were provided to the
        create command invocation.
    release_track: The desired value of the enum
      googlecloudsdk.calliope.base.ReleaseTrack.

  Returns:
    A Worker Pool First Generation resource.
  """
  wp_region = args.region
  if not wp_region:
    wp_region = properties.VALUES.builds.region.GetOrFail()

  client = cloudbuild_util.GetClientInstance(release_track)
  messages = cloudbuild_util.GetMessagesModule(release_track)

  parent = properties.VALUES.core.project.Get(required=True)

  wp_name = args.WORKER_POOL

  # Get the workerpool ref
  wp_resource = resources.REGISTRY.Parse(
      None,
      collection='cloudbuild.projects.locations.workerPools',
      api_version=cloudbuild_util.RELEASE_TRACK_TO_API_VERSION[release_track],
      params={
          'projectsId': parent,
          'locationsId': wp_region,
          'workerPoolsId': wp_name,
      })

  # Send the Get request
  wp = client.projects_locations_workerPools.Get(
      messages.CloudbuildProjectsLocationsWorkerPoolsGetRequest(
          name=wp_resource.RelativeName()))

  # Format the workerpool name for display
  try:
    wp.name = cloudbuild_util.WorkerPoolShortName(wp.name)
  except ValueError:
    pass  # Must be an old version.

  return wp
