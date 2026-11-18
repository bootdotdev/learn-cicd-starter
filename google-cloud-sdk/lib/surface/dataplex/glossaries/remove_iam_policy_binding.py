# -*- coding: utf-8 -*- #
# Copyright 2024 Google Inc. All Rights Reserved.
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
"""`gcloud dataplex glossaries remove-iam-policy-binding` command."""
from googlecloudsdk.api_lib.dataplex import glossary
from googlecloudsdk.api_lib.util import exceptions as gcloud_exception
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.dataplex import resource_args
from googlecloudsdk.command_lib.iam import iam_util


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class RemoveIamPolicyBinding(base.Command):
  """Removes IAM policy binding from a Dataplex Glossary."""

  detailed_help = {
      'EXAMPLES': """\
          To remove an IAM policy binding for the role `roles/dataplex.viewer`
          for the user `test-user@gmail.com` from a glossary `test-glossary` within projet
          `test-project` in location `us-central1`, run:
            $ {command} test-glossary --project=test-project --location=us-central1 --role=roles/dataplex.viewer --member=user:test-user@gmail.com
          See https://cloud.google.com/dataplex/docs/iam-roles for details of
          policy role and member types.
          """,
  }

  @staticmethod
  def Args(parser):
    resource_args.AddGlossaryResourceArg(
        parser, 'to remove IAM policy binding from '
    )
    iam_util.AddArgsForRemoveIamPolicyBinding(parser)

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException(
      'Status code: {status_code}. {status_message}.'
  )
  def Run(self, args):
    glossary_ref = args.CONCEPTS.glossary.Parse()
    result = glossary.GlossaryRemoveIamPolicyBinding(
        glossary_ref, args.member, args.role
    )
    return result
