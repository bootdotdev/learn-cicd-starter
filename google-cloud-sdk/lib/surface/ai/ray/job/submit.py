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
"""Command to create a serverless ray job in Vertex AI."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.ai.serverless_ray_jobs import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.ai import constants
from googlecloudsdk.command_lib.ai import endpoint_util
from googlecloudsdk.command_lib.ai.serverless_ray_jobs import flags
from googlecloudsdk.command_lib.ai.serverless_ray_jobs import serverless_ray_jobs_util
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log

_OPERATION_RESOURCE_NAME_TEMPLATE = (
    'projects/{project_number}/locations/{region}/operations/{operation_id}'
)

_JOB_CREATION_DISPLAY_MESSAGE_TEMPLATE = """\
Serverless Ray Job [{job_name}] is submitted successfully.

Your job is still active. You may view the status of your job with the command:

  $ {command_prefix} ai ray job describe {job_name}

"""


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.UniverseCompatible
class CreateGA(base.CreateCommand):
  """Create a new serverless ray job.

  This command will attempt to run the serverless ray job immediately upon
  creation.

  ## EXAMPLES

  To create a job under project ``example'' in region
  ``us-central1'', run:

    $ {command} --region=us-central1 --project=example
    --resource-spec=resource-unit=1,disk-size=100
    --entrypoint='gs://test-project/ray_job.py'
    --display-name=test
  """

  _version = constants.GA_VERSION

  @staticmethod
  def Args(parser):
    flags.AddCreateServerlessRayJobFlags(parser)

  def _DisplayResult(self, response):
    cmd_prefix = 'gcloud'
    if self.ReleaseTrack().prefix:
      cmd_prefix += ' ' + self.ReleaseTrack().prefix

    log.status.Print(
        _JOB_CREATION_DISPLAY_MESSAGE_TEMPLATE.format(
            job_name=response.name, command_prefix=cmd_prefix
        )
    )

  def _PrepareJobSpec(self, args, api_client):
    job_spec = serverless_ray_jobs_util.ConstructServerlessRayJobSpec(
        api_client,
        main_python_file_uri=args.entrypoint,
        entrypoint_file_args=args.entrypoint_file_args,
        archive_uris=args.archive_uris,
        service_account=args.service_account,
        container_image_uri=args.container_image_uri,
        resource_spec=args.resource_spec,
    )

    return job_spec

  def Run(self, args):
    # TODO(b/390723702): Add request validation.
    region_ref = args.CONCEPTS.region.Parse()
    region = region_ref.AsDict()['locationsId']

    with endpoint_util.AiplatformEndpointOverrides(
        version=self._version, region=region):
      api_client = client.ServerlessRayJobsClient(version=self._version)

      print('self._version: {}'.format(self._version))

      job_spec = self._PrepareJobSpec(args, api_client)

      labels = labels_util.ParseCreateArgs(
          args, api_client.ServerlessRayJobMessage().LabelsValue
      )

      response = api_client.Create(
          parent=region_ref.RelativeName(),
          job_spec=job_spec,
          display_name=args.display_name,
          labels=labels,
      )
      self._DisplayResult(response)
      return response


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class CreatePreGA(CreateGA):
  """Create a new custom job.

  This command will attempt to run the custom job immediately upon creation.

  ## EXAMPLES

  To create a job under project ``example'' in region
  ``us-central1'', run:

    $ {command} --region=us-central1 --project=example
    --worker-pool-spec=replica-count=1,machine-type='n1-highmem-2',container-image-uri='gcr.io/ucaip-test/ucaip-training-test'
    --display-name=test
  """
  _version = constants.BETA_VERSION
