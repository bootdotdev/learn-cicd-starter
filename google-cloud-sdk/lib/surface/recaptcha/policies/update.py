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
"""Command to update a reCAPTCHA key policy."""

from apitools.base.py import encoding
from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.recaptcha import policies_util
from googlecloudsdk.generated_clients.apis.recaptchaenterprise.v1 import recaptchaenterprise_v1_messages as messages


@base.Hidden
@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Update(base.UpdateCommand):
  """Update a reCAPTCHA key's policy.

  ## EXAMPLES

  To update a policy for a reCAPTCHA key:

      $ {command} --key=test-key  --policy=policy.yaml

  See [https://cloud.google.com/sdk/gcloud/reference/recaptcha/keys] for more
  details for recaptcha keys.
  """

  @staticmethod
  def Args(parser):
    policies_util.AddKeyResourceArg(parser, 'to update')
    parser.add_argument(
        '--policy',
        help=(
            'Path to a YAML file or a JSON file containing the policy'
            ' definition.'
        ),
        required=True,
        type=arg_parsers.YAMLFileContents(),
    )

  def Run(self, args):
    client = apis.GetClientInstance('recaptchaenterprise', 'v1')
    key_ref = args.CONCEPTS.key.Parse()
    policy_name = key_ref.RelativeName() + '/policy'

    policy_dict = args.policy if args.policy is not None else {}
    policy_message = encoding.DictToMessage(
        policy_dict, messages.GoogleCloudRecaptchaenterpriseV1Policy
    )

    # Create the UpdatePolicyRequest message
    request = messages.RecaptchaenterpriseProjectsKeysUpdatePolicyRequest(
        name=policy_name,
        googleCloudRecaptchaenterpriseV1Policy=policy_message,
    )
    return client.projects_keys.UpdatePolicy(request)
