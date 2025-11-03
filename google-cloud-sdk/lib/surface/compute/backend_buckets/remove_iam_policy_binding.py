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
"""Command to remove IAM policy for a backend bucket."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.backend_buckets import backend_buckets_utils
from googlecloudsdk.command_lib.compute.backend_buckets import flags
from googlecloudsdk.command_lib.iam import iam_util


@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.DefaultUniverseOnly
class RemoveIamPolicyBinding(base.Command):
  """Remove an IAM policy binding from a Compute Engine backend bucket."""

  @staticmethod
  def Args(parser):
    flags.GLOBAL_REGIONAL_BACKEND_BUCKET_ARG_IAM.AddArgument(parser)
    iam_util.AddArgsForRemoveIamPolicyBinding(parser)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    backend_service_ref = (
        flags.GLOBAL_REGIONAL_BACKEND_BUCKET_ARG_IAM.ResolveAsResource(
            args,
            holder.resources,
            default_scope=compute_scope.ScopeEnum.GLOBAL,
            scope_lister=compute_flags.GetDefaultScopeLister(holder.client),
        )
    )
    policy = backend_buckets_utils.GetIamPolicy(backend_service_ref, client)
    iam_util.RemoveBindingFromIamPolicy(policy, args.member, args.role)
    return backend_buckets_utils.SetIamPolicy(
        backend_service_ref, client, policy
    )


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class RemoveIamPolicyBindingAlpha(RemoveIamPolicyBinding):
  """Remove an IAM policy binding from a Compute Engine backend bucket."""


RemoveIamPolicyBinding.detailed_help = {
    'brief': (
        'Remove an IAM policy binding from a Compute Engine backend bucket.'
    ),
    'DESCRIPTION': """\

Remove an IAM policy binding from a Compute Engine backend bucket.  """,
    'EXAMPLES': """\
  To remove an IAM policy binding for the role of
  'roles/compute.loadBalancerServiceUser' for the user 'test-user@gmail.com'
  with backend bucket 'my-backend-bucket' and region 'REGION', run:

      $ {command} my-backend-bucket --region=REGION \
        --member='user:test-user@gmail.com' \
        --role='roles/compute.loadBalancerServiceUser'

  To remove an IAM policy binding for the role of
  'roles/compute.loadBalancerServiceUser' for the user 'test-user@gmail.com'
  with globalbackend bucket 'my-backend-bucket', run either of the following:

      $ {command} my-backend-bucket --global \
        --member='user:test-user@gmail.com' \
        --role='roles/compute.loadBalancerServiceUser'

      $ {command} my-backend-bucket \
        --member='user:test-user@gmail.com' \
        --role='roles/compute.loadBalancerServiceUser'

  See https://cloud.google.com/iam/docs/managing-policies for details of
  policy role and member types.
""",
    'API REFERENCE': """\
    This command uses the compute API. The full documentation for this
    API can be found at: https://cloud.google.com/compute/""",
}
