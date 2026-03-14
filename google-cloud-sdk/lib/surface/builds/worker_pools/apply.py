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
"""Create worker pool command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.cloudbuild import cloudbuild_exceptions
from googlecloudsdk.api_lib.cloudbuild import workerpool_config
from googlecloudsdk.api_lib.cloudbuild.v2 import client_util as cloudbuild_v2_util
from googlecloudsdk.api_lib.cloudbuild.v2 import input_util
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class CreateAlpha(base.CreateCommand):
  """Create a private pool for use by Cloud Build."""

  @staticmethod
  def Args(parser):
    """Register flags for this command.

    Args:
      parser: An argparse.ArgumentParser-like object. It is mocked out in order
        to capture some information, but behaves like an ArgumentParser.
    """
    parser.add_argument(
        '--file',
        required=True,
        help='The YAML file to use as the worker pool configuration file.')
    parser.add_argument(
        '--region',
        help='Region for Cloud Build.')
    parser.add_argument(
        '--generation',
        default=2,
        type=int,
        help=('Generation of the worker pool.'),
    )
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

    if args.generation == 1:
      raise exceptions.InvalidArgumentException(
          '--generation',
          'for generation=1 please use the gcloud commands "gcloud builds'
          ' worker-pools create" or "gcloud builds worker-pools update"',
      )
    if args.generation == 2:
      return _CreateWorkerPoolSecondGen(args)

    raise exceptions.InvalidArgumentException(
        '--generation',
        'please use one of the following valid generation values: 1, 2',
    )


def _CreateWorkerPoolSecondGen(args):
  """Creates a worker pool second generation.

  Args:
    args: an argparse namespace. All the arguments that were provided to the
        create command invocation.

  Returns:
    A worker pool second generation resource.
  """
  wp_region = args.region
  if not wp_region:
    wp_region = properties.VALUES.builds.region.GetOrFail()

  client = cloudbuild_v2_util.GetClientInstance()
  messages = client.MESSAGES_MODULE

  try:
    wpsg = workerpool_config.LoadWorkerpoolConfigFromPath(
        args.file, messages.WorkerPoolSecondGen
    )
    # Public IP in primary network interface of VM has to be disabled when
    # routing all the traffic to network attachment.
    if (
        wpsg.network is not None
        and wpsg.network.privateServiceConnect is not None
        and wpsg.network.privateServiceConnect.routeAllTraffic
        and wpsg.network.publicIpAddressDisabled is None
    ):
      wpsg.network.publicIpAddressDisabled = True
  except cloudbuild_exceptions.ParseProtoException as err:
    log.err.Print(
        '\nFailed to parse configuration from file. If you'
        ' were a Private Preview user, note that the format for this'
        ' file has changed slightly for GA.\n')
    raise err

  yaml_data = input_util.LoadYamlFromPath(args.file)
  workerpoolsecondgen_id = yaml_data['name']
  # Get the workerpool second gen ref
  wp_resource = resources.REGISTRY.Parse(
      None,
      collection='cloudbuild.projects.locations.workerPoolSecondGen',
      api_version=cloudbuild_v2_util.GA_API_VERSION,
      params={
          'projectsId': properties.VALUES.core.project.Get(required=True),
          'locationsId': wp_region,
          'workerPoolSecondGenId': workerpoolsecondgen_id,
      },
  )

  update_mask = cloudbuild_v2_util.MessageToFieldPaths(wpsg)
  req = messages.CloudbuildProjectsLocationsWorkerPoolSecondGenPatchRequest(
      name=wp_resource.RelativeName(),
      workerPoolSecondGen=wpsg,
      updateMask=','.join(update_mask),
      allowMissing=True,
  )

  # Update worker pool second gen (or create if missing).
  updated_op = client.projects_locations_workerPoolSecondGen.Patch(req)

  op_resource = resources.REGISTRY.ParseRelativeName(
      updated_op.name, collection='cloudbuild.projects.locations.operations'
  )
  updated_wp = waiter.WaitFor(
      waiter.CloudOperationPoller(
          client.projects_locations_workerPoolSecondGen,
          client.projects_locations_operations,
      ),
      op_resource,
      'Applying {file} as worker pool second gen {name}'.format(
          file=args.file, name=wp_resource.RelativeName()
      ),
  )

  return updated_wp
