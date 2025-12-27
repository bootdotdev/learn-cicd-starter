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

"""Command to Get IAM policy for an investigation."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.gemini_cloud_assist import args as geminicloudassist_args
from googlecloudsdk.api_lib.gemini_cloud_assist import util as geminicloudassist_util
from googlecloudsdk.calliope import base


@base.UniverseCompatible
class GetIamPolicy(base.Command):
  """Get IAM policy for an investigation."""

  detailed_help = {
      'EXAMPLES': """\
          To get the IAM policy a the investigation 'project/my-project/locations/my-location/investigations/my-investigation', run:

            $ {command} project/my-project/locations/my-location/investigations/my-investigation
          """,
  }

  @staticmethod
  def Args(parser):
    """Registers flags for this command.

    Args:
      parser: The argparse parser.
    """
    geminicloudassist_args.AddInvestigationResourceArg(
        parser, 'to get IAM policy for'
    )

  def Run(self, args):
    """ Get IAM policy for an investigation.

    Args:
      args: An argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      The IAM policy for the given investigation.
    """
    return geminicloudassist_util.GetInvestigationIamPolicy(args.investigation)
