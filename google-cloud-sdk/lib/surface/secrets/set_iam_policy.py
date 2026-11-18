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
"""Set the IAM policy for a secret."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.secrets import api as secrets_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.iam import iam_util
from googlecloudsdk.command_lib.secrets import args as secrets_args


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class SetIamPolicy(base.ListCommand):
  """Set the IAM policy binding for a secret.

  Sets the IAM policy for the given secret as defined in a JSON or YAML file.

  See https://cloud.google.com/iam/docs/managing-policies for details of the
  policy file format and contents.
  """

  detailed_help = {
      'EXAMPLES': """\
          The following command will read an IAM policy defined in a JSON file
    'policy.json' and set it for the secret 'my-secret':

        $ {command} my-secret policy.json
          """,
  }

  @staticmethod
  def Args(parser):
    secrets_args.AddSecret(
        parser,
        purpose='',
        positional=True,
        required=True,
        help_text='Name of the secret for which to set the IAM policy.',
    )
    secrets_args.AddLocation(parser, purpose='to set iam policy', hidden=False)
    iam_util.AddArgForPolicyFile(parser)
    base.URI_FLAG.RemoveFromParser(parser)
    base.FILTER_FLAG.RemoveFromParser(parser)
    base.LIMIT_FLAG.RemoveFromParser(parser)
    base.PAGE_SIZE_FLAG.RemoveFromParser(parser)
    base.SORT_BY_FLAG.RemoveFromParser(parser)

  def Run(self, args):
    api_version = secrets_api.GetApiFromTrack(self.ReleaseTrack())
    secret_ref = args.CONCEPTS.secret.Parse()
    messages = secrets_api.GetMessages(version=api_version)
    policy, update_mask = iam_util.ParseYamlOrJsonPolicyFile(
        args.policy_file, messages.Policy
    )
    result = secrets_api.Secrets(api_version=api_version).SetIamPolicy(
        secret_ref, policy, update_mask, secret_location=args.location
    )
    iam_util.LogSetIamPolicy(secret_ref.Name(), 'secret')
    return result


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class SetIamPolicyBeta(SetIamPolicy):
  """Set the IAM policy for a secret.

  Sets the IAM policy for the given secret.

  Returns an empty policy if the resource does not have a policy
  set.
  """

  detailed_help = {
      'EXAMPLES': """\
          To print the IAM policy for secret named 'my-secret', run:

        $ {command} my-secret [--location=]
          """,
  }
