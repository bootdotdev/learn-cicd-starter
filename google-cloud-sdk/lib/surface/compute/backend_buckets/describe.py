# -*- coding: utf-8 -*- #
# Copyright 2015 Google LLC. All Rights Reserved.
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
"""Command for describing backend buckets."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.backend_buckets import flags


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Describe(base.DescribeCommand):
  """Describe a backend bucket.

  *{command}* displays all data associated with a backend bucket in a
  project.
  """

  BACKEND_BUCKET_ARG = None
  _support_regional_global_flags = False

  @classmethod
  def Args(cls, parser):
    cls.BACKEND_BUCKET_ARG = (
        flags.GLOBAL_REGIONAL_BACKEND_BUCKET_ARG
        if cls._support_regional_global_flags
        else flags.BackendBucketArgument()
    )
    cls.BACKEND_BUCKET_ARG.AddArgument(parser, operation_type='describe')

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    backend_bucket_ref = self.BACKEND_BUCKET_ARG.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(client),
        default_scope=compute_scope.ScopeEnum.GLOBAL,
    )

    requests = []
    if backend_bucket_ref.Collection() == 'compute.backendBuckets':
      requests = [(
          client.apitools_client.backendBuckets,
          'Get',
          client.messages.ComputeBackendBucketsGetRequest(
              **backend_bucket_ref.AsDict()
          ),
      )]
    elif backend_bucket_ref.Collection() == 'compute.regionBackendBuckets':
      requests = [(
          client.apitools_client.regionBackendBuckets,
          'Get',
          client.messages.ComputeRegionBackendBucketsGetRequest(
              **backend_bucket_ref.AsDict()
          ),
      )]

    return client.MakeRequests(requests)[0]


@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.DefaultUniverseOnly
class DescribeBeta(Describe):
  """Describe a backend bucket.

  *{command}* displays all data associated with a backend bucket in a
  project.

  To describe a global backend bucket, run either of the following:

      $ {command} my-backend-bucket
        --gcs-bucket-name gcs-bucket-1
        --global

      $ {command} my-backend-bucket
        --gcs-bucket-name gcs-bucket-1

  To describe a regional backend bucket, run the following:

      $ {command} my-backend-bucket
        --gcs-bucket-name gcs-bucket-1
        --region=us-central1
  """

  _support_regional_global_flags = True


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class DescribeAlpha(DescribeBeta):
  """Describe a backend bucket.

  *{command}* displays all data associated with a backend bucket in a
  project.

  To describe a global backend bucket, run either of the following:

      $ {command} my-backend-bucket
        --gcs-bucket-name gcs-bucket-1
        --global

      $ {command} my-backend-bucket
        --gcs-bucket-name gcs-bucket-1

  To describe a regional backend bucket, run the following:

      $ {command} my-backend-bucket
        --gcs-bucket-name gcs-bucket-1
        --region=us-central1
  """

  _support_regional_global_flags = True
