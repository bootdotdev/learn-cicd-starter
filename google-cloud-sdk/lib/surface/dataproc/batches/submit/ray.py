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

"""Submit a Ray batch job."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.dataproc import dataproc as dp
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.dataproc import flags
from googlecloudsdk.command_lib.dataproc.batches import batch_submitter
from googlecloudsdk.command_lib.dataproc.batches import ray_batch_factory


@base.Hidden
class Ray(base.Command):
  """Submit a Ray batch job."""
  detailed_help = {
      'EXAMPLES':
          """\
          To submit a Ray batch job called "my-batch" that runs "my-ray.py", run:

            $ {command} my-ray.py --batch=my-batch --deps-bucket=gs://my-bucket --location=us-central1
          """
  }

  @staticmethod
  def Args(parser):
    ray_batch_factory.AddArguments(parser)
    flags.AddLocationFlag(parser)

  def Run(self, args):
    dataproc = dp.Dataproc(base.ReleaseTrack.BETA)
    ray_batch = ray_batch_factory.RayBatchFactory(
        dataproc).UploadLocalFilesAndGetMessage(args)

    return batch_submitter.Submit(ray_batch, dataproc, args)
