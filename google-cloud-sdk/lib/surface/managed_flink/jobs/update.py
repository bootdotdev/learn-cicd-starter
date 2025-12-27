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

"""Update a Flink job's parallelism."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.managed_flink import util as flink_util
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.managed_flink import flags
from googlecloudsdk.command_lib.managed_flink import flink_backend
from googlecloudsdk.command_lib.util.args import common_args
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Update(base.UpdateCommand):
  r"""Update the parallelism of a Flink job.

  Update the parallelism of a Flink job.

  ## EXAMPLES

  The following command updates a Flink Job with the ID `example-job-id`
  to change max parallesim to 4:

    $ {command} example-job-id \
        --project=example-project \
        --location=us-central1 \
        --autotuning-mode elastic \
        --min-parallelism=1 \
        --max-parallelism=4 \

  """

  @staticmethod
  def Args(parser):
    common_args.ProjectArgument(
        help_text_to_overwrite='Project to update the job in.'
    ).AddToParser(parser)
    flags.AddJobIdArgument(parser)
    flags.AddLocationArgument(parser)
    flags.AddDeploymentArgument(
        parser, help_text_to_overwrite='Deployment to update the job in.'
    )
    flags.AddShowOutputArgument(parser)
    flags.AddAutotuningModeArgument(parser, required=False)
    flags.AddFixedParallelismArgs(parser)
    flags.AddElasticParallelismArgs(parser)
    flags.AddAsyncArgument(parser, default=False)

  def Run(self, args):
    flink_backend.ValidateAutotuning(
        args.autotuning_mode,
        args.min_parallelism,
        args.max_parallelism,
        args.parallelism,
    )
    msg = flink_util.GetMessagesModule(self.ReleaseTrack())

    # Configure autotuning mode
    autotuning_config = msg.AutotuningConfig()
    if args.autotuning_mode == 'fixed':
      autotuning_config.fixed = msg.Fixed(parallelism=args.parallelism)
    else:
      autotuning_config.throughputBased = msg.Elastic(
          parallelism=args.min_parallelism,
          minParallelism=args.min_parallelism,
          maxParallelism=args.max_parallelism,
      )

    jobspec = msg.JobSpec(
        autotuningConfig=autotuning_config,
    )

    job = msg.Job(
        name=args.job_id,
        jobSpec=jobspec,
    )

    if args.deployment:
      job.deploymentId = args.deployment

    update = msg.ManagedflinkProjectsLocationsJobsPatchRequest(
        name='projects/{0}/locations/{1}/jobs/{2}'.format(
            properties.VALUES.core.project.Get(required=True),
            args.location,
            args.job_id,
        ),
        job=job,
        updateMask='autotuningConfig',
    )

    flink_client = flink_util.FlinkClient(self.ReleaseTrack())
    patch_op = flink_client.client.projects_locations_jobs.Patch(update)

    if args.async_submit:
      return patch_op

    log.status.Print('Update request issued for [{0}]'.format(update.job.name))

    patch_op_ref = resources.REGISTRY.Parse(
        patch_op.name, collection='managedflink.projects.locations.operations'
    )
    waiter.WaitFor(
        waiter.CloudOperationPoller(
            flink_client.client.projects_locations_jobs,
            flink_client.client.projects_locations_operations,
        ),
        patch_op_ref,
        'Waiting for update operations [{0}] to complete...'.format(
            patch_op.name
        ),
    )
    return patch_op
