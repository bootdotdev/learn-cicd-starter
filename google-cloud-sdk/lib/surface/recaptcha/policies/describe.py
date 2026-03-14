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
"""Command to describe a reCAPTCHA key policy."""

from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.recaptcha import policies_util
from googlecloudsdk.generated_clients.apis.recaptchaenterprise.v1 import recaptchaenterprise_v1_messages as messages


@base.Hidden
@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Describe(base.DescribeCommand):
  """Describe a reCAPTCHA key's policy.

  ## EXAMPLES

  To describe a policy for a reCAPTCHA key:

      $ {command} --key=test-key

  See [https://cloud.google.com/sdk/gcloud/reference/recaptcha/keys] for more
  details for recaptcha keys.
  """

  @staticmethod
  def Args(parser):
    policies_util.AddKeyResourceArg(parser, 'to describe')

  def Run(self, args):
    client = apis.GetClientInstance('recaptchaenterprise', 'v1')
    key_ref = args.CONCEPTS.key.Parse()
    policy_name = key_ref.RelativeName() + '/policy'
    request = messages.RecaptchaenterpriseProjectsKeysGetPolicyRequest(
        name=policy_name
    )
    return client.projects_keys.GetPolicy(request)
