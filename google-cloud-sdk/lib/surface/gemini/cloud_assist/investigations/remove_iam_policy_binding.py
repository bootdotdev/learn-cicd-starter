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

"""Command to remove an IAM policy binding from an investigation."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.gemini_cloud_assist import args as geminicloudassist_args
from googlecloudsdk.api_lib.gemini_cloud_assist import util as geminicloudassist_util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.iam import iam_util


@base.UniverseCompatible
class RemoveIamPolicyBinding(base.Command):
  """Removes an IAM policy binding from an investigation."""

  detailed_help = {
      'EXAMPLES': """\
          To remove an IAM policy binding for the role of 'roles/geminicloudassist.investigationUser'
          for the user 'test-user@gmail.com' from the investigation
          'project/my-project/locations/my-location/investigations/my-investigation', run:

            $ {command} project/my-project/locations/my-location/investigations/my-investigation --member='user:test-user@gmail.com' --role='roles/geminicloudassist.investigations.user'

          See https://cloud.google.com/iam/docs/managing-policies for details of
          policy role and member types.
          """,
  }

  @staticmethod
  def Args(parser):
    """Registers flags for this command.

    Args:
      parser: The argparse parser.
    """
    geminicloudassist_args.AddInvestigationResourceArg(
        parser, 'to remove IAM policy binding from'
    )
    iam_util.AddArgsForAddIamPolicyBinding(parser)

  def Run(self, args):
    """Removes an IAM policy binding from an investigation.

    Args:
      args: An argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      The updated IAM policy.
    """
    return geminicloudassist_util.RemoveInvestigationIamPolicyBinding(
        args.investigation, args.member, args.role
    )
