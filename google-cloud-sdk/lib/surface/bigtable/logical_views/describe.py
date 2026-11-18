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
"""Bigtable logical views describe command."""

import textwrap

from googlecloudsdk.api_lib.bigtable import logical_views
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.bigtable import arguments


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.GA, base.ReleaseTrack.BETA, base.ReleaseTrack.ALPHA
)
class DescribeLogicalView(base.DescribeCommand):
  """Describe an existing Bigtable logical view."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
          To view a logical view's description, run:

            $ {command} my-logical-view-id --instance=my-instance-id

          """),
  }

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    arguments.AddLogicalViewResourceArg(parser, 'to describe')

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    logical_view_ref = args.CONCEPTS.logical_view.Parse()
    return logical_views.Describe(logical_view_ref)
