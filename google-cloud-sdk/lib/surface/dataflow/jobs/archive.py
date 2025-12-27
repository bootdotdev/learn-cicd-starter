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
"""Implementation of gcloud dataflow jobs archive command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.dataflow import apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.dataflow import job_utils
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io


@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.BETA)
@base.DefaultUniverseOnly
class Archive(base.Command):
  """Archives a job.

  Archives a single job. The job must be in a terminal state, otherwise the
  request will be rejected.

  This command will require confirmation to run.

  ## EXAMPLES

  To archive job `2025-03-15_14_23_56-1234567890123456`, run:

    $ {command} 2025-03-15_14_23_56-1234567890123456
  """

  @staticmethod
  def Args(parser):
    job_utils.ArgsForJobRef(parser)

  def Run(self, args):
    """Runs the command.

    Args:
      args: The arguments that were provided to this command invocation.

    Returns:
      A Job message.
    """
    job_ref = job_utils.ExtractJobRef(args)
    job_id = job_ref.jobId

    console_io.PromptContinue(
        message='Job [{}] will be archived.'.format(job_id), cancel_on_no=True
    )

    messages = apis.GetMessagesModule()
    job = messages.Job(
        jobMetadata=messages.JobMetadata(
            userDisplayProperties=messages.JobMetadata.UserDisplayPropertiesValue(
                additionalProperties=[
                    messages.JobMetadata.UserDisplayPropertiesValue.AdditionalProperty(
                        key='archived', value='true'
                    )
                ]
            )
        )
    )

    request = messages.DataflowProjectsLocationsJobsUpdateRequest(
        jobId=job_ref.jobId,
        location=job_ref.location,
        projectId=job_ref.projectId,
        job=job,
        updateMask='job_metadata.user_display_properties.archived',
    )

    result = apis.Jobs.GetService().Update(request)
    log.status.Print('Archived job [{}].'.format(job_id))
    return result
