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
"""Bigtable materialized views list command."""

import textwrap
from typing import Generator

from googlecloudsdk.api_lib.bigtable import materialized_views
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import parser_arguments
from googlecloudsdk.calliope import parser_extensions
from googlecloudsdk.command_lib.bigtable import arguments
from googlecloudsdk.generated_clients.apis.bigtableadmin.v2 import bigtableadmin_v2_messages


@base.DefaultUniverseOnly
@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.GA, base.ReleaseTrack.BETA, base.ReleaseTrack.ALPHA
)
class ListMaterializedViews(base.ListCommand):
  """List existing Bigtable materialized views."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
          To list all materialized views for an instance, run:

            $ {command} --instance=my-instance-id

          You may also specify what information to return by supplying the `--view` flag, such as:

            $ {command} --instance=my-instance-id --view=schema

          Currently, only the schema view is supported for this command. This is the default view, and it returns information about the schemas of your materialized views.
          """),
  }

  @staticmethod
  def Args(parser: parser_arguments.ArgumentInterceptor) -> None:
    """Register flags for this command."""
    arguments.AddInstanceResourceArg(parser, 'to list materialized views for')
    arguments.AddViewOverMaterializedView(parser)

  def Run(
      self, args: parser_extensions.Namespace
  ) -> Generator[bigtableadmin_v2_messages.MaterializedView, None, None]:
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    instance_ref = args.CONCEPTS.instance.Parse()
    return materialized_views.List(instance_ref, view=args.view)
