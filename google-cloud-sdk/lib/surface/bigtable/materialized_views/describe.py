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
"""Bigtable materialized views describe command."""

import textwrap

from googlecloudsdk.api_lib.bigtable import materialized_views
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import parser_extensions
from googlecloudsdk.command_lib.bigtable import arguments
from googlecloudsdk.generated_clients.apis.bigtableadmin.v2 import bigtableadmin_v2_messages


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.GA, base.ReleaseTrack.BETA, base.ReleaseTrack.ALPHA
)
class DescribeMaterializedView(base.DescribeCommand):
  """Describe an existing Bigtable materialized view."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
          To get back information related to a view's schema (for example, description), run:

            $ {command} my-materialized-view-id --instance=my-instance-id --view=schema

          or (because schema is the default view) simply:

            $ {command} my-materialized-view-id --instance=my-instance-id

          To get back information related to the view's replication state, run:

            $ {command} my-materialized-view-id --instance=my-instance-id --view=replication

          To get back all information for the view, run:

            $ {command} my-materialized-view-id --instance=my-instance-id --view=full
          """),
  }

  @staticmethod
  def Args(parser) -> None:
    """Register flags for this command."""
    arguments.AddMaterializedViewResourceArg(parser, 'to describe')
    arguments.AddViewOverMaterializedView(parser)

  def Run(
      self, args: parser_extensions.Namespace
  ) -> bigtableadmin_v2_messages.MaterializedView:
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    materialized_view_ref = args.CONCEPTS.materialized_view.Parse()
    return materialized_views.Describe(materialized_view_ref, view=args.view)
