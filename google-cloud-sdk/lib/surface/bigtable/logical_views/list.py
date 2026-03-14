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
"""Bigtable logical views list command."""

import textwrap

from googlecloudsdk.api_lib.bigtable import logical_views
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.bigtable import arguments


@base.DefaultUniverseOnly
@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.GA, base.ReleaseTrack.BETA, base.ReleaseTrack.ALPHA
)
class ListLogicalViews(base.ListCommand):
  """List existing Bigtable logical views."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
          To list all logical views for an instance, run:

            $ {command} --instance=my-instance-id

          """),
  }

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    arguments.AddInstanceResourceArg(parser, 'to list logical views for')

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    instance_ref = args.CONCEPTS.instance.Parse()
    return logical_views.List(instance_ref)
