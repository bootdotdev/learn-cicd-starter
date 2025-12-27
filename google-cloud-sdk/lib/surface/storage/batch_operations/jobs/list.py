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
"""Implementation of list command for batch operations jobs."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.storage import storage_batch_operations_api
from googlecloudsdk.calliope import base

_SBO_CLH_LOCATION_GLOBAL = "global"


def _TransformTransformation(job):
  """Transform for the TRANSFORMATION field in the table output.

  TRANSFORMATION is generated from the oneof field transformation.

  Args:
    job: job dictionary for transform

  Returns:
    A dictionary of the transformation type and its values.
  """
  transformation = {}
  transform_types = [
      "putObjectHold",
      "deleteObject",
      "putMetadata",
      "rewriteObject",
  ]
  for transform in transform_types:
    if transform in job:
      transformation[transform] = job[transform]
      return transformation


def _TransformDryRun(job):
  """Transform for the DRY_RUN field in the table output."""
  return job.get("dry_run", False)


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class List(base.ListCommand):
  """List batch-operations jobs."""

  detailed_help = {
      "DESCRIPTION": """
      List batch operation jobs.
      """,
      "EXAMPLES": """
      To list all batch jobs:

          $ {command}

      To list all batch jobs with a page size of `10`:

          $ {command} --page-size=10

      To list a limit of `20` batch jobs:

          $ {command} --limit=20

      To list all batch jobs in `JSON` format:

          $ {command} --format=json
      """,
  }

  @staticmethod
  def Args(parser):
    base.URI_FLAG.RemoveFromParser(parser)
    parser.display_info.AddFormat("""
      table(
        name.basename():wrap=20:label=BATCH_JOB_ID,
        bucketList.buckets:wrap=20:label=SOURCE,
        transformation():wrap=20:label=TRANSFORMATION,
        createTime:wrap=20:label=CREATE_TIME,
        counters:wrap=20:label=COUNTERS,
        errorSummaries:wrap=20:label=ERROR_SUMMARIES,
        state:wrap=20:label=STATE
      )
    """)
    parser.display_info.AddTransforms({
        "transformation": _TransformTransformation,
    })

  def Run(self, args):
    return storage_batch_operations_api.StorageBatchOperationsApi().list_batch_jobs(
        _SBO_CLH_LOCATION_GLOBAL, args.limit, args.page_size
    )


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class ListAlpha(List):
  """List batch-operations jobs."""

  detailed_help = {
      "DESCRIPTION": """
      List batch operation jobs.
      """,
      "EXAMPLES": """
      To list all batch jobs:

          $ {command}

      To list all batch jobs that are `not` dry run:

          $ {command} --filter="dry_run=false"

      To list all batch jobs with a page size of `10`:

          $ {command} --page-size=10

      To list a limit of `20` batch jobs:

          $ {command} --limit=20

      To list all batch jobs in `JSON` format:

          $ {command} --format=json
      """,
  }

  @staticmethod
  def Args(parser):
    base.URI_FLAG.RemoveFromParser(parser)
    parser.display_info.AddFormat("""
      table(
        name.basename():wrap=20:label=BATCH_JOB_ID,
        dryrun():wrap=20:label=DRY_RUN,
        bucketList.buckets:wrap=20:label=SOURCE,
        transformation():wrap=20:label=TRANSFORMATION,
        createTime:wrap=20:label=CREATE_TIME,
        counters:wrap=20:label=COUNTERS,
        errorSummaries:wrap=20:label=ERROR_SUMMARIES,
        state:wrap=20:label=STATE
      )
    """)
    parser.display_info.AddTransforms({
        "transformation": _TransformTransformation,
        "dryrun": _TransformDryRun,
    })
