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
"""Implementation of create command for batch actions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.storage import storage_batch_operations_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage import flags
from googlecloudsdk.command_lib.storage.batch_operations.jobs import resource_args
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Create(base.Command):
  """Create a new batch operation job."""

  detailed_help = {
      "DESCRIPTION": """
      Create a batch operation job, allowing you to perform operations
      such as deletion, updating metadata, and more on objects in a
      serverless manner.
      """,
      "EXAMPLES": """
      To create a batch job with the name `my-job` to perform object deletion
      on bucket `my-bucket` and the manifest file
      `gs://my-bucket/manifest.csv` specifies the objects to be transformed:

          $ {command} my-job --bucket=my-bucket --manifest-location=gs://my-bucket/manifest.csv
          --delete-object

      To create a batch job with the name `my-job` to update object metadata
      `Content-Disposition` to `inline` and `Content-Language` to `en` on bucket `my-bucket` where
      you want to match objects with the prefix `prefix1` or `prefix2`:

          $ {command} my-job --bucket=my-bucket --included-object-prefixes=prefix1,prefix2
          --put-metadata=Content-Disposition=inline,Content-Language=en

      To create a batch job with the name `my-job` to put object event based hold on objects in bucket `my-bucket` with
      logging config enabled for corresponding transform action and succeeded and failed action states:

          $ {command} my-job --bucket=my-bucket --put-object-event-based-hold
          --put-metadata=Content-Disposition=inline,Content-Language=en
          --log-actions=transform --log-action-states=succeeded,failed
      """,
  }

  @staticmethod
  def Args(parser):
    resource_args.add_batch_job_resource_arg(parser, "to create")
    flags.add_batch_jobs_flags(parser)

  def Run(self, args):
    # Prompts to confirm deletion if --delete-object is specified.
    dry_run = getattr(args, "dry_run", False)
    if args.delete_object and not dry_run:
      delete_prompt = (
          "This command will delete objects specified in the batch operation"
          " job. Please ensure that you have soft delete enabled on the bucket"
          " if you want to restore the objects within the retention duration."
      )
      console_io.PromptContinue(
          message=delete_prompt,
          cancel_on_no=True,
      )
    job_ref = args.CONCEPTS.batch_job.Parse()
    storage_batch_operations_api.StorageBatchOperationsApi().create_batch_job(
        args, job_ref.RelativeName()
    )
    log.status.Print("Created batch job: {}".format(job_ref.RelativeName()))


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CreateAlpha(Create):
  """Create a new batch operation job."""

  @staticmethod
  def Args(parser):
    resource_args.add_batch_job_resource_arg(parser, "to create")
    flags.add_batch_jobs_flags(parser)
    flags.add_batch_jobs_dry_run_flag(parser)
