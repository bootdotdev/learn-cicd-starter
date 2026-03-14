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
from typing import Any, Dict, Generator

from googlecloudsdk.api_lib.database_migration import resource_args
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.database_migration.conversion_workspaces import command_mixin
from googlecloudsdk.command_lib.database_migration.conversion_workspaces import flags as cw_flags

_DEFAULT_PAGE_SIZE = 100


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class DescribeIssues(
    command_mixin.ConversionWorkspacesCommandMixin,
    base.ListCommand,
):
  """Describe issues in a Database Migration Service conversion workspace."""

  detailed_help = {
      'DESCRIPTION': """
        Describe database entity issues in a Database Migration Services conversion workspace.
      """,
      'EXAMPLES': """\
          To describe the database entity issues in a conversion workspace
          in a project and location `us-central1`, run:

              $ {command} my-conversion-workspace --region=us-central1
      """,
  }

  @staticmethod
  def Args(parser: argparse.ArgumentParser) -> None:
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    resource_args.AddConversionWorkspaceResourceArg(
        parser, 'to describe issues'
    )
    cw_flags.AddCommitIdFlag(parser)
    cw_flags.AddUncommittedFlag(parser)
    base.PAGE_SIZE_FLAG.SetDefault(parser, _DEFAULT_PAGE_SIZE)

    parser.display_info.AddFormat("""
          table(
            parentEntity:label=PARENT,
            shortName:label=NAME,
            entityType:label=ENTITY_TYPE,
            issueType:label=ISSUE_TYPE,
            issueSeverity:label=ISSUE_SEVERITY,
            issueCode:label=ISSUE_CODE,
            issueMessage:label=ISSUE_MESSAGE
          )
        """)

  def Run(
      self,
      args: argparse.Namespace,
  ) -> Generator[Dict[str, Any], None, None]:
    """Describe the database entity issues for a DMS conversion workspace.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      A list of database entity issues for the specified conversion workspace
      and arguments.
    """
    conversion_workspace_ref = args.CONCEPTS.conversion_workspace.Parse()
    return self.client.entities.DescribeIssues(
        name=conversion_workspace_ref.RelativeName(),
        commit_id=args.commit_id,
        uncommitted=args.uncommitted,
        filter_expr=self.ExtractBackendFilter(args),
        page_size=args.GetValue('page_size'),
    )
