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

"""Command to add an IAM policy binding for an investigation."""

import textwrap

from googlecloudsdk.api_lib.gemini_cloud_assist import args as geminicloudassist_args
from googlecloudsdk.api_lib.gemini_cloud_assist import util as geminicloudassist_util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.iam import iam_util


@base.UniverseCompatible
class AddIamPolicyBinding(base.Command):
  """Adds an IAM policy binding for an investigation."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
          To add an IAM policy binding for the role of 'roles/geminicloudassist.investigationViewer'
          for the user 'test-user@gmail.com' on the investigation
          'project/my-project/locations/my-location/investigations/my-investigation', run:

            $ {command} project/my-project/locations/my-location/investigations/my-investigation --member='user:test-user@gmail.com' --role='roles/geminicloudassist.investigationViewer'

          See https://cloud.google.com/iam/docs/managing-policies for details of
          policy role and member types.
          """),
  }

  @staticmethod
  def Args(parser):
    """Registers flags for this command.

    Args:
      parser: The argparse parser.
    """
    geminicloudassist_args.AddInvestigationResourceArg(
        parser, 'to add IAM policy binding for'
    )
    iam_util.AddArgsForAddIamPolicyBinding(parser)

  def Run(self, args):
    """Adds an IAM policy binding for an investigation.

    Args:
      args: An argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      The updated IAM policy.
    """
    return geminicloudassist_util.AddInvestigationIamPolicyBinding(
        args.investigation, args.member, args.role
    )
