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
"""Fetch the IAM policy for a secret."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.secrets import api as secrets_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.secrets import args as secrets_args


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class GetIamPolicy(base.ListCommand):
  """Get the IAM policy for the secret.

  Displays the IAM policy associated with the secret. If formatted as JSON,
  the output can be edited and used as a policy file for set-iam-policy. The
  output includes an "etag" field identifying the version emitted and
  allowing detection of concurrent policy updates.

  Run gcloud secrets set-iam-policy for additional details.
  """

  detailed_help = {
      'EXAMPLES': """\
          To print the IAM policy for secret named 'my-secret', run:

          $ {command} my-secret
          """,
  }

  @staticmethod
  def Args(parser):
    secrets_args.AddSecret(
        parser,
        purpose='',
        positional=True,
        required=True,
        help_text='Name of the secret from which to get IAM policy.',
    )
    secrets_args.AddLocation(parser, purpose='to get iam policy', hidden=False)
    base.URI_FLAG.RemoveFromParser(parser)

  def Run(self, args):
    api_version = secrets_api.GetApiFromTrack(self.ReleaseTrack())
    multi_ref = args.CONCEPTS.secret.Parse()
    return secrets_api.Secrets(api_version=api_version).GetIamPolicy(
        multi_ref, secret_location=args.location
    )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class GetIamPolicyBeta(GetIamPolicy):
  """Get the IAM policy of a secret.

  Gets the IAM policy for the given secret.

  Returns an empty policy if the resource does not have a policy
  set.
  """

  detailed_help = {
      'EXAMPLES': """\
          To print the IAM policy for secret named 'my-secret', run:

          $ {command} my-secret [--location=]
          """,
  }
