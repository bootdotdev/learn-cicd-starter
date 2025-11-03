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
"""Command to update conversion workspaces for a database migration."""

import argparse
from typing import Optional

from googlecloudsdk.api_lib.database_migration import resource_args
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.database_migration.conversion_workspaces import command_mixin
from googlecloudsdk.command_lib.database_migration.conversion_workspaces import flags as cw_flags
from googlecloudsdk.generated_clients.apis.datamigration.v1 import datamigration_v1_messages as messages


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Update(command_mixin.ConversionWorkspacesCommandMixin, base.Command):
  """Update a Database Migration Service conversion workspace."""

  detailed_help = {
      'DESCRIPTION': """
        Update a Database Migration Service conversion workspace.
      """,
      'EXAMPLES': """\
        To update a conversion workspace:

            $ {command} my-conversion-workspace --region=us-central1
            --display-name=new-display-name
      """,
  }

  @staticmethod
  def Args(parser: argparse.ArgumentParser) -> None:
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    resource_args.AddConversionWorkspaceResourceArg(parser, 'to update')
    cw_flags.AddNoAsyncFlag(parser)
    cw_flags.AddDisplayNameFlag(parser)
    cw_flags.AddGlobalFilterFlag(parser)

  def Run(self, args: argparse.Namespace) -> Optional[messages.Operation]:
    """Update a Database Migration Service conversion workspace.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      A dict object representing the operations resource describing the update
      operation if the update was successful.
    """
    conversion_workspace_ref = args.CONCEPTS.conversion_workspace.Parse()
    result_operation = self.client.crud.Update(
        name=conversion_workspace_ref.RelativeName(),
        display_name=args.display_name,
        global_filter=args.global_filter,
    )
    return self.HandleOperationResult(
        conversion_workspace_ref=conversion_workspace_ref,
        result_operation=result_operation,
        operation_name='Updated',
        sync=args.IsKnownAndSpecified('no_async'),
    )
