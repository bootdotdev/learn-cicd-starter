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
"""Command to set IAM policy for a resource."""


from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.backend_buckets import backend_buckets_utils
from googlecloudsdk.command_lib.compute.backend_buckets import flags
from googlecloudsdk.command_lib.iam import iam_util


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class SetIamPolicy(base.Command):
  """Set the IAM policy binding for a Compute Engine backend bucket."""

  @staticmethod
  def Args(parser):
    flags.GLOBAL_REGIONAL_BACKEND_BUCKET_ARG_IAM.AddArgument(
        parser, operation_type='setIamPolicy'
    )
    iam_util.AddArgForPolicyFile(parser)

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

    policy = iam_util.ParsePolicyFile(args.policy_file, client.messages.Policy)
    policy.version = iam_util.MAX_LIBRARY_IAM_SUPPORTED_VERSION

    return backend_buckets_utils.SetIamPolicy(
        backend_bucket_ref, client, policy
    )


SetIamPolicy.detailed_help = {
    'brief': 'Set the IAM policy binding for a Compute Engine backend bucket.',
    'DESCRIPTION': """\

    Sets the IAM policy for the given backend bucket as defined in a
    JSON or YAML file.  """,
    'EXAMPLES': """\
    The following command will read an IAM policy defined in a JSON file
    'policy.json' and set it for the backend bucket `my-backend-bucket`:

      $ {command} my-backend-bucket policy.json --region=REGION

      $ {command} my-backend-bucket policy.json --global

      $ {command} my-backend-bucket policy.json

    See https://cloud.google.com/iam/docs/managing-policies for details of the
    policy file format and contents.
    """,
    'API REFERENCE': """\
    This command uses the compute/alpha API. The full documentation for this
    API can be found at: https://cloud.google.com/compute/""",
}
