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
"""Command to get IAM policy for a resource."""


from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.backend_buckets import backend_buckets_utils
from googlecloudsdk.command_lib.compute.backend_buckets import flags


@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.DefaultUniverseOnly
class GetIamPolicy(base.ListCommand):
  """Get the IAM policy for a Compute Engine backend bucket."""

  @staticmethod
  def Args(parser):
    flags.GLOBAL_REGIONAL_BACKEND_BUCKET_ARG_IAM.AddArgument(parser)
    base.URI_FLAG.RemoveFromParser(parser)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    backend_bucket_ref = (
        flags.GLOBAL_REGIONAL_BACKEND_BUCKET_ARG_IAM.ResolveAsResource(
            args,
            holder.resources,
            default_scope=compute_scope.ScopeEnum.GLOBAL,
            scope_lister=compute_flags.GetDefaultScopeLister(holder.client),
        )
    )

    return backend_buckets_utils.GetIamPolicy(backend_bucket_ref, client)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class GetIamPolicyAlpha(GetIamPolicy):
  """Get the IAM policy for a Compute Engine backend bucket."""

GetIamPolicy.detailed_help = {
    'brief': 'Get the IAM policy for a Compute Engine backend bucket.',
    'DESCRIPTION': """\

      *{command}* displays the IAM policy associated with a
    Compute Engine backend bucket in a project. If formatted as JSON,
    the output can be edited and used as a policy file for
    set-iam-policy. The output includes an "etag" field
    identifying the version emitted and allowing detection of
    concurrent policy updates; see
    $ {parent} set-iam-policy for additional details.  """,
    'EXAMPLES':
        """\
    To print the IAM policy for a given regional backend bucket, run:

      $ {command} my-backend-bucket --region=REGION

    To print the IAM policy for a given global backend bucket, run either of
    the following:

      $ {command} my-backend-bucket --global

      $ {command} my-backend-bucket
      """,
    'API REFERENCE':
    """\
        This command uses the compute API. The full documentation for this
    API can be found at: https://cloud.google.com/compute/""",
}
