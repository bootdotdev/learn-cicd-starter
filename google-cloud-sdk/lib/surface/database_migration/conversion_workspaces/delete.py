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
"""Command to delete a database migration conversion workspace."""

import argparse
from typing import Optional

from googlecloudsdk.api_lib.database_migration import resource_args
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.database_migration.conversion_workspaces import command_mixin
from googlecloudsdk.command_lib.database_migration.conversion_workspaces import flags as pc_flags
from googlecloudsdk.core.console import console_io
from googlecloudsdk.generated_clients.apis.datamigration.v1 import datamigration_v1_messages as messages


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Delete(command_mixin.ConversionWorkspacesCommandMixin, base.Command):
  """Delete a Database Migration conversion workspace."""

  detailed_help = {
      'DESCRIPTION': """
        Delete a Database Migration conversion workspace.
      """,
      'EXAMPLES': """\
        To delete a conversion workspace called 'my-conversion-workspace', run:

            $ {command} my-conversion-workspace --region=us-central1
      """,
  }

  @staticmethod
  def CommonArgs(parser):
    """Common arguments for all release tracks.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    resource_args.AddConversionWorkspaceResourceArg(parser, 'to delete')
    pc_flags.AddNoAsyncFlag(parser)

  @staticmethod
  def Args(parser: argparse.ArgumentParser) -> None:
    """Args is called by calliope to gather arguments for this command."""
    Delete.CommonArgs(parser)

  def Run(self, args: argparse.Namespace) -> Optional[messages.Operation]:
    """Delete a Database Migration conversion workspace.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      An Optional[dict] object representing the operations resource describing
      the delete
      operation if the delete was successful.
    """
    conversion_workspace_ref = args.CONCEPTS.conversion_workspace.Parse()

    if not console_io.PromptContinue(
        message=(
            'You are about to delete conversion workspace'
            f' {conversion_workspace_ref.RelativeName()}.\n'
            'Are you sure?'
        )
    ):
      return

    result_operation = self.client.crud.Delete(
        name=conversion_workspace_ref.RelativeName(),
    )

    return self.HandleOperationResult(
        conversion_workspace_ref=conversion_workspace_ref,
        result_operation=result_operation,
        operation_name='Deleted',
        sync=args.IsKnownAndSpecified('no_async'),
        has_resource=False,
    )
