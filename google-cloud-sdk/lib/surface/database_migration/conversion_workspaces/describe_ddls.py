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
"""Command to commit conversion workspaces for a database migration."""

import argparse
from typing import Generator

from googlecloudsdk.api_lib.database_migration import resource_args
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.database_migration.conversion_workspaces import command_mixin
from googlecloudsdk.command_lib.database_migration.conversion_workspaces import flags as cw_flags
from googlecloudsdk.generated_clients.apis.datamigration.v1 import datamigration_v1_messages as messages

_DEFAULT_PAGE_SIZE = 100


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class DescribeDDLs(
    command_mixin.ConversionWorkspacesCommandMixin,
    base.ListCommand,
):
  """Describe DDLs in a Database Migration Service conversion workspace."""

  detailed_help = {
      'DESCRIPTION': """
        Describe DDLs in a Database Migration Service conversion workspace.
      """,
      'EXAMPLES': """\
        To describe the DDLs of the draft tree in my-conversion-workspace in a
        project and location `us-central1`, run:

            $ {command} my-conversion-workspace --region=us-central1

        To describe the DDLs of the source tree in a conversion workspace in a
        project and location `us-central1`, run:

            $ {command} my-conversion-workspace --region=us-central1 --tree-type=SOURCE
      """,
  }

  @staticmethod
  def Args(parser: argparse.ArgumentParser) -> None:
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    resource_args.AddConversionWorkspaceResourceArg(parser, 'to describe DDLs')
    cw_flags.AddTreeTypeFlag(parser, required=False)
    cw_flags.AddCommitIdFlag(parser)
    cw_flags.AddUncommittedFlag(parser)
    base.PAGE_SIZE_FLAG.SetDefault(parser, _DEFAULT_PAGE_SIZE)

    parser.display_info.AddFormat("""table(ddl:label=DDLs)""")

  def Run(
      self,
      args: argparse.Namespace,
  ) -> Generator[messages.EntityDdl, None, None]:
    """Describe the DDLs for a Database Migration Service conversion workspace.

    Args:
      args: argparse.Namespace, the arguments that this command was invoked
        with.

    Returns:
      A list of DDLs for the specified conversion workspace and arguments.
    """
    conversion_workspace_ref = args.CONCEPTS.conversion_workspace.Parse()
    return self.client.entities.DescribeDDLs(
        name=conversion_workspace_ref.RelativeName(),
        commit_id=args.commit_id,
        uncommitted=args.uncommitted,
        tree_type=args.tree_type,
        filter_expr=self.ExtractBackendFilter(args),
        page_size=args.GetValue('page_size'),
    )
