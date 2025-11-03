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
"""Implementation of delete command for batch operations jobs."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.storage import storage_batch_operations_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage.batch_operations.jobs import resource_args
from googlecloudsdk.core import log


@base.DefaultUniverseOnly
class Delete(base.Command):
  """Delete a batch-operations job."""

  detailed_help = {
      "DESCRIPTION": """
      Delete the batch operation job.
      """,
      "EXAMPLES": """
      To delete a batch job with the name `my-job` in location `us-central1`:

          $ {command} my-job --location=us-central1

      To delete the same batch job with fully specified name:

          $ {command} projects/my-project/locations/us-central1/jobs/my-job
      """,
  }

  @staticmethod
  def Args(parser):
    resource_args.add_batch_job_resource_arg(parser, "to delete")

  def Run(self, args):
    job_name = args.CONCEPTS.batch_job.Parse().RelativeName()
    storage_batch_operations_api.StorageBatchOperationsApi().delete_batch_job(
        job_name
    )
    log.status.Print("Deleted batch job: {}".format(job_name))
